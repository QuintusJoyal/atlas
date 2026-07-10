import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { Agent } from '@cursor/sdk';

import { ccFetch, redactSecrets } from './cc-client.js';

import { IngestClient, ingestClientFromEnv } from './ingest-client.js';
import {
  TIER_MODELS,
  isModelUnavailableError,
  modelFallbackChain,
  resolveModel,
} from './models.js';
import { runPipelineJob, type PipelineJobPayload } from './pipeline-core.js';
import { resolveCwdForRun } from './run-workspace.js';
import { resolveCwdForRun } from './run-workspace.js';



const RUNNER_ID = `runner_${process.pid}`;

const POLL_MS = 2000;

const HEARTBEAT_MS = 15000;



type RunnerJob = {

  id: string;

  type: 'ticket.chat' | 'ticket.subtasks' | 'role.chat' | 'pipeline.run';

  payload: Record<string, unknown>;

  status: string;

};

function pipelinePayload(job: RunnerJob): PipelineJobPayload {
  const runId = typeof job.payload.runId === 'string' ? job.payload.runId : '';
  const workflow = typeof job.payload.workflow === 'string' ? job.payload.workflow : 'feature';
  const task = typeof job.payload.task === 'string' ? job.payload.task : undefined;
  const workspace = typeof job.payload.workspace === 'string' ? job.payload.workspace : undefined;
  const pathMap = Array.isArray(job.payload.pathMap)
    ? (job.payload.pathMap as { hostPrefix: string; containerPrefix: string }[])
    : undefined;
  if (!runId) throw new Error('pipeline.run missing runId');
  return { runId, workflow, task, workspace, pathMap };
}



function atlasRoot(): string {
  return process.env.ATLAS_WORKSPACE || process.env.ATLAS_ROOT || process.cwd();
}



function readAgentModel(role: string, cwd: string): string | undefined {
  const filePath = join(cwd, 'agents', `${role}.md`);
  if (!existsSync(filePath)) return undefined;
  try {
    const content = readFileSync(filePath, 'utf8');
    const match = content.match(/^model:\s*(.+)$/m);
    return match?.[1]?.trim();
  } catch {
    return undefined;
  }
}



function jobRunId(job: RunnerJob): string | undefined {

  return typeof job.payload.runId === 'string' ? job.payload.runId : undefined;

}



async function heartbeat(): Promise<void> {
  try {
    await ccFetch('/api/runner/health', {
      method: 'POST',
      body: JSON.stringify({ runnerId: RUNNER_ID, version: '0.1.0', modes: ['local'] }),
    });
  } catch (err) {
    console.warn('[runner] heartbeat failed:', err instanceof Error ? err.message : err);
  }
}



async function pollJobs(): Promise<RunnerJob[]> {

  const res = await ccFetch('/api/runner/jobs?limit=1');

  if (!res.ok) throw new Error(`jobs poll HTTP ${res.status}`);

  return (await res.json()) as RunnerJob[];

}



async function ackJob(id: string): Promise<RunnerJob> {

  const res = await ccFetch(`/api/runner/jobs/${id}/ack`, { method: 'POST', body: '{}' });

  if (!res.ok) throw new Error(`ack HTTP ${res.status}`);

  return (await res.json()) as RunnerJob;

}



async function completeJob(id: string, ok: boolean, error?: string): Promise<void> {

  await ccFetch(`/api/runner/jobs/${id}/complete`, {

    method: 'POST',

    body: JSON.stringify({ ok, error }),

  });

}



function parseSubtasks(text: string): { title: string; done: false }[] {

  const fenced = /```(?:json)?\s*([\s\S]*?)```/.exec(text);

  const raw = fenced ? fenced[1] : text;

  try {

    const parsed = JSON.parse(raw.trim()) as unknown;

    if (Array.isArray(parsed)) {

      return parsed

        .map((item) => {

          if (typeof item === 'string') return { title: item, done: false as const };

          if (item && typeof item === 'object' && 'title' in item) {

            const title = (item as { title: unknown }).title;

            return typeof title === 'string' ? { title, done: false as const } : null;

          }

          return null;

        })

        .filter((x): x is { title: string; done: false } => Boolean(x?.title));

    }

  } catch {

    /* fall through to line parse */

  }

  return raw

    .split('\n')

    .map((l) => l.replace(/^[-*\d.)\s]+/, '').trim())

    .filter(Boolean)

    .slice(0, 12)

    .map((title) => ({ title, done: false as const }));

}



async function createAgentWithFallback(
  apiKey: string,
  cwd: string,
  preferredModel: string,
): Promise<Awaited<ReturnType<typeof Agent.create>>> {
  const chain = modelFallbackChain(preferredModel);
  let lastErr: unknown;
  for (let i = 0; i < chain.length; i++) {
    const modelId = resolveModel(chain[i]);
    try {
      return await Agent.create({
        apiKey,
        model: { id: modelId },
        local: { cwd },
      });
    } catch (err) {
      lastErr = err;
      const canRetry = isModelUnavailableError(err) && i < chain.length - 1;
      if (canRetry) {
        console.warn(`[runner] model ${modelId} unavailable, retrying at ${chain[i + 1]}`);
        continue;
      }
      throw err;
    }
  }
  throw lastErr instanceof Error ? lastErr : new Error(String(lastErr));
}



async function runAgentPrompt(
  role: string,
  prompt: string,
  ingest: IngestClient | null,
  agentId?: string,
  runId?: string,
  modelId?: string,
  cwdOverride?: string,
): Promise<{ text: string; agentId: string }> {
  const apiKey = process.env.CURSOR_API_KEY;
  if (!apiKey) throw new Error('CURSOR_API_KEY not set on host runner');

  const cwd = cwdOverride ?? atlasRoot();

  const preferred =
    resolveModel(modelId ?? readAgentModel(role, cwd) ?? TIER_MODELS.standard);

  const agent = agentId

    ? await Agent.resume({ apiKey, agentId, local: { cwd } })

    : await createAgentWithFallback(apiKey, cwd, preferred);



  try {

    const run = await agent.send(`Act as ${role}. ${prompt}`);

    const streamIngest = ingest?.streamMapper(role, runId);

    let text = '';

    for await (const event of run.stream()) {

      if (streamIngest) await streamIngest.onEvent(event);

      if (event.type !== 'assistant') continue;

      for (const block of event.message.content) {

        if (block.type === 'text') text += block.text;

      }

    }

    if (streamIngest) await streamIngest.flush();

    const result = await run.wait();

    if (result.status === 'error') {

      throw new Error(`Agent run failed: ${result.id}`);

    }

    return { text: result.result ?? text, agentId: agent.agentId };

  } finally {

    await agent.dispose?.();

  }

}



async function handleTicketChat(job: RunnerJob, ingest: IngestClient | null): Promise<void> {

  const ticketId = String(job.payload.ticketId ?? '');

  const role = String(job.payload.role ?? 'atlas-dev');

  const operatorMessage = String(job.payload.operatorMessage ?? '');

  const existingAgentId = typeof job.payload.agentId === 'string' ? job.payload.agentId : undefined;

  const runId = jobRunId(job);
  const cwd = await resolveCwdForRun(runId, job.payload);

  await ingest?.phaseStart(role, 'ticket-chat');



  const ticketRes = await ccFetch(`/api/tickets/${ticketId}`);

  if (!ticketRes.ok) throw new Error(`ticket ${ticketId} not found`);

  const ticket = (await ticketRes.json()) as { title: string; description?: string; runId?: string };

  const chatRes = await ccFetch(`/api/tickets/${ticketId}/chat`);

  const chat = chatRes.ok ? ((await chatRes.json()) as { role: string; body: string }[]) : [];



  const transcript = chat

    .slice(-12)

    .map((m) => `${m.role}: ${m.body}`)

    .join('\n');



  const prompt = [

    `Ticket ${ticketId}: ${ticket.title}`,

    ticket.description ? `Description: ${ticket.description}` : '',

    transcript ? `Transcript:\n${transcript}` : '',

    `Operator: ${operatorMessage}`,

    'Reply as the assigned Atlas role. Be concise and actionable.',

  ]

    .filter(Boolean)

    .join('\n\n');



  const { text, agentId } = await runAgentPrompt(
    role,
    prompt,
    ingest,
    existingAgentId,
    runId ?? ticket.runId,
    undefined,
    cwd,
  );



  const res = await ccFetch(`/api/tickets/${ticketId}/chat/agent`, {

    method: 'POST',

    body: JSON.stringify({ body: redactSecrets(text), author: role, agentId }),

  });

  if (!res.ok) throw new Error(`post agent chat HTTP ${res.status}`);



  await ingest?.ticket(role, `${ticketId}: agent reply posted`, { ticketId, jobId: job.id });

}



async function handleRoleChat(job: RunnerJob, ingest: IngestClient | null): Promise<void> {

  const sessionId = String(job.payload.sessionId ?? '');

  const roleId = String(job.payload.roleId ?? 'atlas-dev');

  const operatorMessage = String(job.payload.operatorMessage ?? '');

  const history = Array.isArray(job.payload.history)

    ? (job.payload.history as { role: string; body: string; author?: string }[])

    : [];



  const roleRes = await ccFetch(`/api/roles/${roleId}`);

  if (!roleRes.ok) throw new Error(`role ${roleId} not found`);

  const role = (await roleRes.json()) as { content: string };



  const transcript = history

    .slice(-12)

    .map((m) => `${m.role}: ${m.body}`)

    .join('\n');



  const prompt = [

    `You are ${roleId}. Follow your agent definition below. No run/ticket context.`,

    role.content,

    transcript ? `Conversation:\n${transcript}` : '',

    `Operator: ${operatorMessage}`,

    'Reply in character.',

  ]

    .filter(Boolean)

    .join('\n\n');



  const { text } = await runAgentPrompt(roleId, prompt, ingest, undefined, undefined);



  const res = await ccFetch(`/api/roles/${roleId}/chat/agent`, {

    method: 'POST',

    body: JSON.stringify({ sessionId, body: redactSecrets(text), author: roleId }),

  });

  if (!res.ok) throw new Error(`post role chat HTTP ${res.status}`);

}



async function handleTicketSubtasks(job: RunnerJob, ingest: IngestClient | null): Promise<void> {

  const ticketId = String(job.payload.ticketId ?? '');

  const role = String(job.payload.role ?? 'atlas-pm');

  const title = String(job.payload.title ?? '');

  const description = String(job.payload.description ?? '');

  const runId = jobRunId(job);
  const cwd = await resolveCwdForRun(runId, job.payload);

  await ingest?.phaseStart(role, 'ticket-subtasks');



  const prompt = [

    `Break down this ticket into 3-8 concrete subtasks.`,

    `Return JSON array: [{ "title": "..." }]`,

    `Ticket: ${title}`,

    description ? `Description: ${description}` : '',

  ]

    .filter(Boolean)

    .join('\n');



  const { text } = await runAgentPrompt(role, prompt, ingest, undefined, runId, undefined, cwd);

  const subs = parseSubtasks(text);

  if (subs.length === 0) throw new Error('Could not parse subtasks from agent output');



  const res = await ccFetch(`/api/tickets/${ticketId}`, {

    method: 'PATCH',

    body: JSON.stringify({ subtasks: subs }),

  });

  if (!res.ok) throw new Error(`patch ticket HTTP ${res.status}`);



  await ingest?.ticket(role, `${ticketId}: generated ${subs.length} subtasks`, {

    ticketId,

    jobId: job.id,

    count: subs.length,

  });

}



async function handlePipelineRun(job: RunnerJob, ingest: IngestClient | null): Promise<void> {
  await runPipelineJob(pipelinePayload(job), ingest);
}



async function executeJob(job: RunnerJob, ingest: IngestClient | null): Promise<void> {

  await ingest?.system(`runner: claimed ${job.type} (${job.id})`, {

    signal: 'job.start',

    jobId: job.id,

    jobType: job.type,

    runnerId: RUNNER_ID,

  });

  switch (job.type) {

    case 'ticket.chat':

      await handleTicketChat(job, ingest);

      break;

    case 'role.chat':

      await handleRoleChat(job, ingest);

      break;

    case 'ticket.subtasks':

      await handleTicketSubtasks(job, ingest);

      break;

    case 'pipeline.run':

      await handlePipelineRun(job, ingest);

      break;

    default:

      throw new Error(`unknown job type: ${job.type}`);

  }

}



async function processOne(job: RunnerJob, ingest: IngestClient | null): Promise<void> {

  const claimed = await ackJob(job.id);

  try {

    await executeJob(claimed, ingest);

    await completeJob(job.id, true);

    await ingest?.system(`runner: completed ${job.type} (${job.id})`, {

      signal: 'job.complete',

      jobId: job.id,

    });

  } catch (err) {

    const msg = err instanceof Error ? err.message : String(err);

    console.error(`[runner] job ${job.id} failed:`, msg);

    await ingest?.system(`runner: failed ${job.type}: ${msg}`, {

      signal: 'job.failed',

      jobId: job.id,

    });

    await completeJob(job.id, false, msg);

  }

}



async function main(): Promise<void> {

  if (!process.env.ATLAS_CC_URL || !process.env.ATLAS_CC_TOKEN) {

    console.error('Set ATLAS_CC_URL and ATLAS_CC_TOKEN for the runner.');

    process.exit(1);

  }

  if (!process.env.CURSOR_API_KEY) {

    console.warn('[runner] CURSOR_API_KEY not set — polling only; jobs will fail until key is set.');

  }



  const ingest = ingestClientFromEnv();

  console.log(`[runner] starting ${RUNNER_ID} → ${process.env.ATLAS_CC_URL}`);

  await heartbeat();
  setInterval(() => void heartbeat(), HEARTBEAT_MS);



  while (true) {

    try {

      const jobs = await pollJobs();

      for (const job of jobs) {

        await processOne(job, ingest);

      }

    } catch (err) {

      console.warn('[runner] poll error:', err instanceof Error ? err.message : err);

    }

    await new Promise((r) => setTimeout(r, POLL_MS));

  }

}



await main();

