---
name: lingxi-image
description: Use when generating or editing images through Lingxi API Gateway, including Midjourney, DALL-E 3, FLUX, Ideogram, Grok Image, GPT Image-1, Qwen Image, Doubao, and platform-native formats (Replicate, Fal.ai, Tencent AIGC).
version: 1.2.0
---

Category: provider

# Lingxi Image

## Validation

```bash
mkdir -p output/lingxi-image
python -m py_compile skills/lingxi-image/scripts/image_demo.py && echo "py_compile_ok" > output/lingxi-image/validate.txt
```

Pass criteria: command exits 0 and `output/lingxi-image/validate.txt` is generated.

## Output And Evidence

- Save generated image URLs and metadata to `output/lingxi-image/`.
- Keep one end-to-end run log for troubleshooting.

## Prerequisites

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install openai requests
```

- Set `LINGXI_API_KEY` and `LINGXI_BASE_URL` in environment.

## Supported Models & Platforms

| Platform | Model Examples | Format | Async/Sync |
|----------|---------------|--------|------------|
| DALL-E 3 | `dall-e-3` | OpenAI | Sync |
| Midjourney | `midjourney` | Native (task-based) | Async |
| FLUX | `flux-kontext-dev`, `flux-schnell`, `flux-kontext-pro`, `flux-kontext-max` | Replicate / OpenAI-compatible | Async (Replicate) / Sync (OpenAI) |
| Ideogram | `ideogram-3.0`, `V_1`, `V_1_TURBO`, `V_2`, `V_2_TURBO` | Native | Sync |
| Grok Image | `grok-3-image` | Native | Sync |
| GPT Image-1 | `gpt-image-1`, `gpt-image-1.5`, `gpt-image-2`, `gpt-image-2-all` | OpenAI | Sync |
| Qwen Image | `qwen-image-max`, `z-image-turbo`, `qwen-image-edit-2509` | Native / OpenAI-compatible | Sync |
| Doubao | `doubao-seedream-3-0-t2i-250415`, `doubao-seedream-5-0-260128`, `doubao-seedream-4-5-251128`, `doubao-seedream-4-0-250828`, `doubao-seededit-3-0-i2i-250628` | OpenAI-compatible | Sync |
| Fal.ai | `fal-ai/nano-banana` | Fal.ai native | Async |
| Tencent AIGC | `GEM`, `Qwen`, `Hunyuan` | Native | Async |
| Replicate | `black-forest-labs/flux-kontext-dev`, `black-forest-labs/flux-schnell` | Replicate native | Async |

## Image Object

Represents a generated image URL or content.

| Parameter | Type | Description |
|-----------|------|-------------|
| `b64_json` | string | Base64-encoded JSON if `response_format` is `b64_json` |
| `url` | string | Image URL if `response_format` is `url` (default) |
| `revised_prompt` | string | The revised prompt used for generation if any |

## Upload Requirements by Platform

| Platform / Task | Upload Method | Format / Limit | Notes |
| --- | --- | --- | --- |
| **DALL-E 3 Generate** | None (text only) | — | No upload needed |
| **DALL-E 3 Edit** | Local file (multipart) | PNG; <4MB | Original image + optional mask |
| **GPT Image-1 Generate** | None (text only) | — | No upload needed |
| **GPT Image-1 Edit** | Base64 (inline) | PNG; <4MB | Base64-only; mask must match dimensions |
| **Midjourney Imagine** | None (text only) | — | No upload needed |
| **Midjourney Blend** | URL | Image URL | Upload to image bed first |
| **Midjourney Describe** | URL | Image URL | Upload to image bed first |
| **Midjourney Upload** | Local file | Any image | Auto-uploaded to Discord |
| **FLUX (OpenAI format)** | None or URL | — | For img2img, provide URL |
| **FLUX (Replicate)** | Local file or URL | Any image | Passed in `input.image` |
| **Ideogram Generate** | None (text only) | — | No upload needed |
| **Ideogram Edit/Remix** | URL | Image URL | Upload to image bed first |
| **Grok Image Generate** | None (text only) | — | No upload needed |
| **Grok Image Edit** | URL or Base64 | JPEG, PNG | Check specific endpoint |
| **Qwen Image Generate** | None (text only) | — | No upload needed |
| **Qwen Image Edit** | URL | Image URL | `image` field expects URL |
| **Doubao Image** | Local file or URL | JPEG, PNG; up to 14 reference images | Multi-image supported |
| **Fal.ai** | Local file or URL | Any image | Passed in request body |
| **Tencent AIGC** | Local file or URL | JPEG, PNG | Passed in request body |
| **Replicate** | Local file or URL | Any image | Passed in `input` object |

> **Image Bed**: For platforms requiring URLs, use Lingxi's built-in image bed (`POST` to image bed endpoint, see `lingxi-entry` skill) to upload and get a public URL.

## OpenAI-Compatible Image Generation

**Endpoint**: `POST /v1/images/generations`

**Request**:
- `prompt` (string, required)
- `model` (string, optional): default depends on group
- `n` (number, optional): default 1
- `size` (string, optional): e.g. `1024x1024`
- `quality` (string, optional): `standard` or `hd`
- `response_format` (string, optional): `url` or `b64_json`

**Response**:
- `data[].url` (string)
- `data[].b64_json` (string, if requested)
- `data[].revised_prompt` (string)

### Image Editing (DALL-E / GPT Image-1 / Qwen / Doubao / FLUX)

**Endpoint**: `POST /v1/images/edits`

Requires:
- `image` (file or URL): original image
- `prompt` (string)
- Optional `mask` (file) for inpainting

## Midjourney Native Tasks

Midjourney uses asynchronous task-based API. Full flow:

### 1. Upload Image (optional)
**Endpoint**: `POST /mj/submit/upload-discord-images`
- `base64Array` (array of strings): base64-encoded images

### 2. Submit Imagine
**Endpoint**: `POST /mj/submit/imagine`
- `botType` (string, required): `MID_JOURNEY` or `NIJI_JOURNEY`
- `prompt` (string, required)
- `base64Array` (array, optional): reference images
- `notifyHook` (string, optional): webhook URL
- `state` (string, optional): custom parameter

**Response**:
```json
{
  "code": 1,
  "description": "Submit success",
  "result": "task_id",
  "properties": {
    "discordChannelId": "...",
    "discordInstanceId": "..."
  }
}
```

### 3. Query Task by ID
**Endpoint**: `GET /mj/task/{task_id}/fetch`

**Response fields**:
- `id` (string): task ID
- `action` (string): e.g. `IMAGINE`
- `status` (string): `SUCCESS`, `FAILURE`, `PENDING`, `PROCESSING`, etc.
- `progress` (string): e.g. `0%`, `50%`, `100%`
- `imageUrl` (string): result image URL
- `failReason` (string): error message if failed
- `buttons` (array): available actions
  - `label`: `U1`, `U2`, `U3`, `U4` (Upscale), `V1`, `V2`, `V3`, `V4` (Variation), `🔄` (Reroll)
  - `customId`: action identifier for next step
- `properties.finalPrompt` (string): actual prompt used
- `properties.finalZhPrompt` (string): Chinese prompt if available

### 4. Query Tasks by ID List
**Endpoint**: `POST /mj/task/list-by-condition`
- `ids` (array of strings): task IDs to query
- Returns array of task objects (same schema as single fetch)

### 5. Get Image Seed
**Endpoint**: `GET /mj/task/{id}/image-seed`
- Returns task object with seed information

### 6. Execute Action
**Endpoint**: `POST /mj/submit/action`
- `taskId` (string): original task ID
- `customId` (string): from query response buttons
- `chooseSameChannel` (boolean): use same channel account
- `notifyHook` (string, optional): webhook URL
- `state` (string, optional): custom parameter

**Response**:
```json
{
  "created": 1589478378,
  "data": [
    {"url": "https://..."}
  ]
}
```

### Other Midjourney Tasks

**Blend** (`POST /mj/submit/blend`):
- `base64Array` (array): 2+ images to blend
- `dimensions` (string): `PORTRAIT` (2:3), `SQUARE` (1:1), `LANDSCAPE` (3:2)
- `botType`: `MID_JOURNEY` or `NIJI_JOURNEY`
- `notifyHook` (string, optional)
- `state` (string, optional)

**Describe** (`POST /mj/submit/describe`):
- `base64` (string): base64-encoded image
- `botType`: `MID_JOURNEY` or `NIJI_JOURNEY`
- Returns prompt descriptions of the image

**Modal** (`POST /mj/submit/modal`):
- `taskId` (string): original task ID
- `maskBase64` (string): mask for local repaint
- `prompt` (string): edit prompt

### Midjourney Task States

Typical lifecycle: `PENDING` → `PROCESSING` → `SUCCESS` (or `FAILURE`)

Polling interval: 3-5 seconds. Expose progress updates to user.

## Ideogram

### Ideogram 3.0 (Latest)
**Generate Endpoint**: `POST /ideogram/v1/ideogram-v3/generate`

Sync generation. **Image URLs valid for 24 hours.**

- `prompt` (string, required)
- `seed` (integer, optional): 0-2147483647
- `resolution` (string, optional): many options (512x1536 to 1536x640)
- `aspect_ratio` (string, optional): `1x1`, `16x9`, `9x16`, `3x2`, `2x3`, `4x3`, `3x4`, `5x4`, `4x5`, `10x16`, `16x10`, `1x2`, `2x1`, `1x3`, `3x1`
  - **Cannot use `resolution` and `aspect_ratio` together**
- `rendering_speed` (string, optional): `TURBO`, `DEFAULT`, `QUALITY`
- `magic_prompt` (string, optional): `AUTO`, `ON`, `OFF`
- `negative_prompt` (string, optional)
- `num_images` (integer, optional): 1-8, default 1
- `color_palette` (object, optional): preset `name` or custom `members`
- `style_codes` (array of hex strings, optional): 8-char hex style codes
- `style_type` (string, optional): `AUTO`, `GENERAL`, `REALISTIC`, `DESIGN`

**Response**:
```json
{
  "data": [
    {
      "seed": 511526458,
      "prompt": "...",
      "resolution": "1024x1024",
      "url": "https://...",
      "is_image_safe": true,
      "style_type": "REALISTIC"
    }
  ],
  "created": "2025-08-27T18:23:28.806107195+08:00"
}
```

### Ideogram 3.0 Edit
**Endpoint**: `POST /ideogram/v1/ideogram-v3/edit`
- `image` (file): original image (JPEG, WebP, PNG, max 10MB)
- `mask` (file, optional): mask image
- `prompt` (string)
- `seed` (integer, optional)

### Ideogram 3.0 Remix / Reframe / Replace Background
- Remix: `POST /ideogram/v1/ideogram-v3/remix`
- Reframe: `POST /ideogram/v1/ideogram-v3/reframe`
- Replace Background: `POST /ideogram/v1/ideogram-v3/replace-background`

### Older Ideogram Versions
**Endpoint**: `POST /ideogram/generate`
- Uses `image_request` wrapper object
- `model`: `V_1`, `V_1_TURBO`, `V_2`, `V_2_TURBO`
- `aspect_ratio`: `ASPECT_1_1`, `ASPECT_16_9`, etc.
- `magic_prompt_option`: `AUTO`, `ON`, `OFF`
- `style_type`: `AUTO`, `GENERAL`, `REALISTIC`, `DESIGN`, `RENDER_3D`, `ANIME`

### Key Differences: v3 vs Older
| Feature | v3 | Older (V1/V2) |
|---------|-----|---------------|
| Wrapper | Direct params | `image_request` object |
| Aspect ratio format | `1x1`, `16x9` | `ASPECT_1_1`, `ASPECT_16_9` |
| Model param | N/A (endpoint-specific) | `V_1`, `V_2`, `V_2_TURBO` |
| Rendering speed | `TURBO`/`DEFAULT`/`QUALITY` | Not available |
| Style codes | Supported | Not available |

## Grok Image

**Create Endpoint**: `POST /v1/images/generations`
- `model`: `grok-3-image`
- `prompt` (string, required): max 1000 characters
- `size` (string, optional): `960x960`, `720x1280`, `1280x720`, `1168x784`, `784x1168`

**Response**:
```json
{
  "created": 1773127037,
  "data": [
    {"url": "https://..."}
  ],
  "usage": {
    "generated_images": 1,
    "output_tokens": 16384,
    "total_tokens": 16384
  }
}
```

**Edit Endpoint**: `POST /v1/images/edits`
- `model`: `grok-3-image`
- `image` (file): image to edit (1 image supported)
- `prompt` (string): edit prompt
- `aspect_ratio` (string, optional): `1:1`, `3:4`, `4:3`, `9:16`, `16:9`, `2:3`, `3:2`, `9:19.5`, `19.5:9`, `9:20`, `20:9`, `1:2`, `2:1`, `auto`
- `response_format` (string, optional): `b64_json` or `url`
- `resolution` (string, optional): `1k`, `2k`
- `quality` (string, optional): `low`, `medium`, `high`
- `n` (integer, optional): 1-10, default 1

## DALL-E 3

**Endpoint**: `POST /v1/images/generations`
- `model`: `dall-e-3`
- `size`: `1024x1024`, `1792x1024`, `1024x1792`
- `quality`: `standard` or `hd`
- `style`: `vivid` or `natural`
- `n`: 1 (DALL-E 3 only supports 1 image per request)

**Image Edit (DALL-E 2 only)**:
- `POST /v1/images/edits`
- `model`: `dall-e-2`
- `image`: < 4MB, square PNG
- `mask`: < 4MB, square PNG, same dimensions as image
- `size`: `256x256`, `512x512`, `1024x1024`
- `n`: 1-10

## FLUX

### OpenAI-Compatible Format
**Endpoint**: `POST /v1/images/generations`
- `model`: `flux-kontext-pro`, `flux-kontext-max`, `flux-schnell`, etc.
- `prompt` (string, required)
- `aspect_ratio` (string, required): `21:9`, `16:9`, `4:3`, `3:2`, `1:1`, `2:3`, `3:4`, `9:16`, `9:21`
- `n` (integer, optional)

### OpenAI-Compatible Edit Format
**Endpoint**: `POST /v1/images/edits`
- `model`: `flux-kontext-pro`, `flux-kontext-max`, `gpt-image-1`, `gpt-image-1-all`
- `image` (file or array): original image(s)
- `prompt` (string, required)
- `mask` (file, optional): PNG with transparent areas
- `aspect_ratio` (string, optional): `21:9`, `16:9`, `4:3`, `3:2`, `1:1`, `2:3`, `3:4`, `9:16`, `9:21`
- `n` (integer, optional): 1-10
- `quality` (string, optional): `high`, `medium`, `low`
- `response_format` (string, optional): `url` or `b64_json`

### Replicate Native Format

Replace `https://api.replicate.com` with `{{BASE_URL}}/replicate`. Input, output, and request methods are consistent with the official API.

**Create Task (Path way)**: `POST /replicate/v1/models/{model_owner}/{model_name}/predictions`
- Example: `/replicate/v1/models/black-forest-labs/flux-kontext-dev/predictions`
- `input` (object):
  - `prompt` (string, required)
  - `input_image` (string, optional): URL of reference image
  - `go_fast` (boolean, optional): faster inference, default true
  - `guidance` (number, optional): 0-10, default 2.5
  - `aspect_ratio` (string, optional): default `match_input_image`
  - `output_format` (string, optional): `webp`, `jpg`, `png`
  - `output_quality` (integer, optional): 0-100, default 80
  - `num_inference_steps` (integer, optional): 4-50, default 28

**Create Task (Version way)**: `POST /replicate/v1/predictions`
- `version` (string): model version hash
- `input` (object): same as above

**Query Task**: `GET /replicate/v1/predictions/{prediction_id}`

**Response fields**:
- `id` (string): prediction ID
- `status` (string): `starting`, `processing`, `succeeded`, `failed`, `canceled`
- `output` (string or array): result URL(s) when completed
- `error` (string): error message if failed
- `urls.get` (string): polling URL
- `metrics.predict_time` (number): inference duration
- `data_removed` (boolean)

**Important**: Resource links are valid for only 1 hour.

### FLUX Resolution Guide
FLUX supports flexible resolutions. When using OpenAI-compatible format, specify `aspect_ratio`. When using Replicate native format, use `aspect_ratio: match_input_image` to preserve input dimensions, or specify explicit ratios. Common output sizes depend on the specific model version.

## Doubao (豆包)

**Endpoint**: `POST /v1/images/generations`

Supported models:
- Text-to-image: `doubao-seedream-3-0-t2i-250415`, `doubao-seedream-5-0-260128`, `doubao-seedream-4-5-251128`, `doubao-seedream-4-0-250828`
- Image editing: `doubao-seededit-3-0-i2i-250628`

- `prompt` (string, required)
- `image` (string or array, optional): URL or base64 (`data:image/png;base64,...`) for image-to-image
  - seedream-5.0/4.5/4.0 support up to 14 reference images
- `size` (string, optional): varies by model
  - seedream-3.0: `1024x1024` and other 1K sizes
  - seedream-5.0/4.5/4.0: `2K`, `3K`, `4K` or explicit pixel values
  - seededit-3.0: `adaptive` (matches input aspect ratio)
- `seed` (integer, optional): -1 to 2147483647
- `guidance_scale` (number, optional): text weight, 1-10
  - seedream-3.0 default: 2.5
  - seededit-3.0 default: 5.5
- `watermark` (boolean, optional): default true
- `response_format` (string, optional): `url` or `b64_json`
- `sequential_image_generation` (string, optional): `auto` or `disabled` (seedream-5.0/4.5/4.0)
- `output_format` (string, optional): `png` or `jpeg` (seedream-5.0 only)

## Fal.ai Platform

Fal.ai uses fully asynchronous queue-based API.

**Create Task**: `POST /fal-ai/{model_path}`
- Example models: `fal-ai/nano-banana`, `fal-ai/flux-1/dev`
- `prompt` (string, required)
- `num_images` (integer, optional): 1-4, default 1

**Edit Task**: `POST /fal-ai/{model_path}/edit`
- Example: `/fal-ai/nano-banana/edit`
- `prompt` (string, required)
- `image_urls` (array of strings): URLs of images to edit
- `num_images` (integer, optional): 1-4, default 1

**Response** (immediate):
```json
{
  "status": "IN_QUEUE",
  "request_id": "e7e9202c-efb8-40f2-81c3-13b3f7aaa4ca",
  "response_url": "https://queue.fal.run/fal-ai/nano-banana/requests/...",
  "status_url": "https://queue.fal.run/fal-ai/nano-banana/requests/.../status",
  "cancel_url": "https://queue.fal.run/fal-ai/nano-banana/requests/.../cancel",
  "logs": null,
  "metrics": {},
  "queue_position": 0
}
```

**Query Results**: `GET /fal-ai/{model_name}/requests/{request_id}`

**Response** (when completed):
```json
{
  "seed": 2841475369,
  "images": [
    {
      "url": "https://...",
      "width": 1024,
      "height": 1024,
      "content_type": "image/jpeg"
    }
  ],
  "prompt": "...",
  "has_nsfw_concepts": [false]
}
```

### Fal.ai Status Codes
- `IN_QUEUE`: waiting in queue
- `IN_PROGRESS`: actively generating
- `COMPLETED`: generation finished
- `FAILED`: generation failed

## Tencent AIGC

**Create Task**: `POST /tencent-vod/v1/aigc-image`
- `model_name` (string, required): `GEM`, `Qwen`, `Hunyuan`
- `model_version` (string, required): GEM (`2.5`, `3.0`), Qwen (`0925`), Hunyuan (`3.0`)
- `prompt` (string, required)
- `negative_prompt` (string, optional)
- `enhance_prompt` (string, optional): `Enabled` or `Disabled`
- `file_infos` (array, optional): reference images with `type` (`File`/`Url`), `file_id` or `url`, `text`
- `output_config` (object):
  - `storage_mode` (string): `Permanent` or `Temporary`
  - `resolution` (string): `720P`, `1080P`, `2K`, `4K`, `1024x1024`, `2048x2048`, `2304x1728`, `2496x1664`, `2560x1440`, `3024x1296`, `4096x4096`, `4694x3520`, `4992x3328`, `5404x3040`, `6198x2656`
  - `aspect_ratio` (string): `1:1`, `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`
  - `person_generation` (string): `AllowAdult` or `Disallowed`
  - `input_compliance_check` (string): `Enabled` or `Disabled`
  - `output_compliance_check` (string): `Enabled` or `Disabled`
- `session_id` (string, optional): deduplication ID (max 50 chars)
- `session_context` (string, optional): pass-through context (max 1000 chars)
- `tasks_priority` (string, optional): -10 to 10

**Response**:
```json
{
  "Response": {
    "TaskId": "...",
    "RequestId": "..."
  }
}
```

**Query Results**: `GET /tencent-vod/v1/query/{task_id}`

**Response**:
```json
{
  "Response": {
    "Status": "FINISH",
    "TaskType": "AigcImageTask",
    "RequestId": "...",
    "CreateTime": "2025-12-29T12:03:30Z",
    "FinishTime": "2025-12-29T12:03:43Z",
    "AigcImageTask": {
      "Status": "FINISH",
      "TaskId": "...",
      "Progress": 100,
      "Input": { ... },
      "Output": {
        "FileInfos": [
          {
            "FileUrl": "http://...",
            "ExpireTime": "2026-01-05T12:03:57Z",
            "StorageMode": "Temporary"
          }
        ]
      }
    }
  }
}
```

### Tencent AIGC Status Values
- `FINISH`: task completed
- `PROCESSING`: task in progress

## Qwen Image

### qwen-image-max / z-image-turbo
**Endpoint**: `POST /v1/images/generations`
- `model`: `qwen-image-max` or `z-image-turbo`
- `prompt` (string, required)
- `size` (string, required): e.g. `1328x1328` for qwen-image-max, `1280x720` for z-image-turbo
- `n` (integer, required): only 1 supported
- `watermark` (boolean, required): true/false
- `prompt_extend` (boolean, required): AI prompt optimization, default true

**Response**:
- `data[].url` (string)
- `data[].b64_json` (string, optional)

### qwen-image-edit-2509
**Endpoint**: `POST /v1/images/generations`
- `model`: `qwen-image-edit-2509`
- `prompt` (string, required)
- `image` (string, required): image URL

**Response**:
- `data[].url` (string)
- `usage` (object): token counts (`prompt_tokens`, `completion_tokens`, `total_tokens`)

## GPT Image-1

### Create
**Endpoint**: `POST /v1/images/generations`
- `model`: `gpt-image-1`, `gpt-image-1.5`, `gpt-image-2`, `gpt-image-2-all`
- `prompt` (string, required)
- `n` (integer, required): 1-10
- `size` (string, required): `1024x1024`, `1536x1024` (landscape), `1024x1536` (portrait), `auto`

For `gpt-image-2`, additional sizes: `2048x2048` (2K square), `2048x1152` (2K landscape), `3840x2160` (4K landscape), `2160x3840` (4K portrait)

For `gpt-image-2`, additional params:
- `format` (string, optional): `png`, `jpeg`, `webp`
- `quality` (string, optional): `low`, `medium`, `high`, `auto` (default)

### Edit
**Endpoint**: `POST /v1/images/edits`
- `model`: `gpt-image-1`, `gpt-image-1-all`, `gpt-image-1.5`, `gpt-image-2`, `gpt-image-2-all`, `flux-kontext-pro`, `flux-kontext-max`
- `image` (file or array, required): original image(s)
  - gpt-image-1: < 25MB, png/webp/jpg
  - dall-e-2: < 4MB, square png only
- `prompt` (string, required): max 32000 chars for gpt-image-1, 1000 for dall-e-2
- `mask` (file, optional): PNG with transparent areas marking edit region
  - Must be valid PNG, < 4MB, same dimensions as image
- `n` (integer, optional): 1-10
- `quality` (string, optional): `high`, `medium`, `low` (gpt-image-1 only)
- `size` (string, optional): `1024x1024`, `1536x1024`, `1024x1536`, `auto`
- `background` (string, optional): `transparent`, `opaque`, `auto` (gpt-image-1 only)
- `moderation` (string, optional): `low` or `auto` (gpt-image-1 only)

**Important**: gpt-image-1 always returns base64 encoded images. Do NOT use `response_format: url` with gpt-image-1.

## Upload Methods by Platform

| Platform | Upload Method | Notes |
|----------|--------------|-------|
| Midjourney | Base64 array | `base64Array` in JSON |
| Ideogram v3 Edit/Remix/Reframe/Replace Background | File upload | multipart/form-data, max 10MB, JPEG/WebP/PNG |
| Ideogram older | Base64 or URL | Via `image_request` |
| DALL-E 3 | File upload | multipart/form-data |
| GPT Image-1 | File upload | < 25MB png/webp/jpg |
| FLUX Replicate | URL | `input_image` as HTTPS URL |
| Doubao | URL or Base64 | `data:image/png;base64,...` format |
| Fal.ai | URL | `image_urls` array |
| Tencent AIGC | File ID or URL | `file_infos` with `File` or `Url` type |
| Qwen Edit | URL | `image` field as URL |

## Quick Start (Python)

### OpenAI-compatible (DALL-E / FLUX / Qwen / Doubao)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LINGXI_API_KEY"),
    base_url=os.getenv("LINGXI_BASE_URL"),
)

response = client.images.generate(
    model="dall-e-3",
    prompt="A futuristic city at sunset, cyberpunk style",
    size="1024x1024",
    n=1,
)
print(response.data[0].url)
```

### Image Edit (DALL-E / GPT Image-1)

```python
response = client.images.edit(
    image=open("original.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="Add a rainbow in the sky",
    model="gpt-image-1",
    size="1024x1024",
)
# gpt-image-1 returns base64
image_base64 = response.data[0].b64_json
import base64
image_bytes = base64.b64decode(image_base64)
with open("output.png", "wb") as f:
    f.write(image_bytes)
```

### GPT Image-1

```python
response = client.images.generate(
    model="gpt-image-1",
    prompt="A hand-drawn cat wearing a wizard hat",
    size="1024x1024",
    n=1,
)
```

### Grok Image

```python
response = client.images.generate(
    model="grok-3-image",
    prompt="A cat",
    size="960x960",
)
print(response.data[0].url)
```

### Midjourney Async Flow

```python
import requests
import time

base_url = os.getenv("LINGXI_BASE_URL")
headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

# 1. Submit imagine
resp = requests.post(f"{base_url}/mj/submit/imagine", headers=headers, json={
    "botType": "MID_JOURNEY",
    "prompt": "A serene Japanese garden with cherry blossoms",
})
task_id = resp.json()["result"]

# 2. Poll until complete
while True:
    status = requests.get(f"{base_url}/mj/task/{task_id}/fetch", headers=headers).json()
    print(f"Status: {status['status']}, Progress: {status.get('progress', '0%')}")
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

base_url = os.getenv("LINGXI_BASE_URL")
headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

# 1. Create prediction
resp = requests.post(
    f"{base_url}/replicate/v1/models/black-forest-labs/flux-kontext-dev/predictions",
    headers=headers,
    json={"input": {"prompt": "A beautiful landscape", "go_fast": True}},
)
prediction_id = resp.json()["id"]

# 2. Poll
while True:
    status = requests.get(f"{base_url}/replicate/v1/predictions/{prediction_id}", headers=headers).json()
    print(f"Status: {status['status']}")
    if status["status"] == "succeeded":
        print("Output:", status["output"])
        break
    elif status["status"] in ("failed", "canceled"):
        print("Error:", status.get("error"))
        break
    time.sleep(5)
```

### Fal.ai Async Flow

```python
import requests
import time

base_url = os.getenv("LINGXI_BASE_URL")
headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

# 1. Submit
resp = requests.post(f"{base_url}/fal-ai/nano-banana", headers=headers, json={
    "prompt": "A cute cat",
    "num_images": 1,
})
request_id = resp.json()["request_id"]

# 2. Poll via requests endpoint
while True:
    result = requests.get(
        f"{base_url}/fal-ai/nano-banana/requests/{request_id}",
        headers=headers,
    ).json()
    if "images" in result:
        print("Image URL:", result["images"][0]["url"])
        break
    time.sleep(5)
```

### Tencent AIGC Async Flow

```python
import requests
import time

base_url = os.getenv("LINGXI_BASE_URL")
headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

# 1. Create task
resp = requests.post(f"{base_url}/tencent-vod/v1/aigc-image", headers=headers, json={
    "model_name": "GEM",
    "model_version": "3.0",
    "prompt": "convert this image to anime style",
    "enhance_prompt": "Enabled",
    "output_config": {
        "storage_mode": "Temporary",
        "resolution": "1080P",
        "aspect_ratio": "1:1",
        "person_generation": "AllowAdult",
    },
})
task_id = resp.json()["Response"]["TaskId"]

# 2. Poll
while True:
    result = requests.get(f"{base_url}/tencent-vod/v1/query/{task_id}", headers=headers).json()
    task = result["Response"]["AigcImageTask"]
    print(f"Status: {task['Status']}, Progress: {task.get('Progress', 0)}%")
    if task["Status"] == "FINISH":
        urls = [f["FileUrl"] for f in task["Output"]["FileInfos"]]
        print("URLs:", urls)
        break
    time.sleep(5)
```

### PHP Example (Image Edit)

```php
<?php
require_once 'vendor/autoload.php';
use GuzzleHttp\Client;

$model = "flux-kontext-max";
$queue = ['prompt' => '改成蓝色'];
$correctedImg = '场景1.png';

$client = new Client();
$multipart = [
    ['name' => 'model', 'contents' => $model],
    ['name' => 'prompt', 'contents' => $queue['prompt']],
    ['name' => 'n', 'contents' => '1'],
    ['name' => 'size', 'contents' => '1024x1024'],
    ['name' => 'response_format', 'contents' => 'b64_json'],
];

if ($correctedImg !== false && file_exists($correctedImg)) {
    $multipart[] = [
        'name' => 'image',
        'contents' => fopen($correctedImg, 'r'),
        'filename' => basename($correctedImg),
        'headers' => ['Content-Type' => 'image/png']
    ];
}

$response = $client->request('POST', 'https://api.aicso.top/v1/images/edits', [
    'headers' => [
        'Authorization' => 'Bearer sk-your-key',
        'Accept' => 'application/json'
    ],
    'multipart' => $multipart,
    'timeout' => 60,
]);

$responseData = json_decode($response->getBody()->getContents(), true);
if (isset($responseData['data'][0]['url'])) {
    echo "Image URL: " . $responseData['data'][0]['url'] . "\n";
}
?>
```

## Operational Guidance

- Image generation is often asynchronous; expose progress and allow cancel/retry.
- Cache results by (prompt, model, size, seed) to avoid redundant costs.
- Store image assets in object storage and persist only URLs in metadata.
- For Midjourney, task polling is required; typical states: `PENDING` → `PROCESSING` → `SUCCESS`.
- For FLUX on Replicate, polling interval: 5-10 seconds. Resource links valid for 1 hour.
- For Fal.ai, poll by `request_id` via `/fal-ai/{model}/requests/{request_id}`.
- For Tencent AIGC, check `Response.AigcImageTask.Status` and `Progress` fields.
- Ideogram and GPT Image-1 image URLs expire (24 hours for Ideogram, 60 minutes for DALL-E URLs); download promptly.
- When using masks for editing, ensure exact dimension match with the original image.

## Size Notes

- DALL-E 3: `1024x1024`, `1792x1024`, `1024x1792`
- DALL-E 2: `256x256`, `512x512`, `1024x1024`
- GPT Image-1: `1024x1024`, `1536x1024` (landscape), `1024x1536` (portrait), `auto`
- GPT Image-2: `1024x1024`, `1536x1024`, `1024x1536`, `2048x2048`, `2048x1152`, `3840x2160`, `2160x3840`, `auto`
- FLUX: flexible via `aspect_ratio`; common ratios: `1:1`, `16:9`, `9:16`, `3:2`, `2:3`, `4:3`, `3:4`, `21:9`, `9:21`
- Ideogram v3: extensive resolution list or aspect_ratio; cannot use both together
- Grok Image: `960x960`, `720x1280`, `1280x720`, `1168x784`, `784x1168`
- Doubao seedream-3.0: up to `2048x2048`; seedream-5.0/4.5/4.0: up to 4K
- Qwen image-max: `1328x1328` and other sizes
- z-image-turbo: `1280x720` and other sizes

## Anti-patterns

- Do not invent model names; use exact IDs from Lingxi model list.
- Do not block the UI without progress updates for async tasks.
- Do not retry blindly on 4xx (e.g., invalid size).
- Do not use `response_format: url` with gpt-image-1; it always returns base64.
- Do not mix `resolution` and `aspect_ratio` in Ideogram v3.
- Do not exceed file size limits: gpt-image-1 < 25MB, dall-e-2 < 4MB, Ideogram edit < 10MB.

## Workflow

1) Confirm user intent, target model/platform, and output format.
2) Run one minimal generation first to verify connectivity and group permissions.
3) Execute the target operation with explicit parameters.
4) For async tasks, poll with appropriate intervals and expose progress.
5) Verify results and save output/evidence files.

## References

- Lingxi API Docs Portal: https://aicso.apifox.cn/
- Midjourney Docs: https://docs.midjourney.com/
- Ideogram API Docs: https://developer.ideogram.ai/api-reference/api-reference/
- OpenAI Image API: https://platform.openai.com/docs/api-reference/images
- Replicate Docs: https://replicate.com/docs
- Fal.ai Docs: https://fal.ai/docs
- Tencent AIGC Docs: https://cloud.tencent.com/document/product/266/126240
- Doubao Docs: https://www.volcengine.com/docs/82379/1541523
- Source list: `references/sources.md`
