import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { parseKickoffArgs } from "./kickoff-via-cc.js";

describe("parseKickoffArgs", () => {
  it("parses required workflow and task", () => {
    const args = parseKickoffArgs(["--workflow", "bugfix", "--task", "Fix login timeout"]);
    assert.deepEqual(args, {
      workflow: "bugfix",
      task: "Fix login timeout",
      rationale: undefined,
      autoRun: true,
    });
  });

  it("parses short flags, rationale, and --no-auto-run", () => {
    const args = parseKickoffArgs([
      "-w",
      "feature",
      "-t",
      "Add export",
      "-r",
      "User-facing CSV export",
      "--no-auto-run",
    ]);
    assert.deepEqual(args, {
      workflow: "feature",
      task: "Add export",
      rationale: "User-facing CSV export",
      autoRun: false,
    });
  });

  it("trims workflow and task", () => {
    const args = parseKickoffArgs(["--workflow", "  hotfix  ", "--task", "  Patch CVE  "]);
    assert.equal(args.workflow, "hotfix");
    assert.equal(args.task, "Patch CVE");
  });

  it("throws when task is missing", () => {
    assert.throws(() => parseKickoffArgs(["--workflow", "feature"]), /--task is required/);
  });

  it("throws when workflow is empty", () => {
    assert.throws(
      () => parseKickoffArgs(["--workflow", "", "--task", "x"]),
      /--workflow is required/,
    );
  });

  it("throws on unknown flags", () => {
    assert.throws(
      () => parseKickoffArgs(["--workflow", "feature", "--task", "x", "--bogus"]),
      /Unknown argument: --bogus/,
    );
  });
});
