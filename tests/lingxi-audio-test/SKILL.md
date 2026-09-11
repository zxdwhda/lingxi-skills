---
name: lingxi-audio-test
description: Minimal smoke test for lingxi-audio skill. Sends one TTS request.
---

Category: test

# Minimal Viable Test

## Goals

- Validate the TTS endpoint with a minimal request.
- If execution fails, record exact error details.

## Prerequisites

- Set `LINGXI_API_KEY` and `LINGXI_BASE_URL` in environment.
- Install `openai` SDK: `python -m pip install openai`
- Target skill: `skills/lingxi-audio`

## Test Steps (Minimal)

1) Run the Python quick-start example from the skill.
2) Record request summary, response summary, and success/failure reason.

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LINGXI_API_KEY"),
    base_url=os.getenv("LINGXI_BASE_URL"),
)

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello from Lingxi audio test.",
)
response.stream_to_file("output/lingxi-audio-test.mp3")
print("Audio saved")
```

## Output

- Save results to `output/lingxi-audio-test-results.md`.

## Result Template

- Date: YYYY-MM-DD
- Skill: skills/lingxi-audio
- Model tested: (e.g. tts-1)
- Conclusion: pass / fail
- Latency: (ms)
- Notes:
