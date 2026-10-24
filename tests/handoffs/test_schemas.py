import json
import jsonschema
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

def load_schema(path):
    with open(ROOT / path) as f:
        return json.load(f)


def test_base_schema_validates_minimal():
    base = load_schema("schemas/handoffs/base.schema.json")
    # Validate schema itself is valid JSON Schema draft-07
    jsonschema.Draft7Validator.check_schema(base)
    
    minimal = {
        "role": "atlas-pm",
        "workflow": "feature",
        "runId": "run-123",
        "variant": "full",
        "phaseState": "active",
        "tokenBudget": {
            "estimate": "medium",
            "rationale": "standard work"
        },
        "nextRole": {
            "role": "atlas-ba",
            "why": "need refinement",
            "firstAction": "review requirements"
        }
    }
    jsonschema.validate(minimal, base)


def test_pm_schema_validates():
    base = load_schema("schemas/handoffs/base.schema.json")
    pm = load_schema("schemas/handoffs/atlas-pm.schema.json")
    validator = jsonschema.Draft7Validator(pm)
    
    handoff = {
        "role": "atlas-pm",
        "workflow": "feature",
        "runId": "run-123",
        "variant": "full",
        "phaseState": "active",
        "tokenBudget": {"estimate": "medium", "rationale": "requirements work"},
        "nextRole": {"role": "atlas-ba", "why": "refine requirements", "firstAction": "create edge cases"},
        "outputs": {
            "artifacts": [{"path": "$ATLAS_DATA_DIR/runs/run-123/requirements.md", "type": "requirements"}]
        }
    }
    validator.validate(handoff)


def test_ba_schema_validates():
    ba = load_schema("schemas/handoffs/atlas-ba.schema.json")
    handoff = {
        "role": "atlas-ba",
        "workflow": "feature",
        "runId": "run-123",
        "variant": "full",
        "phaseState": "active",
        "tokenBudget": {"estimate": "medium", "rationale": "analysis work"},
        "nextRole": {"role": "atlas-architect", "why": "design system", "firstAction": "review refined requirements"},
        "outputs": {
            "artifacts": [{"path": "$ATLAS_DATA_DIR/runs/run-123/refined-requirements.md", "type": "refined-requirements"}]
        }
    }
    jsonschema.Draft7Validator(load_schema("schemas/handoffs/base.schema.json"))  # ensure base loads
    jsonschema.Draft7Validator(ba).validate(handoff)


def test_architect_schema_validates():
    architect = load_schema("schemas/handoffs/atlas-architect.schema.json")
    handoff = {
        "role": "atlas-architect",
        "workflow": "feature",
        "runId": "run-123",
        "variant": "full",
        "phaseState": "active",
        "tokenBudget": {"estimate": "heavy", "rationale": "design work"},
        "nextRole": {"role": "atlas-dev", "why": "implement design", "firstAction": "review design.md and ADRs"},
        "outputs": {
            "artifacts": [{"path": "$ATLAS_DATA_DIR/runs/run-123/design.md", "type": "design"}]
        }
    }
    jsonschema.Draft7Validator(architect).validate(handoff)


def test_lead_schema_validates():
    lead = load_schema("schemas/handoffs/atlas-lead.schema.json")
    handoff = {
        "role": "atlas-lead",
        "workflow": "feature",
        "runId": "run-123",
        "variant": "full",
        "phaseState": "active",
        "tokenBudget": {"estimate": "light", "rationale": "orchestration"},
        "nextRole": {"role": "atlas-pm", "why": "start requirements", "firstAction": "gather requirements"}
    }
    jsonschema.Draft7Validator(lead).validate(handoff)
