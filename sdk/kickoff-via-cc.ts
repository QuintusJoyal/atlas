/**
 * CLI: create a Control Center run via POST /api/kickoff/start.
 * Requires ATLAS_CC_URL and ATLAS_CC_TOKEN in the environment.
 */
import { pathToFileURL } from "node:url";
import { ccFetch } from "./cc-client.js";

export interface KickoffCliArgs {
  workflow: string;
  task: string;
  rationale?: string;
  autoRun: boolean;
}

export interface KickoffResult {
  id: string;
  jobId?: string;
  autoRunSkipped?: string;
}

export function parseKickoffArgs(argv: string[]): KickoffCliArgs {
  let workflow = "feature";
  let task = "";
  let rationale: string | undefined;
  let autoRun = true;

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--workflow" || arg === "-w") {
      workflow = argv[++i] ?? "";
      continue;
    }
    if (arg === "--task" || arg === "-t") {
      task = argv[++i] ?? "";
      continue;
    }
    if (arg === "--rationale" || arg === "-r") {
      rationale = argv[++i] ?? "";
      continue;
    }
    if (arg === "--no-auto-run") {
      autoRun = false;
      continue;
    }
    if (arg === "--help" || arg === "-h") {
      printUsage();
      process.exit(0);
    }
    throw new Error(`Unknown argument: ${arg}`);
  }

  if (!workflow.trim()) throw new Error("--workflow is required");
  if (!task.trim()) throw new Error("--task is required");

  return {
    workflow: workflow.trim(),
    task: task.trim(),
    rationale: rationale?.trim() || undefined,
    autoRun,
  };
}

function printUsage(): void {
  console.log(`Usage: kickoff-via-cc.ts --workflow <preset> --task "<title>" [options]

Options:
  --workflow, -w   Workflow preset (feature, bugfix, hotfix, …)
  --task, -t       Run title / task description (required)
  --rationale, -r  Optional workflow rationale
  --no-auto-run    Create run skeleton only; do not enqueue pipeline.run
  --help, -h       Show this help

Environment:
  ATLAS_CC_URL     Control Center base URL
  ATLAS_CC_TOKEN   API token (X-Atlas-CC-Token)`);
}

export async function kickoffViaCc(args: KickoffCliArgs): Promise<KickoffResult> {
  const res = await ccFetch("/api/kickoff/start", {
    method: "POST",
    body: JSON.stringify({
      workflow: args.workflow,
      task: args.task,
      rationale: args.rationale,
      autoRun: args.autoRun,
    }),
  });

  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as { error?: string };
    throw new Error(err.error || res.statusText || `HTTP ${res.status}`);
  }

  return (await res.json()) as KickoffResult;
}

async function main(): Promise<void> {
  try {
    const args = parseKickoffArgs(process.argv.slice(2));
    const result = await kickoffViaCc(args);
    console.log(JSON.stringify(result));
  } catch (e) {
    console.error((e as Error).message);
    process.exit(1);
  }
}

const isMain =
  process.argv[1] !== undefined &&
  pathToFileURL(process.argv[1]).href === import.meta.url;

if (isMain) {
  void main();
}
