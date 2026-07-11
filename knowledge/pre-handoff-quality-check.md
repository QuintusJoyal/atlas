---
name: pre-handoff-quality-check
category: process
load-when: Before submitting any handoff or declaring completion
skip-when: In-progress work, intermediate updates
description: 5-point verification before declaring done. Includes 3-strike rule for repeated errors.
audience: [all]
tags: [quality, handoff, verification, completion]
---

# Pre-handoff quality check

Before submitting any handoff or declaring completion:

## Quick Reference
1. Does the output address the original task?
2. Are all file references valid?
3. Have you verified changes compile/run/pass tests?
4. Is there anything uncertain? Flag it explicitly.
5. Would a peer reviewer need to ask "why did you do X?"

## Checklist

1. Does the output address the original task?
2. Are all file references valid (files exist, line numbers correct)?
3. Have you verified your changes compile/run/pass tests?
4. Is there anything you're uncertain about? Flag it explicitly.
5. Would a peer reviewer need to ask "why did you do X?" If so, explain X.

## 3-strike rule

Don't loop more than 3 times fixing the same error. On the third failure, escalate with diagnostic context:
- What you tried
- What failed
- What you suspect
- What help is needed

This prevents infinite loops and ensures stuck agents escalate rather than spinning.
