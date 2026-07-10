import { mkdirSync, appendFileSync, readFileSync, existsSync } from "node:fs";

import { join } from "node:path";

import { Agent, CursorAgentError } from "@cursor/sdk";

import { ingestClientFromEnv, type IngestClient } from "./ingest-client.js";

import {

  MODEL_CASCADE,

  TIER_MODELS,

  type CascadeModel,

  isModelUnavailableError,

  modelFallbackChain,

  resolveModel,

} from "./models.js";



/**

 * Optional headless Atlas pipeline.

 * Runs phases in sequence, threading each phase's result into the next.

 * Stops at the first approval gate when run unattended, and reports.

 *

 * Model resilience: if a phase fails because a model is quota-limited, rate-limited,

 * unavailable, or blocked, the runner retries the same phase one tier down and

 * continues without interruption. It only stops a phase if every tier is exhausted.

 * See knowledge/model-resilience.md.

 */



type Phase = {

  role: string;

  tier: CascadeModel;

  gate?: "requirements" | "design" | "final";

  premiumGate?: boolean;

  brief: (task: string, prior: string) => string;

};



const PHASES: Phase[] = [

  {

    role: "atlas-pm",

    tier: TIER_MODELS.standard,

    gate: "requirements",

    brief: (task) =>

      `Act as atlas-pm. For this task, produce user stories with testable acceptance criteria and list open questions. Task: ${task}`,

  },

  {

    role: "atlas-architect",

    tier: TIER_MODELS.premium,

    gate: "design",

    premiumGate: true,

    brief: (task, prior) =>

      `Act as atlas-architect. Propose a simple, scalable design with an ADR and noted trade-offs. Requirements:\n${prior}\nTask: ${task}`,

  },

  {

    role: "atlas-dev",

    tier: TIER_MODELS.fast,

    brief: (task, prior) =>

      `Act as atlas-dev. Implement against this design, following clean-code and the team charter.\n${prior}\nTask: ${task}`,

  },

  {

    role: "atlas-qa",

    tier: TIER_MODELS.standard,

    brief: (_task, prior) =>

      `Act as atlas-qa. Write tests and a short test plan for the implemented change.\n${prior}`,

  },

  {

    role: "atlas-reviewer",

    tier: TIER_MODELS.premium,

    premiumGate: true,

    brief: (_task, prior) =>

      `Act as atlas-reviewer. Review for correctness and charter conformance, including the human-authored voice.\n${prior}`,

  },

  {

    role: "atlas-security",

    tier: TIER_MODELS.premium,

    gate: "final",

    premiumGate: true,

    brief: (_task, prior) =>

      `Act as atlas-security. Audit the change and give a pass or block recommendation with fixes.\n${prior}`,

  },

];



const GATE_BEFORE_ROLE: Record<string, "requirements" | "design"> = {

  "atlas-architect": "requirements",

  "atlas-dev": "design",

};



function isGateApproved(runDir: string, gate: string): boolean {

  const p = join(runDir, "gates", `${gate}.json`);

  if (!existsSync(p)) return false;

  try {

    return (JSON.parse(readFileSync(p, "utf8")) as { status?: string }).status === "approved";

  } catch {

    return false;

  }

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

  tier: CascadeModel,

): Promise<Awaited<ReturnType<typeof Agent.create>>> {

  const chain = modelFallbackChain(tier);

  let lastErr: unknown;

  for (let i = 0; i < chain.length; i++) {

    const modelId = resolveModel(chain[i]);

    try {

      return await Agent.create({

        apiKey,

        model: { id: modelId },

        local: { cwd: process.cwd() },

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

  phase: Phase,

  task: string,

  prior: string,

  apiKey: string,

  tier: CascadeModel,

  ingest: IngestClient | null,

): Promise<string> {

  await using agent = await createAgentWithFallback(apiKey, tier);

  const run = await agent.send(phase.brief(task, prior));

  console.log("run:", run.id, "agent:", agent.agentId, "tier:", tier);

  const streamIngest = ingest?.streamMapper(phase.role);

  for await (const event of run.stream()) {

    if (streamIngest) await streamIngest.onEvent(event);

    if (event.type !== "assistant") continue;

    for (const block of event.message.content) {

      if (block.type === "text") process.stdout.write(block.text);

    }

  }

  if (streamIngest) await streamIngest.flush();

  const result = await run.wait();

  if (result.status === "error") {

    // Run executed but failed mid-flight. Not a model-availability issue;

    // record and continue without interrupting the pipeline.

    console.error(`\n${phase.role} run errored: ${result.id}`);

    if (ingest) {

      await ingest.post({

        kind: "agent",

        actor: phase.role,

        message: `${phase.role}: run errored (${result.id})`,

        meta: { signal: "phase.error", sdkRunId: result.id },

      });

    }

  }

  return result.result ?? "";

}



async function runPhase(

  phase: Phase,

  task: string,

  prior: string,

  apiKey: string,

  logDowngrade: (note: string) => void,

  ingest: IngestClient | null,

): Promise<PhaseOutcome | null> {

  const start = MODEL_CASCADE.indexOf(phase.tier);

  for (let i = start; i < MODEL_CASCADE.length; i++) {

    const tier = MODEL_CASCADE[i];

    try {

      const text = await executeOnce(phase, task, prior, apiKey, tier, ingest);

      if (i > start) {

        const note = `- downgrade: ${phase.role} ${phase.tier} to ${tier}, reason quota-or-unavailable, run sdk, date ${new Date().toISOString()}`;

        logDowngrade(note);

        if (ingest) await ingest.downgrade(phase.role, phase.tier, tier);

        if (phase.premiumGate) {

          console.log(`\n[flag] premium gate ${phase.role} ran downgraded to ${tier}. Consider re-running at ${phase.tier}.`);

        }

      }

      return { text, usedTier: tier, downgraded: i > start };

    } catch (err) {

      const canRetry = isDowngradeTrigger(err) && i < MODEL_CASCADE.length - 1;

      if (canRetry) {

        console.log(`\n[downgrade] ${phase.role}: ${tier} unavailable, retrying at ${MODEL_CASCADE[i + 1]}.`);

        continue;

      }

      if (err instanceof CursorAgentError) {

        console.error(`\n${phase.role}: all tiers exhausted. ${err.message}`);

        return null;

      }

      throw err;

    }

  }

  return null;

}



async function main() {

  const task = process.argv.slice(2).join(" ").trim();

  if (!task) {

    console.error('Usage: npm run pipeline -- "<task description>"');

    process.exit(1);

  }

  const unattended = process.env.ATLAS_UNATTENDED === "1";

  const apiKey = process.env.CURSOR_API_KEY;

  if (!apiKey) {

    console.error("Set CURSOR_API_KEY before running.");

    process.exit(1);

  }



  const runId = process.env.ATLAS_RUN_ID || `${new Date().toISOString().slice(0, 10)}-sdk-run`;

  const runDir = join(process.cwd(), ".atlas", "runs", runId);

  mkdirSync(runDir, { recursive: true });

  const budgetFile = join(runDir, "budget.md");

  const downgrades: string[] = [];

  const ingest = ingestClientFromEnv(runId);

  const logDowngrade = (note: string) => {

    downgrades.push(note);

    appendFileSync(budgetFile, note + "\n");

  };



  if (ingest) {

    await ingest.system(`pipeline started: ${runId}`, { workflow: "sdk-pipeline", task });

  }



  let prior = "";

  for (const phase of PHASES) {

    if (phase.gate && unattended) {

      console.log(`\n[gate: ${phase.gate}] Approval required. Stopping unattended run before ${phase.role}.`);

      console.log("Re-run interactively to approve and continue.");

      if (ingest) await ingest.gatePause(phase.gate);

      break;

    }



    console.log(`\n=== ${phase.role} ===`);

    const needed = GATE_BEFORE_ROLE[phase.role];

    if (needed && !isGateApproved(runDir, needed)) {

      console.log(`\n[gate: ${needed}] Not approved. Approve in chat or write gates/${needed}.json, then re-run.`);

      if (ingest) await ingest.gatePause(needed);

      break;

    }

    if (ingest) await ingest.phaseStart(phase.role);

    const outcome = await runPhase(phase, task, prior, apiKey, logDowngrade, ingest);

    if (outcome === null) {

      console.error(`\nStopping: ${phase.role} could not run on any tier. Addressing the user.`);

      if (ingest) {

        await ingest.post({

          kind: "agent",

          actor: phase.role,

          message: `${phase.role}: failed — all tiers exhausted`,

          meta: { signal: "phase.failed" },

        });

      }

      process.exit(2);

    }

    if (ingest) await ingest.phaseComplete(phase.role, outcome.usedTier, { downgraded: outcome.downgraded });

    if (phase.gate && !unattended) {

      console.log(`\n[gate: ${phase.gate}] Approve in chat or write gates/${phase.gate}.json before continuing.`);

      if (ingest) await ingest.gatePause(phase.gate);

    }

    prior = `Output of ${phase.role}:\n${outcome.text}`;

  }



  if (downgrades.length > 0) {

    console.log(`\nModel downgrades this run (also in ${budgetFile}):`);

    downgrades.forEach((d) => console.log("  " + d));

  }

  if (ingest) await ingest.system("Pipeline complete.");

  console.log("\nPipeline complete.");

}



await main();

