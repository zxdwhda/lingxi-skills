---
name: lingxi-chat-test
description: Minimal smoke test for lingxi-chat skill. Sends one non-streaming chat completion.
---

Category: test

# Minimal Viable Test

## Goals

- Validate the chat completion endpoint with a minimal request.
- If execution fails, record exact error details.

## Prerequisites

- Set `LINGXI_API_KEY` and `LINGXI_BASE_URL` in environment.
- Install `openai` SDK: `python -m pip install openai`
- Target skill: `skills/lingxi-chat`

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

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hello"}],
    max_tokens=10,
)
print(response.choices[0].message.content)
```

## Output

- Save results to `output/lingxi-chat-test-results.md`.

## Result Template

- Date: YYYY-MM-DD
- Skill: skills/lingxi-chat
- Model tested: (e.g. gpt-4o-mini)
- Conclusion: pass / fail
- Latency: (ms)
- Notes:
