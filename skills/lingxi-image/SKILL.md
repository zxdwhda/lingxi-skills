---
name: lingxi-image
description: Use when the user wants to generate or edit images through the Lingxi API Gateway. Trigger when the user asks to (1) generate an image from text, (2) edit or modify an existing image, (3) blend or mix images, or (4) mentions any image generation model (DALL-E, Midjourney, FLUX, GPT Image-1, Qwen, Doubao, Ideogram, Grok).
---

Category: provider

# Lingxi Image

## When to Use

- User wants to generate an image from text
- User wants to edit or modify an existing image
- User mentions any image generation model (DALL-E, Midjourney, FLUX, etc.)
- User says "画", "生成图", "做张海报", "image"

## Configuration

1. Read `LINGXI_API_KEY` from environment. If not set, ask the user.
2. Base URL: `https://api.aicso.top/v1`
3. Install if needed: `pip install openai requests`

## Image Upload Handling

**For local image files**: Upload via `lingxi-entry` image bed first to get a public URL.

**For image editing tasks** (DALL-E edit, GPT Image-1 edit): OpenAI format accepts local files directly via multipart upload.

## Intent Routing

| User Says | Recommended Platform | Model | Sync/Async |
|-----------|---------------------|-------|-----------|
| "Generate image", "Draw", "画一张" | DALL-E 3 (simplest) | `dall-e-3` | Sync |
| "High quality image", "Best image" | GPT Image-1 | `gpt-image-1` | Sync |
| "Grok style image" | Grok Image | `grok-3-image` | Sync |
| "Anime style", "Specific art style" | Midjourney | `midjourney` | Async |
| "Photo realistic", "Landscape" | FLUX (Replicate) | `flux-kontext-dev` | Async |
| "Quick image", "Cheap image" | Doubao / Qwen | `doubao-seedream` / `qwen-image-max` | Sync |
| "Edit image", "Change this image" | DALL-E 3 Edit / GPT Image-1 | `dall-e-3` / `gpt-image-1` | Sync |
| "Blend images", "Mix images" | Midjourney Blend | `midjourney` | Async |

> **Default recommendation**: Use `dall-e-3` for most cases (simple, fast, reliable). Use `midjourney` for artistic/high-quality requests.

## Core Code Templates

### OpenAI-compatible Generation (DALL-E 3 / FLUX / Qwen / Doubao)

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("LINGXI_API_KEY"),
    base_url="https://api.aicso.top/v1",
)

response = client.images.generate(
    model="dall-e-3",  # or "flux-kontext-dev", "qwen-image-max", "doubao-seedream-3-0-t2i-250415"
    prompt="USER_PROMPT_HERE",
    size="1024x1024",  # Options: 1024x1024, 1792x1024, 1024x1792
    n=1,
)
# Lingxi returns base64 for most image models; save to file
import base64
image_bytes = base64.b64decode(response.data[0].b64_json)
with open("output.png", "wb") as f:
    f.write(image_bytes)
print("Saved to output.png")
```

### GPT Image-1

```python
response = client.images.generate(
    model="gpt-image-1",
    prompt="A hand-drawn cat wearing a wizard hat",
    size="1024x1024",
    n=1,
)
# Returns base64
import base64
image_bytes = base64.b64decode(response.data[0].b64_json)
with open("output.png", "wb") as f:
    f.write(image_bytes)
```

### Image Edit (DALL-E / GPT Image-1)

```python
response = client.images.edit(
    image=open("original.png", "rb"),
    mask=open("mask.png", "rb"),  # optional: white = edit region
    prompt="Add a rainbow in the sky",
    model="gpt-image-1",
    size="1024x1024",
)
```

### Grok Image

```python
response = client.images.generate(
    model="grok-3-image",
    prompt="A futuristic city",
    size="960x960",
)
print(response.data[0].url)
```

### Midjourney Async Flow

```python
import requests
import time

base_url = "https://api.aicso.top"
headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

# 1. Submit
resp = requests.post(f"{base_url}/mj/submit/imagine", headers=headers, json={
    "botType": "MID_JOURNEY",
    "prompt": "A serene Japanese garden with cherry blossoms",
}).json()
task_id = resp["result"]

# 2. Poll
for _ in range(60):
    status = requests.get(f"{base_url}/mj/task/{task_id}/fetch", headers=headers).json()
    if status["status"] == "SUCCESS":
        print("Image URL:", status["imageUrl"])
        break
    elif status["status"] == "FAILURE":
        print("Failed:", status["failReason"])
        break
    time.sleep(5)
```

### Replicate FLUX Async Flow

```python
import requests
import time

base_url = "https://api.aicso.top"
headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

# 1. Create
resp = requests.post(
    f"{base_url}/replicate/v1/models/black-forest-labs/flux-kontext-dev/predictions",
    headers=headers,
    json={"input": {"prompt": "A beautiful landscape", "go_fast": True}},
).json()
prediction_id = resp["id"]

# 2. Poll
for _ in range(60):
    status = requests.get(f"{base_url}/replicate/v1/predictions/{prediction_id}", headers=headers).json()
    if status["status"] == "succeeded":
        print("Output:", status["output"])
        break
    elif status["status"] in ("failed", "canceled"):
        raise RuntimeError(f"Failed: {status.get('error')}")
    time.sleep(5)
```

## Platform Notes

| Platform | Best For | Size Options | Special Features |
|----------|----------|-------------|------------------|
| DALL-E 3 | General use, reliability | 1024x1024, 1792x1024, 1024x1792 | Simple, fast |
| GPT Image-1 | High quality, editing | 1024x1024 | Best edit quality |
| Midjourney | Artistic, stylized | Various | Upscale, vary, blend |
| FLUX | Photorealistic | Various | Kontext-aware |
| Grok | X/Twitter style | 960x960 | Native Grok aesthetic |
| Qwen | Chinese prompts | Various | Good for Asian aesthetics |
| Doubao | Fast, cheap | Various | ByteDance models |

## Error Handling

- **"无可用渠道"** → The current token group does not support this model. Switch group or model.
- **"Invalid URL"** → Usually means a non-OpenAI endpoint was prefixed with `/v1`. Check the base URL (most native endpoints use `https://api.aicso.top` without `/v1`).
- **"this channel is designed for task-based operations"** → The model requires a native async endpoint, not the OpenAI-compatible one. Use the platform-specific code template.
- **"all_retries_failed" / "上游负载已饱和"** → The upstream provider is temporarily unavailable. Retry later.

## Anti-patterns

- Do NOT send base64 images to URL-only platforms (Midjourney, some Kling); use image bed first
- Do NOT use `dall-e-3` for complex artistic requests; use Midjourney instead
- Do NOT forget to handle async tasks (Midjourney, Replicate, Fal.ai need polling)
- Do NOT use `n > 1` with models that don't support it

## Workflow

1. Understand user's image request (subject, style, size)
2. Choose platform: default to DALL-E 3, upgrade to Midjourney for artistic needs
3. If editing: get original image (upload to bed if local URL needed)
4. Execute generation/edit call
5. For async platforms: poll and report progress
6. Return final image URL to user
