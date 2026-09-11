---
name: lingxi-video-test
description: Minimal smoke test for lingxi-video skill. Submits one video generation task and polls status.
---

Category: test

# Minimal Viable Test

## Goals

- Validate the video generation endpoint with a minimal request.
- If execution fails, record exact error details.

## Prerequisites

- Set `LINGXI_API_KEY` and `LINGXI_BASE_URL` in environment.
- Install `openai` SDK: `python -m pip install openai`
- Target skill: `skills/lingxi-video`

## Test Steps (Minimal)

1) Run the Python quick-start example from the skill with a simple prompt.
2) If async, poll until completion or timeout.
3) Record request summary, response summary, and success/failure reason.

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LINGXI_API_KEY"),
    base_url=os.getenv("LINGXI_BASE_URL"),
)

response = client.video.generations.create(
    model="sora-2",
    prompt="A cat sleeping on a couch",
)
print(response)
```

## Output

- Save results to `output/lingxi-video-test-results.md`.

## Result Template

- Date: YYYY-MM-DD
- Skill: skills/lingxi-video
- Model tested: (e.g. sora-2)
- Conclusion: pass / fail
- Task ID: (if async)
- Notes:
