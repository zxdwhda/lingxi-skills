---
name: lingxi-image-test
description: Minimal smoke test for lingxi-image skill. Sends one image generation request.
---

Category: test

# Minimal Viable Test

## Goals

- Validate the image generation endpoint with a minimal request.
- If execution fails, record exact error details.

## Prerequisites

- Set `LINGXI_API_KEY` and `LINGXI_BASE_URL` in environment.
- Install `openai` SDK: `python -m pip install openai`
- Target skill: `skills/lingxi-image`

## Test Steps (Minimal)

1) Run the Python quick-start example from the skill with a simple prompt.
2) Record request summary, response summary, and success/failure reason.

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LINGXI_API_KEY"),
    base_url=os.getenv("LINGXI_BASE_URL"),
)

response = client.images.generate(
    model="dall-e-3",
    prompt="A simple red apple on a white background",
    size="1024x1024",
    n=1,
)
print(response.data[0].url)
```

## Output

- Save results to `output/lingxi-image-test-results.md`.

## Result Template

- Date: YYYY-MM-DD
- Skill: skills/lingxi-image
- Model tested: (e.g. dall-e-3)
- Conclusion: pass / fail
- Latency: (ms)
- Notes:
