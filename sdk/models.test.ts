import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  MODEL_CASCADE,
  TIER_MODELS,
  isModelUnavailableError,
  modelFallbackChain,
  resolveModel,
  roleTierToModel,
} from "./models.js";

describe("models", () => {
  it("roleTierToModel maps tier names to SDK slugs", () => {
    assert.equal(roleTierToModel("premium"), TIER_MODELS.premium);
    assert.equal(roleTierToModel("standard"), TIER_MODELS.standard);
    assert.equal(roleTierToModel("fast"), TIER_MODELS.fast);
    assert.equal(roleTierToModel(undefined), TIER_MODELS.standard);
    assert.equal(TIER_MODELS.premium, "claude-opus-4-8");
  });

  it("resolveModel maps IDE-only slugs to SDK-valid ids", () => {
    assert.equal(resolveModel("composer-2.5-fast"), "composer-2.5");
    assert.equal(resolveModel("composer-2.5"), "composer-2.5");
    assert.equal(resolveModel("claude-opus-4-8-thinking-high"), "claude-opus-4-8");
    assert.equal(resolveModel("claude-opus-4-7-thinking-medium"), "claude-opus-4-7");
    assert.equal(resolveModel("composer-2"), "composer-2");
  });

  it("modelFallbackChain starts at resolved preferred model", () => {
    assert.deepEqual(modelFallbackChain("composer-2.5-fast"), [
      "composer-2.5",
      "composer-2",
      "default",
    ]);
    assert.deepEqual(modelFallbackChain("composer-2.5"), [
      "composer-2.5",
      "composer-2",
      "default",
    ]);
    assert.deepEqual(modelFallbackChain("claude-opus-4-8-thinking-high"), [
      ...MODEL_CASCADE,
    ]);
    assert.deepEqual(modelFallbackChain("inherit"), ["default"]);
    assert.deepEqual(modelFallbackChain(TIER_MODELS.premium), [...MODEL_CASCADE]);
  });

  it("isModelUnavailableError detects cannot-use-model messages", () => {
    assert.equal(
      isModelUnavailableError(new Error("Cannot use this model: composer-2.5-fast")),
      true,
    );
    assert.equal(isModelUnavailableError(new Error("network timeout")), false);
  });
});
