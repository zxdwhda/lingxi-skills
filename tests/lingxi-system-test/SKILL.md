---
name: lingxi-system-test
description: Minimal smoke test for lingxi-system skill. Lists tokens and retrieves account info.
---

Category: test

# Minimal Viable Test

## Goals

- Validate the system API endpoints with read-only requests.
- If execution fails, record exact error details.

## Prerequisites

- Set `LINGXI_API_KEY` and `LINGXI_BASE_URL` in environment.
- Target skill: `skills/lingxi-system`

## Test Steps (Minimal)

1) Run the read-only examples from the skill:
   - List tokens
   - Get account info
   - Get supported models
2) Record request summary, response summary, and success/failure reason.

```python
import os
import requests

base_url = os.getenv("LINGXI_BASE_URL")
headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

# List tokens
resp = requests.get(f"{base_url}/api/token", headers=headers)
print("Tokens:", len(resp.json().get("data", [])))

# Get account info
resp = requests.get(f"{base_url}/api/user", headers=headers)
print("Account:", resp.json().get("data", {}))

# Get models
resp = requests.get(f"{base_url}/api/models", headers=headers)
print("Models:", len(resp.json().get("data", [])))
```

## Output

- Save results to `output/lingxi-system-test-results.md`.

## Result Template

- Date: YYYY-MM-DD
- Skill: skills/lingxi-system
- Conclusion: pass / fail
- Latency: (ms)
- Notes:
