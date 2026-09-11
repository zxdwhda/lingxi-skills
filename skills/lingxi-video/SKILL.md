---
name: lingxi-video
description: Use when the user wants to generate or edit videos through the Lingxi API Gateway. Trigger when the user asks to (1) generate a video from text, (2) generate a video from an image, (3) extend or transform an existing video, or (4) mentions any video generation platform (Kling, Sora, Veo, Luma, Runway, MiniMax, Doubao).
---

Category: provider

# Lingxi Video

## When to Use

- User wants to generate a video from text or image
- User wants to extend, edit, or transform a video
- User mentions any video generation platform (Kling, Sora, Veo, Luma, etc.)
- User says "视频", "做段视频", "图生视频", "animation"

## Configuration

1. Read `LINGXI_API_KEY` from environment. If not set, ask the user.
2. Base URL: `https://api.aicso.top/v1`
3. Install if needed: `pip install openai requests`

## Image/Video Upload Handling

**For local image/video files**: Upload via `lingxi-entry` image bed first to get a public URL.

**For image-to-video tasks**: Most platforms require a URL reference. Always use the image bed for local files.

## Intent Routing

| User Says | Recommended Platform | Model | Sync/Async |
|-----------|---------------------|-------|-----------|
| "Generate video", "Text to video" | Kling (recommended) | `kling-text-to-video` | Async |
| "Image to video", "Animate this photo" | Kling | `kling-image-to-video` | Async |
| "Cinematic video", "High quality" | Sora | `sora-2` | Async (OpenAI fmt) |
| "Quick video", "Fast generation" | Veo | `veo3.1-fast` | Async |
| "Extend video" | Luma / Kling | `ray-v2` / kling extend | Async |
| "Character video" | Sora | `sora-2` | Async |
| "Chinese style video" | MiniMax (海螺) | `MiniMax-Hailuo-02` | Async |
| "Douyin style" | Doubao | `doubao-seedance` | Async |

> **Default recommendation**: Use **Kling** for most cases (best quality/price balance, China-friendly). Use **Sora** for cinematic quality.

## Core Code Templates

### OpenAI-compatible (Sora / Veo / Grok)

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("LINGXI_API_KEY"),
    base_url="https://api.aicso.top/v1",
)

# Text-to-video
response = client.video.generations.create(
    model="sora-2",
    prompt="A cat playing piano in a jazz club",
)
print(response.video_url)

# Image-to-video
response = client.video.generations.create(
    model="sora-2",
    prompt="Make it cinematic",
    image=open("input.png", "rb"),
)
```

### Kling Text-to-Video

```python
import requests
import time

base_url = "https://api.aicso.top"
headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

# Text-to-video
resp = requests.post(f"{base_url}/kling/v1/videos/text2video", headers=headers, json={
    "model_name": "kling-v1",  # Options: kling-v1, kling-v2-master, kling-v2-5-turbo, kling-v3
    "prompt": "A dragon flying over a mountain",
    "mode": "std",        # std (standard) or pro (high quality)
    "duration": "5",      # "5" or "10"
    "aspect_ratio": "16:9",
}).json()
task_id = resp["data"]["task_id"]

# Poll
for _ in range(60):
    status = requests.get(f"{base_url}/kling/v1/videos/text2video/{task_id}", headers=headers).json()
    if status["data"]["task_status"] == "completed":
        print("Video URL:", status["data"].get("video_url"))
        break
    elif status["data"]["task_status"] == "failed":
        print("Failed:", status["data"].get("fail_reason"))
        break
    time.sleep(10)
```

### Kling Image-to-Video

```python
resp = requests.post(f"{base_url}/kling/v1/videos/image2video", headers=headers, json={
    "model_name": "kling-v1",
    "image": "https://imageproxy.zhongzhuan.chat/api/proxy/image/...",
    "prompt": "The character walks forward slowly",
    "mode": "std",
    "duration": "5",
}).json()
task_id = resp["data"]["task_id"]
# Poll same as text2video above
```

### Sora / Veo Unified Format

```python
resp = requests.post(f"{base_url}/v1/video/create", headers=headers, json={
    "model": "sora-2",  # or "veo3.1-fast"
    "prompt": "A drone flying over a tropical beach",
    "size": "1080x1920",  # Required for sora-2
    "duration": 4,        # sora-2 supports: 4, 8, 12 seconds
}).json()
task_id = resp["id"]

for _ in range(60):
    status = requests.get(f"{base_url}/v1/video/query?id={task_id}", headers=headers).json()
    if status["status"] == "completed":
        print("Video URL:", status["video_url"])
        break
    time.sleep(10)
```

### Luma Native Async

```python
resp = requests.post(f"{base_url}/luma/generations", headers=headers, json={
    "user_prompt": "A neon-lit cyberpunk street at night",
    "model_name": "ray-v2",
    "duration": "5s",
    "resolution": "720p",
}).json()
task_id = resp["data"]["task_id"]

for _ in range(60):
    result = requests.get(f"{base_url}/luma/generations/{task_id}", headers=headers).json()
    if result.get("state") == "completed":
        print("Video URL:", result["video"]["url"])
        break
    if result.get("state") == "failed":
        raise RuntimeError("Luma task failed")
    time.sleep(10)
```

### MiniMax (海螺) Async

```python
resp = requests.post(f"{base_url}/minimax/v1/video_generation", headers=headers, json={
    "model": "MiniMax-Hailuo-02",
    "prompt": "A koi fish swimming in a pond",
    "duration": 10,
}).json()
task_id = resp["task_id"]

for _ in range(60):
    result = requests.get(f"{base_url}/minimax/v1/query/video_generation?task_id={task_id}", headers=headers).json()
    status = result["data"]["status"]
    if status == "Success":
        print("Video URL:", result["data"]["file"]["download_url"])
        break
    if status == "Failed":
        raise RuntimeError("MiniMax task failed")
    time.sleep(10)
```

### Doubao Async

```python
resp = requests.post(f"{base_url}/volc/v1/contents/generations/tasks", headers=headers, json={
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
        {"type": "text", "text": "A girl holding a fox --resolution 720p --ratio 16:9 --duration 5"}
    ],
}).json()
task_id = resp["id"]

for _ in range(60):
    result = requests.get(f"{base_url}/volc/v1/contents/generations/tasks/{task_id}", headers=headers).json()
    if result.get("status") == "succeeded":
        print("Video URL:", result["content"]["video_url"])
        break
    time.sleep(10)
```

## Platform Comparison

| Platform | Best For | Duration | Resolution | China Access |
|----------|----------|----------|-----------|-------------|
| Kling | General use, best value | 5-10s | Up to 1080p | ✅ Excellent |
| Sora | Cinematic quality | Up to 20s | Up to 1080p | ✅ Good |
| Veo | Fast generation | 5-8s | Up to 1080p | ✅ Good |
| Luma | Artistic/Creative | 5s | 720p | ✅ Good |
| MiniMax | Chinese content | 5-10s | 720p | ✅ Excellent |
| Doubao | TikTok style | 5-10s | 720p | ✅ Excellent |
| Runway | Professional editing | 4-10s | 720p-1080p | ✅ Good |

## Error Handling

- **"无可用渠道"** → Current token group does not support this model. Switch group or try another model.
- **"上游负载已饱和"** → Upstream provider is temporarily overloaded. Wait and retry.
- **"Invalid URL"** → Endpoint path error. Most native endpoints use `https://api.aicso.top` without `/v1` prefix.
- **"size is required for sora-2"** → Add `size` and `duration` (4, 8, or 12) parameters.
- **"MissingParameter: X-TC-Action"** → Tencent Cloud models require specific headers; check the platform docs.

## Anti-patterns

- Do NOT forget to poll async tasks; all video platforms are async
- Do NOT send local files directly to URL-only endpoints; use image bed first
- Do NOT use text-to-video when user provides an image; route to image-to-video
- Do NOT ignore duration limits (most platforms max 10 seconds)

## Workflow

1. Understand user's video request (subject, style, duration, source)
2. Choose platform: default to Kling, use Sora for cinematic
3. If image-to-video: upload local image to bed first, get URL
4. Submit generation task
5. Poll for completion and report progress to user
6. Return final video URL
