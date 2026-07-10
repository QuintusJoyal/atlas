import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  normalizePath,
  parsePathMap,
  pathMappingsFromEnv,
  resolveWorkspaceCwd,
} from "./workspace-path.js";

const HOST_REPO = "C:/Users/you/Projects/atlas";

describe("workspace-path", () => {
  it("normalizePath converts backslashes and trims trailing slash", () => {
    assert.equal(normalizePath("C:\\Users\\foo\\"), "C:/Users/foo");
    assert.equal(normalizePath("/workspace/"), "/workspace");
  });

  it("parsePathMap handles Windows host:container pairs", () => {
    const maps = parsePathMap(`${HOST_REPO}:/workspace`);
    assert.equal(maps.length, 1);
    assert.equal(maps[0].hostPrefix, HOST_REPO);
    assert.equal(maps[0].containerPrefix, "/workspace");
  });

  it("parsePathMap handles JSON object", () => {
    const maps = parsePathMap(
      JSON.stringify({ "C:/host/repo": "/workspace", "/other": "/projects/other" }),
    );
    assert.equal(maps.length, 2);
  });

  it("resolveWorkspaceCwd maps host meta.workspace to container cwd", () => {
    const env = {
      ATLAS_PATH_MAP: `${HOST_REPO}:/workspace`,
      ATLAS_WORKSPACE: "/workspace",
      ATLAS_WORKSPACE_MOUNTS: "/workspace,/projects/foo",
      ATLAS_ROOT: "/workspace",
    };
    assert.equal(
      resolveWorkspaceCwd(HOST_REPO, env),
      "/workspace",
    );
    assert.equal(
      resolveWorkspaceCwd(`${HOST_REPO}/sdk`, env),
      "/workspace/sdk",
    );
  });

  it("resolveWorkspaceCwd returns mount path when meta is already container-local", () => {
    const env = {
      ATLAS_WORKSPACE: "/workspace",
      ATLAS_WORKSPACE_MOUNTS: "/workspace,/projects/foo",
    };
    assert.equal(resolveWorkspaceCwd("/projects/foo", env), "/projects/foo");
  });

  it("resolveWorkspaceCwd falls back when meta is empty", () => {
    const env = { ATLAS_WORKSPACE: "/workspace", ATLAS_ROOT: "/legacy" };
    assert.equal(resolveWorkspaceCwd("", env), "/workspace");
  });

  it("pathMappingsFromEnv derives from ATLAS_WORKSPACE_HOST", () => {
    const env = {
      ATLAS_WORKSPACE_HOST: HOST_REPO,
      ATLAS_WORKSPACE: "/workspace",
    };
    const maps = pathMappingsFromEnv(env);
    assert.equal(maps.length, 1);
    assert.equal(maps[0].containerPrefix, "/workspace");
  });

  it("resolveWorkspaceCwd uses unmapped host path on native runner", () => {
    const env = { ATLAS_ROOT: HOST_REPO };
    assert.equal(
      resolveWorkspaceCwd(HOST_REPO, env),
      HOST_REPO,
    );
  });

  it("resolveWorkspaceCwd falls back in container when host path has no map", () => {
    const env = {
      ATLAS_WORKSPACE: "/workspace",
      ATLAS_WORKSPACE_MOUNTS: "/workspace",
    };
    assert.equal(
      resolveWorkspaceCwd(HOST_REPO, env),
      "/workspace",
    );
  });
});
