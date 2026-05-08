---
name: lingxi-entry-test
description: Minimal routing smoke test for lingxi-entry skill.
version: 1.0.0
---

Category: test

# Minimal Viable Test

## Goals

- Validate only the minimal request path for this skill.
- If execution fails, record exact error details without guessing parameters.

## Prerequisites

- Prepare authentication: set `LINGXI_API_KEY` and `LINGXI_BASE_URL`.
- Target skill: `skills/lingxi-entry`

## Test Steps (Minimal)

1) Open the target skill `SKILL.md` and verify routing table completeness.
2) Run the validation command from the skill:
   ```bash
   mkdir -p output/lingxi-entry
   echo "validation_placeholder" > output/lingxi-entry/validate.txt
   ```
3) Verify `output/lingxi-entry/validate.txt` exists.

## Output

- Save results to `output/lingxi-entry-test-results.md`.

## Result Template

- Date: YYYY-MM-DD
- Skill: skills/lingxi-entry
- Conclusion: pass / fail
- Notes:
