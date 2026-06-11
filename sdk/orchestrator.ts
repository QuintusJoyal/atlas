import { mkdirSync, appendFileSync } from "node:fs";
import { join } from "node:path";
import { Agent, CursorAgentError } from "@cursor/sdk";

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

// Downgrade cascade. "auto" stands in for the subagent "inherit" tier (server picks).
const TIERS = [
  "claude-opus-4-8-thinking-high",
  "composer-2.5",
  "composer-2.5-fast",
  "auto",
] as const;
type Tier = (typeof TIERS)[number];

type Phase = {
  role: string;
  tier: Tier;
  gate?: "requirements" | "design" | "final";
  premiumGate?: boolean;
  brief: (task: string, prior: string) => string;
};

const PHASES: Phase[] = [
  {
    role: "atlas-pm",
    tier: "composer-2.5",
    gate: "requirements",
    brief: (task) =>
      `Act as atlas-pm. For this task, produce user stories with testable acceptance criteria and list open questions. Task: ${task}`,
  },
  {
    role: "atlas-architect",
    tier: "claude-opus-4-8-thinking-high",
    gate: "design",
    premiumGate: true,
    brief: (task, prior) =>
      `Act as atlas-architect. Propose a simple, scalable design with an ADR and noted trade-offs. Requirements:\n${prior}\nTask: ${task}`,
  },
  {
    role: "atlas-dev",
    tier: "composer-2.5-fast",
    brief: (task, prior) =>
      `Act as atlas-dev. Implement against this design, following clean-code and the team charter.\n${prior}\nTask: ${task}`,
  },
  {
    role: "atlas-qa",
    tier: "composer-2.5",
    brief: (_task, prior) =>
      `Act as atlas-qa. Write tests and a short test plan for the implemented change.\n${prior}`,
  },
  {
    role: "atlas-reviewer",
    tier: "claude-opus-4-8-thinking-high",
    premiumGate: true,
    brief: (_task, prior) =>
      `Act as atlas-reviewer. Review for correctness and charter conformance, including the human-authored voice.\n${prior}`,
  },
  {
    role: "atlas-security",
    tier: "claude-opus-4-8-thinking-high",
    gate: "final",
    premiumGate: true,
    brief: (_task, prior) =>
      `Act as atlas-security. Audit the change and give a pass or block recommendation with fixes.\n${prior}`,
  },
];

function isDowngradeTrigger(err: unknown): boolean {
  if (err instanceof CursorAgentError) {
    const msg = (err.message || "").toLowerCase();
    return (
      err.isRetryable ||
      msg.includes("quota") ||
      msg.includes("rate limit") ||
      msg.includes("rate-limit") ||
      msg.includes("unavailable") ||
      msg.includes("not available") ||
      msg.includes("blocked") ||
      msg.includes("permission")
    );
  }
  return false;
}

type PhaseOutcome = {
  text: string;
  usedTier: Tier;
  downgraded: boolean;
};

async function executeOnce(phase: Phase, task: string, prior: string, apiKey: string, tier: Tier): Promise<string> {
  await using agent = await Agent.create({
    apiKey,
    model: { id: tier },
    local: { cwd: process.cwd() },
  });
  const run = await agent.send(phase.brief(task, prior));
  console.log("run:", run.id, "agent:", agent.agentId, "tier:", tier);
  for await (const event of run.stream()) {
    if (event.type !== "assistant") continue;
    for (const block of event.message.content) {
      if (block.type === "text") process.stdout.write(block.text);
    }
  }
  const result = await run.wait();
  if (result.status === "error") {
    // Run executed but failed mid-flight. Not a model-availability issue;
    // record and continue without interrupting the pipeline.
    console.error(`\n${phase.role} run errored: ${result.id}`);
  }
  return result.result ?? "";
}

async function runPhase(
  phase: Phase,
  task: string,
  prior: string,
  apiKey: string,
  logDowngrade: (note: string) => void,
): Promise<PhaseOutcome | null> {
  const start = TIERS.indexOf(phase.tier);
  for (let i = start; i < TIERS.length; i++) {
    const tier = TIERS[i];
    try {
      const text = await executeOnce(phase, task, prior, apiKey, tier);
      if (i > start) {
        logDowngrade(
          `- downgrade: ${phase.role} ${phase.tier} to ${tier}, reason quota-or-unavailable, run sdk, date ${new Date().toISOString()}`,
        );
        if (phase.premiumGate) {
          console.log(`\n[flag] premium gate ${phase.role} ran downgraded to ${tier}. Consider re-running at ${phase.tier}.`);
        }
      }
      return { text, usedTier: tier, downgraded: i > start };
    } catch (err) {
      const canRetry = isDowngradeTrigger(err) && i < TIERS.length - 1;
      if (canRetry) {
        console.log(`\n[downgrade] ${phase.role}: ${tier} unavailable, retrying at ${TIERS[i + 1]}.`);
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

  const runId = `${new Date().toISOString().slice(0, 10)}-sdk-run`;
  const runDir = join(process.cwd(), ".atlas", "runs", runId);
  mkdirSync(runDir, { recursive: true });
  const budgetFile = join(runDir, "budget.md");
  const downgrades: string[] = [];
  const logDowngrade = (note: string) => {
    downgrades.push(note);
    appendFileSync(budgetFile, note + "\n");
  };

  let prior = "";
  for (const phase of PHASES) {
    if (phase.gate && unattended) {
      console.log(`\n[gate: ${phase.gate}] Approval required. Stopping unattended run before ${phase.role}.`);
      console.log("Re-run interactively to approve and continue.");
      break;
    }

    console.log(`\n=== ${phase.role} ===`);
    const outcome = await runPhase(phase, task, prior, apiKey, logDowngrade);
    if (outcome === null) {
      console.error(`\nStopping: ${phase.role} could not run on any tier. Addressing the user.`);
      process.exit(2);
    }
    prior = `Output of ${phase.role}:\n${outcome.text}`;
  }

  if (downgrades.length > 0) {
    console.log(`\nModel downgrades this run (also in ${budgetFile}):`);
    downgrades.forEach((d) => console.log("  " + d));
  }
  console.log("\nPipeline complete.");
}

await main();
