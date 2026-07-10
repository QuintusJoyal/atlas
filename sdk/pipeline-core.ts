import { Agent, CursorAgentError } from "@cursor/sdk";
import { ccFetch } from "./cc-client.js";
import type { IngestClient } from "./ingest-client.js";
import { resolveCwdForRun } from "./run-workspace.js";
import {
  MODEL_CASCADE,
  type CascadeModel,
  isModelUnavailableError,
  modelFallbackChain,
  resolveModel,
  roleTierToModel,
} from "./models.js";

const GATE_BEFORE_ROLE: Record<string, "requirements" | "design"> = {
  "atlas-architect": "requirements",
  "atlas-dev": "design",
};

const GATE_AFTER_ROLE: Record<string, "requirements" | "design" | "final"> = {
  "atlas-ba": "requirements",
  "atlas-pm": "requirements",
  "atlas-architect": "design",
  "atlas-security": "final",
};

interface TeamRole {
  id: string;
  tier?: string;
  status?: string;
  task?: string;
  model?: string;
  downgraded?: boolean;
}

interface TeamPayload {
  workflow?: string;
  budgetTier?: string;
  orchestrator?: string;
  rationale?: string;
  roles: TeamRole[];
  completed?: number;
  total?: number;
}

export interface PipelineJobPayload {
  runId: string;
  workflow: string;
  task?: string;
  workspace?: string;
  pathMap?: { hostPrefix: string; containerPrefix: string }[];
}

function isDowngradeTrigger(err: unknown): boolean {
  return isModelUnavailableError(err);
}

type PhaseOutcome = {
  text: string;
  usedTier: CascadeModel;
  downgraded: boolean;
};

async function createAgentWithFallback(
  apiKey: string,
  tier: string,
  cwd: string,
): Promise<Awaited<ReturnType<typeof Agent.create>>> {
  const chain = modelFallbackChain(tier);
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
      if (isModelUnavailableError(err) && i < chain.length - 1) continue;
      throw err;
    }
  }
  throw lastErr instanceof Error ? lastErr : new Error(String(lastErr));
}

async function executeOnce(
  roleId: string,
  task: string,
  prior: string,
  apiKey: string,
  tier: CascadeModel,
  cwd: string,
  ingest: IngestClient | null,
  runId: string,
): Promise<string> {
  await using agent = await createAgentWithFallback(apiKey, tier, cwd);
  const run = await agent.send(roleBrief(roleId, task, prior));
  const streamIngest = ingest?.streamMapper(roleId, runId);
  let text = "";
  for await (const event of run.stream()) {
    if (streamIngest) await streamIngest.onEvent(event);
    if (event.type !== "assistant") continue;
    for (const block of event.message.content) {
      if (block.type === "text") text += block.text;
    }
  }
  if (streamIngest) await streamIngest.flush();
  const result = await run.wait();
  if (result.status === "error") {
    await ingest?.post({
      kind: "agent",
      actor: roleId,
      runId,
      message: `${roleId}: run errored (${result.id})`,
      meta: { signal: "phase.error", sdkRunId: result.id },
    });
  }
  return result.result ?? text;
}

function roleBrief(roleId: string, task: string, prior: string): string {
  switch (roleId) {
    case "atlas-pm":
    case "atlas-ba":
      return `Act as ${roleId}. Produce user stories with testable acceptance criteria and list open questions. Task: ${task}`;
    case "atlas-architect":
      return `Act as atlas-architect. Propose a simple, scalable design with an ADR and noted trade-offs. Requirements:\n${prior}\nTask: ${task}`;
    case "atlas-dev":
      return `Act as atlas-dev. Implement against this design, following clean-code and the team charter.\n${prior}\nTask: ${task}`;
    case "atlas-qa":
      return `Act as atlas-qa. Write tests and a short test plan for the implemented change.\n${prior}`;
    case "atlas-reviewer":
      return `Act as atlas-reviewer. Review for correctness and charter conformance, including the human-authored voice.\n${prior}`;
    case "atlas-security":
      return `Act as atlas-security. Audit the change and give a pass or block recommendation with fixes.\n${prior}`;
    case "atlas-devops":
      return `Act as atlas-devops. Propose CI/CD and deployment changes for this task.\n${prior}\nTask: ${task}`;
    case "atlas-cloud":
      return `Act as atlas-cloud. Propose cloud architecture and cost-aware infrastructure for this task.\n${prior}\nTask: ${task}`;
    default:
      return `Act as ${roleId}. Complete your phase of the Atlas pipeline.\n${prior}\nTask: ${task}`;
  }
}

async function runRolePhase(
  role: TeamRole,
  task: string,
  prior: string,
  apiKey: string,
  cwd: string,
  ingest: IngestClient | null,
  runId: string,
): Promise<PhaseOutcome | null> {
  const startTier = resolveModel(roleTierToModel(role.tier)) as CascadeModel;
  const start = MODEL_CASCADE.indexOf(startTier);
  for (let i = Math.max(0, start); i < MODEL_CASCADE.length; i++) {
    const tier = MODEL_CASCADE[i];
    try {
      const text = await executeOnce(role.id, task, prior, apiKey, tier, cwd, ingest, runId);
      const downgraded = i > start;
      if (downgraded) {
        await ingest?.downgrade(role.id, startTier, tier);
      }
      return { text, usedTier: tier, downgraded };
    } catch (err) {
      const canRetry = isDowngradeTrigger(err) && i < MODEL_CASCADE.length - 1;
      if (canRetry) continue;
      if (err instanceof CursorAgentError) return null;
      throw err;
    }
  }
  return null;
}

async function fetchTeam(runId: string): Promise<TeamPayload> {
  const res = await ccFetch(`/api/runs/${runId}/team`);
  if (!res.ok) throw new Error(`run ${runId} team not found`);
  return (await res.json()) as TeamPayload;
}

async function putTeam(runId: string, team: TeamPayload): Promise<void> {
  const res = await ccFetch(`/api/runs/${runId}/team`, {
    method: "PUT",
    body: JSON.stringify(team),
  });
  if (!res.ok) throw new Error(`PUT team HTTP ${res.status}`);
}

async function isGateApproved(runId: string, gate: string): Promise<boolean> {
  const res = await ccFetch(`/api/runs/${runId}/state`);
  if (!res.ok) return false;
  const state = (await res.json()) as { gates?: { name: string; status: string }[] };
  return state.gates?.some((g) => g.name === gate && g.status === "approved") ?? false;
}

/** Execute pipeline.run job: workflow roles from team.json, stop at approval gates. */
export async function runPipelineJob(
  payload: PipelineJobPayload,
  ingest: IngestClient | null,
): Promise<void> {
  const { runId, workflow } = payload;
  const task = payload.task?.trim() || `${workflow} pipeline run`;
  const apiKey = process.env.CURSOR_API_KEY;
  if (!apiKey) throw new Error("CURSOR_API_KEY not set on host runner");

  const cwd = await resolveCwdForRun(runId, payload as Record<string, unknown>);
  const team = await fetchTeam(runId);

  await ingest?.system(`pipeline.run started for ${runId}`, {
    signal: "pipeline.start",
    runId,
    workflow,
  });

  let prior = "";
  for (const role of team.roles) {
    if (role.status === "done" || role.status === "na") continue;

    const needed = GATE_BEFORE_ROLE[role.id];
    if (needed && !(await isGateApproved(runId, needed))) {
      await ingest?.gatePause(needed);
      await ingest?.system(`pipeline paused: ${needed} gate not approved`, { runId, role: role.id });
      return;
    }

    const model = roleTierToModel(role.tier);
    role.status = "active";
    role.task = task;
    role.model = model;
    team.completed = team.roles.filter((r) => r.status === "done").length;
    await putTeam(runId, team);
    await ingest?.phaseStart(role.id, workflow, { runId });

    const outcome = await runRolePhase(role, task, prior, apiKey, cwd, ingest, runId);
    if (outcome === null) {
      role.status = "failed";
      await putTeam(runId, team);
      throw new Error(`${role.id}: all tiers exhausted`);
    }

    role.status = "done";
    role.model = outcome.usedTier;
    role.downgraded = outcome.downgraded;
    team.completed = team.roles.filter((r) => r.status === "done").length;
    await putTeam(runId, team);
    await ingest?.phaseComplete(role.id, outcome.usedTier, {
      downgraded: outcome.downgraded,
      runId,
    });

    prior = `Output of ${role.id}:\n${outcome.text}`;

    const afterGate = GATE_AFTER_ROLE[role.id];
    if (afterGate) {
      await ingest?.gatePause(afterGate);
      await ingest?.system(`pipeline stopped at ${afterGate} gate for approval`, {
        runId,
        gate: afterGate,
      });
      return;
    }
  }

  await ingest?.system(`pipeline.run complete for ${runId}`, { signal: "pipeline.complete", runId });
}
