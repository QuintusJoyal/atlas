"""Workflow loading and parsing."""
import os
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = ROOT / "workflows"


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm_lines = lines[1:i]
            break
    else:
        return None
    
    # simple yaml-like parsing for our specific format
    try:
        # Use yaml for robustness
        fm_text = "\n".join(fm_lines)
        return yaml.safe_load(fm_text) if fm_text.strip() else {}
    except Exception:
        return {}


def load_workflow(workflow_name):
    wf_path = WORKFLOWS_DIR / f"{workflow_name}.md"
    if not wf_path.exists():
        # try with different names
        for f in WORKFLOWS_DIR.glob("*.md"):
            if workflow_name in f.name:
                wf_path = f
                break
        else:
            raise FileNotFoundError(f"Workflow not found: {workflow_name}")
    
    text = wf_path.read_text()
    fm = parse_frontmatter(text)
    return fm, text
