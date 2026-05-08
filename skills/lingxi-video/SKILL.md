---
name: lingxi-video
description: Use when generating or editing videos through Lingxi API Gateway, including Veo, Luma, Runway, MiniMax (海螺), Sora, Grok, Tongyi Wanxiang, Tencent AIGC, Doubao, Kling (可灵), Replicate, Fal.ai, and Vidu.
version: 1.2.0
---

Category: provider

# Lingxi Video

## Validation

```bash
mkdir -p output/lingxi-video
python -m py_compile skills/lingxi-video/scripts/video_demo.py && echo "py_compile_ok" > output/lingxi-video/validate.txt
```

Pass criteria: command exits 0 and `output/lingxi-video/validate.txt` is generated.

## Output And Evidence

- Save task IDs, polling responses, and final video URLs to `output/lingxi-video/`.
- Keep one end-to-end run log for troubleshooting.

## Prerequisites

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install openai requests
```

- Set `LINGXI_API_KEY` and `LINGXI_BASE_URL` in environment.

## Upload Requirements by Platform

| Platform / Task | Upload Method | Format / Limit | Reference Images |
| --- | --- | --- | --- |
| **Veo Text-to-Video** | None (text only) | — | 0 |
| **Veo Image-to-Video** | Local file or URL | JPEG, PNG; <10MB | 1 (first frame) |
| **Veo Reference Image** | Local file or URL | JPEG, PNG; <10MB | 1 (style reference) |
| **Luma Text-to-Video** | None (text only) | — | 0 |
| **Luma Image-to-Video** | Local file or URL | JPEG, PNG | 1 (first frame) |
| **Luma Extend** | None (uses existing video) | — | 0 (extends existing) |
| **Runway Image-to-Video** | Local file or URL | JPEG, PNG | 1 (first frame) |
| **MiniMax Text-to-Video** | None (text only) | — | 0 |
| **MiniMax Image-to-Video** | Local file or URL | JPEG, PNG | 1 (first frame) |
| **MiniMax Keyframe** | Local file or URL | JPEG, PNG | 2 (first + last frame) |
| **Sora Text-to-Video** | None (text only) | — | 0 |
| **Sora Image-to-Video** | Local file or URL | JPEG, PNG | 1 (first frame) |
| **Sora Character** | Video file | MP4, MOV | 1 video (character source) |
| **Grok Text-to-Video** | None (text only) | — | 0 |
| **Grok Image-to-Video** | Local file or URL | JPEG, PNG | 1 (first frame) |
| **Kling Text-to-Video** | None (text only) | — | 0 |
| **Kling Image-to-Video** | Local file or URL | JPEG, PNG | 1 (first frame) |
| **Kling Multi-Image Reference** | Local file or URL | JPEG, PNG | 1-9 (character/style refs) |
| **Kling Keyframe** | Local file or URL | JPEG, PNG | 2 (first + last frame) |
| **Vidu Text-to-Video** | None (text only) | — | 0 |
| **Vidu Image-to-Video** | Local file or URL | JPEG, PNG | 1 (first frame) |
| **Vidu Reference-to-Video** | Local file or URL | JPEG, PNG | 1 (character reference) |
| **Vidu Start-End-to-Video** | Local file or URL | JPEG, PNG | 2 (first + last frame) |
| **Doubao Text-to-Video** | None (text only) | — | 0 |
| **Doubao Image-to-Video** | Local file or URL | JPEG, PNG | 1 (first frame) |
| **Doubao Keyframe** | Local file or URL | JPEG, PNG | 2 (first + last frame) |
| **Replicate** | Local file or URL | Any image/video | Per model |
| **Fal.ai** | Local file or URL | Any image/video | Per model |
| **Tencent AIGC** | Local file or URL | JPEG, PNG | Per template |

> **Tip**: For platforms requiring URLs, upload your image/video to the Lingxi image bed first to get a public URL. For keyframe tasks, prepare exactly 2 images (first and last frame). For multi-image reference tasks, prepare 1-9 images.

## Supported Platforms

| Platform | Capabilities | Format |
|----------|-------------|--------|
| Veo | text-to-video, image-to-video, reference-image | Unified / OpenAI |
| Luma | text-to-video, image-to-video, extend | Native |
| Runway | image-to-video | Native |
| MiniMax (海螺) | text-to-video, image-to-video, keyframe | Native |
| Sora | text-to-video, image-to-video, character, remix | Unified / Chat / OpenAI |
| Grok | text-to-video, image-to-video, extend | Unified / OpenAI |
| Tongyi Wanxiang | image-to-video, audio-driven | Native |
| Tencent AIGC | video generation, effects, multi-model proxy | Native |
| Doubao | text-to-video, image-to-video, seedance, reference-video | Native / Official |
| Kling | text-to-video, image-to-video, omni, editing, effects, image gen, audio, digital human, lip sync, motion control, subject | Native |
| Replicate | various video models | Replicate native |
| Fal.ai | veo3, kling video | Fal.ai native |
| Vidu (Official) | text-to-video, image-to-video, reference-to-video, start-end-to-video, audio | Native |

---

## Veo Platform

Veo supports two request formats: **Unified Video Format** and **OpenAI Video Format**.

### Veo Unified Format

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create video (text / image / reference) | `/v1/video/create` | POST |
| Query task | `/v1/video/query?id={id}` | GET |

**Request (POST /v1/video/create)**:
- `model` (string, required): one of
  - `veo2`, `veo2-fast`, `veo2-fast-frames`, `veo2-fast-components`, `veo2-pro`, `veo2-pro-components`
  - `veo3`, `veo3-fast`, `veo3-fast-frames`, `veo3-frames`, `veo3-pro`, `veo3-pro-frames`
  - `veo3.1`, `veo3.1-fast`, `veo3.1-pro`, `veo3.1-4k`, `veo3.1-pro-4k`
- `prompt` (string, required)
- `images` (array of string, optional): image URLs. Behavior depends on model suffix:
  - `-frames` models: up to 2 images (first + last frame)
  - `-components` models: up to 3 images (elements in video)
  - `veo3-pro-frames`: up to 1 first frame
- `enhance_prompt` (boolean): auto-translate Chinese prompt to English
- `enable_upsample` (boolean): enable super-resolution
- `aspect_ratio` (string, veo3 only): `"16:9"` or `"9:16"`

**Response**: returns `id` (task ID) and `status`

**Query (GET /v1/video/query?id={id})**:
- Returns `status`, `video_url`, `enhanced_prompt`, `upsample_video_url`, etc.

### Veo OpenAI Format

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create video | `/v1/videos` | POST (multipart/form-data) |
| Query task | `/v1/videos/{id}` | GET |
| Download video | `/v1/videos/{id}/content` | GET |

**Request (POST /v1/videos)**:
- `model` (string): currently `veo_3_1` or `veo_3_1-fast`
- `prompt` (string)
- `seconds` (string): duration
- `input_reference` (file): image reference
- `size` (string): `720x1280` (portrait) or `1280x720` (landscape), or `16x9`
- `watermark` (string): `"false"`

**Response**: returns `id`, `status` (`queued`), `progress`, `created_at`

### Veo Status Codes

| Status | Meaning |
|--------|---------|
| `pending` | Task queued |
| `image_downloading` | Downloading reference images |
| `video_generating` | Video generation in progress |
| `video_generation_completed` | Generation done, may continue upsampling |
| `video_generation_failed` | Generation failed |
| `video_upsampling` | Super-resolution in progress |
| `video_upsampling_completed` | Upsampling completed |
| `video_upsampling_failed` | Upsampling failed |
| `completed` | Fully completed |
| `failed` | Task failed |
| `error` | Error response |

---

## Luma Platform

Native Luma endpoints via Lingxi proxy.

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Submit generation | `/luma/generations` | POST |
| Extend video | `/luma/generations/{task_id}/extend` | POST |
| Query single task | `/luma/generations/{task_id}` | GET |
| Batch get tasks | `/luma/tasks` | POST |

**Request (POST /luma/generations)**:
- `user_prompt` (string, required)
- `model_name` (string): `ray-v1` or `ray-v2`
- `duration` (string): `"5s"` only
- `resolution` (string): `"720p"` or `"1080p"`
- `image_url` (string, optional): reference image
- `image_end_url` (string, optional): end keyframe
- `expand_prompt` (boolean): prompt optimization
- `loop` (boolean): loop reference image
- `notify_hook` (string): callback URL

**Response**: returns `task_id`, `task_status`, `created_at`, `updated_at`

**Query (GET /luma/generations/{task_id})**:
- Returns `state`, `video` (`url`, `download_url`, `width`, `height`), `thumbnail`, `last_frame`, etc.

### Luma Status Codes

| Status | Meaning |
|--------|---------|
| `queued` | Queued |
| `pending` | Waiting |
| `processing` | Processing |
| `completed` | Completed |
| `failed` | Failed |
| `error` | Error response |

---

## Runway Platform

Native Runway endpoints via Lingxi proxy.

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Submit image-to-video | `/runwayml/v1/image_to_video` | POST |
| Query task | `/runwayml/v1/tasks/{task_id}` | GET |

**Request (POST /runwayml/v1/image_to_video)**:
- `promptImage` (string, required): HTTPS URL or data URI
- `model` (string, required): `"gen4_turbo"` or `"gen3a_turbo"`
- `ratio` (string, required): resolution format `"width:height"`
- `promptText` (string, optional): max 1000 chars
- `duration` (integer, optional): `5` or `10` (default 10)
- `seed` (integer, optional): 0-4294967295

**Response**: returns `task_id`, `task_status`

### Runway Status Codes

Uses unified task status:
- `submitted` — task submitted
- `error` — error
- `failed` — failed

---

## MiniMax (海螺) Platform

Native MiniMax endpoints via Lingxi proxy.

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Submit generation (text / image / keyframe) | `/minimax/v1/video_generation` | POST |
| Query task | `/minimax/v1/query/video_generation?task_id={task_id}` | GET |

**Request (POST /minimax/v1/video_generation)**:
- `model` (string, required): `"MiniMax-Hailuo-02"`
- `prompt` (string, required)
- `duration` (integer): `6` or `10`
- `first_frame_image` (string, optional): image URL for image-to-video
- `last_frame_image` (string, optional): for first+last frame video
- `resolution` (string, optional): e.g. `"768P"`
- `prompt_optimizer` (boolean, optional)

**Response**: returns `task_id` in `base_resp`

**Query (GET /minimax/v1/query/video_generation)**:
- Returns `task_id`, `status`, `progress`, `fail_reason`, `data.file.download_url`, `data.file.backup_download_url`

### MiniMax Status Codes

| Status | Meaning |
|--------|---------|
| `Waiting` | Waiting |
| `Running` | Running |
| `Success` | Success |
| `Failed` | Failed |
| `Cancelled` | Cancelled |

---

## Doubao Platform

Native Doubao (Volcengine) endpoints via Lingxi proxy. Two API versions exist.

### Seedance / Doubao v1

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create task | `/volc/v1/contents/generations/tasks` | POST |
| Query single task | `/volc/v1/contents/generations/tasks/{task_id}` | GET |
| List tasks | `/volc/v1/contents/generations/tasks` | GET |
| List tasks (filter by IDs) | `/volc/v1/contents/generations/tasks?filter.task_ids=...` | GET |

**Models**:
- `doubao-seedance-1-5-pro-251215` — text, first-frame, first+last-frame
- `doubao-seedance-1-0-pro-250528` — text, first-frame, first+last-frame
- `doubao-seedance-1-0-pro-fast-251015` — text, first-frame
- `doubao-seedance-1-0-lite-t2v-250428` — text only
- `doubao-seedance-1-0-lite-i2v-250428` — first-frame, first+last-frame, reference (1-4 images)

**Request (POST /volc/v1/contents/generations/tasks)**:
- `model` (string, required)
- `content` (array): items with `type` (`text` | `image_url`), `text`, `image_url.url`, `role` (`reference_image` | `first_frame` | `last_frame`)
- Parameters appended via `--` in prompt text:
  - `--resolution 480p/720p/1080p`
  - `--ratio 16:9/4:3/1:1/3:4/9:16/21:9`
  - `--duration 2-12` (seedance 1.5 pro: 4-12)
  - `--camera_fixed true/false`
  - `--watermark true/false`
  - `--seed {integer}`
- `generate_audio` (boolean): only for seedance 1.5 pro

**Response**: returns `id` (task ID, e.g. `cgt-20250918165243-bfpzb`), `status` (`submitted`)

### Doubao 2.0

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create task | `/api/v3/contents/generations/tasks` | POST |
| Query single task | `/api/v3/contents/generations/tasks/{id}` | GET |
| List tasks | `/api/v3/contents/generations/tasks` | GET |

**Model**: `doubao-seedance-2-0-260128`

**Request**: supports `text`, `image_url` (role: `reference_image`), `video_url` (role: `reference_video`), `audio_url` (role: `reference_audio`), plus `generate_audio`, `ratio`, `duration`, `watermark`.

---

## Sora Platform

Sora supports **three** request formats: Unified, Chat, and OpenAI official.

### Sora Unified Format

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create video | `/v1/video/create` | POST |
| Query task | `/v1/video/query?id={id}` | GET |
| Create character | `/sora/v1/characters` | POST |

**Models**: `sora-2`, `sora-2-all`, `sora-2-pro`

**Request (POST /v1/video/create)**:
- `model` (string, required)
- `prompt` (string, required)
- `orientation` (string): `portrait` or `landscape`
- `size` (string): `small` (~720p) or `large` (1080p)
- `duration` (integer): `10` for sora-2, `15` or `25` for sora-2-pro
- `watermark` (boolean/string): `false` forces no watermark
- `private` (boolean): `true` hides video and disables remix
- `images` (array): image URLs for image-to-video
- `character_url` (string): video URL for character creation
- `character_timestamps` (string): e.g. `"1,3"` (range 1-3 seconds)

**Character creation (POST /sora/v1/characters)**:
- `url` (string): video containing character
- `timestamps` (string): time range in seconds
- `from_task` (string): use existing task ID instead of URL

**Response**: returns `id` (prefixed like `sora-2:task_...`), `status` (`pending`)

### Sora Chat Format

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create video (streaming) | `/v1/chat/completions` | POST |

**Request**: Standard OpenAI chat completion schema with `model: sora-2` or `sora-2-pro`.
- For image-to-video, include `image_url` in message content array.
- Supports continuous modification via multi-turn chat.
- `stream: true` returns SSE progress updates.

### Sora OpenAI Official Format

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create video | `/v1/videos` | POST (multipart/form-data) |
| Create character from video | `/v1/videos/characters` | POST (multipart/form-data) |
| Edit video (remix) | `/v1/videos/{id}/remix` | POST |
| Query task | `/v1/videos/{id}` | GET |
| Download video | `/v1/videos/{id}/content` | GET |

**Request (POST /v1/videos)**:
- `model` (string): `sora-2` or `sora-2-pro`
- `prompt` (string)
- `seconds` (string): `4`, `8`, `12` (default 4)
- `size` (string): `720x1280`, `1280x720`, `1024x1792`, `1792x1024`
- `input_reference` (file): optional image reference
- `watermark` (string): `"false"`
- `private` (string): `"false"`
- `style` (string): `thanksgiving`, `comic`, `news`, `selfie`, `nostalgic`, `anime`

**Response**: returns `id`, `status` (`queued`), `progress`, `created_at`

---

## Grok Platform

Grok supports Unified and OpenAI formats.

### Grok Unified Format

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create video | `/v1/video/create` | POST |
| Query task | `/v1/video/query?id={id}` | GET |
| Extend video | `/v1/video/extend` | POST |

**Model**: `grok-video-3`

**Request (POST /v1/video/create)**:
- `model` (string, required): `grok-video-3`
- `prompt` (string, required)
- `aspect_ratio` (string): `2:3`, `3:2`, `1:1`
- `size` (string): `720P` or `1080P` (currently only `720P`)
- `images` (array): image URLs; video size follows image dimensions

**Extend (POST /v1/video/extend)**:
- `model`, `prompt`, `task_id`, `start_time`, `aspect_ratio`, `size`, `upscale`

### Grok OpenAI Format

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create video | `/v1/videos` | POST (multipart/form-data) |
| Query task | `/v1/video/query?id={id}` | GET |

**Model**: `grok-videos`

**Request**:
- `model`, `prompt`, `seconds` (`6` or `10`), `input_reference` (image URL), `size` (`16:9` or `9:16`)

### Grok Status Codes

Same as Veo unified format: `pending`, `processing`, `completed`, `failed`, `error`.

---

## Tongyi Wanxiang Platform

Native Alibaba Cloud Bailian endpoints via Lingxi proxy.

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Generate video | `/alibailian/api/v1/services/aigc/video-generation/video-synthesis` | POST |
| Query task | `/alibailian/api/v1/tasks/{task_id}` | GET |

**Model**: `wan2.5-i2v-preview`

**Request (POST)**:
- `model` (string, required)
- `input.prompt` (string)
- `input.negative_prompt` (string)
- `input.img_url` (string, required): first frame image URL or base64
- `input.audio_url` (string, optional): audio file URL (only wan2.5-i2v-preview)
- `input.template` (string, optional): video effect template
- `parameters.resolution` (string): e.g. `"480P"`
- `parameters.duration` (integer): seconds
- `parameters.prompt_extend` (boolean): default true
- `parameters.watermark` (boolean): default false
- `parameters.audio` (boolean): auto-add audio when audio_url empty
- `parameters.seed` (integer)

**Response**: returns `request_id`, `output.task_id`, `output.task_status`

**Query**: returns `output.task_status`, `output.video_url`, `usage.duration`, etc.

### Tongyi Wanxiang Status Codes

- `PENDING` — pending
- `SUCCEEDED` — succeeded

---

## Tencent AIGC Platform

Native Tencent Cloud VOD AIGC endpoints via Lingxi proxy. Supports multiple backend models (Kling, Hailuo, Vidu).

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Create task | `/tencent-vod/v1/aigc-video` | POST |
| Query result | `/tencent-vod/v1/query/{task_id}` | GET |
| Template effect | `/tencent-vod/v1/template-effect` | POST |

**Request (POST /tencent-vod/v1/aigc-video)**:
- `model_name` (string, required): `Hailuo`, `Kling`, `Vidu`
- `model_version` (string, required):
  - Hailuo: `02`, `2.3`, `2.3-fast`
  - Kling: `1.6`, `2.0`, `2.1`, `2.5`, `O1`, `3.0`, `3.0-Omni`
  - Vidu: `q2`, `q2-pro`, `q2-turbo`, `q3-pro`, `q3-turbo`
- `prompt` (string, required)
- `negative_prompt` (string)
- `enhance_prompt` (string): `Enabled` / `Disabled`
- `file_infos` (array): input images/videos
- `last_frame_url` (string): end frame (GV, Kling 2.1 1080P, Vidu q2-pro/q2-turbo)
- `output_config` (object):
  - `storage_mode`: `Permanent` / `Temporary`
  - `resolution`: `720P` / `1080P` (model-dependent)
  - `aspect_ratio`: `16:9`, `9:16`, `1:1`, `4:3`, `3:4`
  - `duration`: seconds (model-dependent)
  - `audio_generation`: `Enabled` / `Disabled`
  - `person_generation`: `AllowAdult` / `Disallowed`
- `scene_type` (string): `motion_control`, `avatar_i2v`, `lip_sync`
- `ext_info.AdditionalParameters` (object): `multi_shot`, `shot_type`, `multi_prompt`

**Response**: returns `Response.TaskId`, `Response.RequestId`

### Tencent AIGC Status Codes

| Status | Meaning |
|--------|---------|
| `WAITING` | Waiting |
| `PROCESSING` | Processing |
| `FINISH` | Finished |
| `ABORTED` | Aborted |

Sub-task status (`AigcImageTask`, `AigcVideoTask`):
- `PROCESSING` — processing
- `FINISH` — finished

---

## Kling Platform (可灵)

Kling has the richest API surface. All Kling tasks are async: submit -> get `task_id` -> poll -> download.

> **Note**: Kling also provides image generation, audio generation, and other capabilities. See `lingxi-image` for Kling image-specific workflows.

### Video Generation

| Capability | Submit Endpoint | Query Endpoint |
|-----------|----------------|----------------|
| Text-to-video (`文生视频`) | `POST /kling/text-to-video` | `GET /kling/tasks/{task_id}` |
| Image-to-video (`图生视频`) | `POST /kling/image-to-video` | `GET /kling/tasks/{task_id}` |
| Omni-Video (`Omni-Video`) | `POST /kling/omni-video` | `GET /kling/tasks/{task_id}` |
| Multi-image reference video (`多图参考生视频`) | `POST /kling/multi-image-video` | `GET /kling/tasks/{task_id}` |
| Video extension (`视频延长`) | `POST /kling/video-extend` | `GET /kling/tasks/{task_id}` |
| Video effects (`视频特效`) | `POST /kling/video-effects` | `GET /kling/tasks/{task_id}` |
| Motion control (`动作控制`) | `POST /kling/motion-control` | `GET /kling/tasks/{task_id}` |

### Multi-modal Video Editing (`多模态视频编辑`)

A staged editing workflow:

1. **Initialize video to edit**: `POST /kling/video-edit/init`
   - Provide source video
   - Returns `edit_session_id`

2. **Add selection**: `POST /kling/video-edit/add-selection`
   - Define region/time selection to edit

3. **Remove selection**: `POST /kling/video-edit/remove-selection`
   - Remove a previously added selection

4. **Preview selected regions**: `POST /kling/video-edit/preview`
   - Preview the current edit mask/selection

5. **Generate edited video**: `POST /kling/video-edit/generate`
   - Apply edits and start generation
   - Returns `task_id`

6. **Query task**: `GET /kling/tasks/{task_id}`

### Digital Human (`数字人`)

- **Submit**: `POST /kling/digital-human`
- **Query**: `GET /kling/tasks/{task_id}`
- Generates talking-head / presenter videos

### Lip Sync (`对口型`)

Two-step process:

1. **Face recognition**: `POST /kling/face-recognition`
   - Detect face in source image/video
   - Returns face data

2. **Lip sync**: `POST /kling/lip-sync`
   - Apply lip synchronization to audio
   - Returns `task_id`

3. **Query**: `GET /kling/tasks/{task_id}`

### Audio & Sound (Kling)

| Capability | Submit Endpoint | Query Endpoint |
|-----------|----------------|----------------|
| Text-to-sound-effect (`文生音效`) | `POST /kling/text-to-sound` | `GET /kling/tasks/{task_id}` |
| Video-to-sound-effect (`视频生音效`) | `POST /kling/video-to-sound` | `GET /kling/tasks/{task_id}` |
| Voice synthesis (`语音合成`) | `POST /kling/voice-synthesis` | `GET /kling/tasks/{task_id}` |

### Virtual Try-on (`虚拟试穿`)

- **Submit**: `POST /kling/virtual-try-on`
- **Query**: `GET /kling/tasks/{task_id}`

### Custom Voice (`自定义音色`)

- **Create custom voice**: `POST /kling/custom-voice`
- **Query single custom voice**: `GET /kling/custom-voice/{voice_id}`
- **Query official voice list**: `GET /kling/custom-voice/official`
- **Delete custom voice**: `DELETE /kling/custom-voice/{voice_id}`

### Subject / Character (`主体`)

For character consistency across generations:

- **Subject (old)**: `POST /kling/subject` (legacy)
- **Subject (new)**: `POST /kling/subject/v2`
- **Query custom subject (new)**: `GET /kling/subject/v2/{subject_id}`
- **Query official subject list (new)**: `GET /kling/subject/v2/official`
- **Delete custom subject (new)**: `DELETE /kling/subject/v2/{subject_id}`

### Kling Callback Protocol

Kling supports webhook callbacks for async task completion:

- Configure callback URL in Lingxi dashboard or per-request
- Callback payload format:

```json
{
  "task_id": "string",
  "task_status": "string",
  "task_status_msg": "string",
  "created_at": 1722769557708,
  "updated_at": 1722769557708,
  "task_result": {
    "images": [
      {
        "index": 0,
        "url": "string"
      }
    ],
    "videos": [
      {
        "id": "string",
        "url": "string",
        "duration": "string"
      }
    ]
  }
}
```

**`task_status` values**: `submitted`, `processing`, `succeed`, `failed`

- When failed, `task_status_msg` contains failure reason
- Verify callback signature if provided
- Reference: https://aicso.apifox.cn/doc-8626198.md

---

## Replicate Platform

Replicate-style async tasks via Lingxi proxy.

### Task Flow

1. **Create task**: `POST` with model version and input parameters
2. **Query task**: `GET` by prediction ID

### Supported Video Models

| Model | Official Doc |
|-------|-------------|
| `minimax/video-01-live` | https://replicate.com/minimax/video-01-live |
| `minimax/video-01` | https://replicate.com/minimax/video-01 |
| `andreasjansson/stable-diffusion-animation` | https://replicate.com/andreasjansson/stable-diffusion-animation |
| `lucataco/animate-diff` | https://replicate.com/lucataco/animate-diff |
| `riffusion/riffusion` | https://replicate.com/riffusion/riffusion |
| `prunaai/vace-14b` | https://replicate.com/prunaai/vace-14b |

### Create Task by Model Version

**Endpoint**: Replicate predictions endpoint via Lingxi proxy

**Request**:
- `version` (string): model version ID
- `input` (object): model-specific parameters

**Response**:
- `id` (string): prediction ID for polling
- `status` (string): `starting`, `processing`, `succeeded`, `failed`

**Query**:
- `GET` by prediction ID
- Poll until `succeeded` or `failed`

---

## Fal.ai Platform

Fal.ai native endpoints via Lingxi proxy. Uses `request_id` for polling.

### Veo3 Video Generation

| Endpoint | Description | Official Doc |
|----------|-------------|--------------|
| `POST /fal-ai/veo3` | Text-to-video | https://fal.ai/models/fal-ai/veo3 |
| `POST /fal-ai/veo3/fast` | Fast text-to-video | https://fal.ai/models/fal-ai/veo3/fast |
| `POST /fal-ai/veo3/image-to-video` | Image-to-video | https://fal.ai/models/fal-ai/veo3/image-to-video |
| `POST /fal-ai/veo3/fast/image-to-video` | Fast image-to-video | https://fal.ai/models/fal-ai/veo3/fast/image-to-video |
| `GET /fal-ai/veo3/requests/{request_id}` | Poll result | — |

### Kling Video on Fal.ai

| Endpoint | Description | Official Doc |
|----------|-------------|--------------|
| `POST /fal-ai/kling-video/v2.5-turbo/pro/text-to-video` | Kling text-to-video | https://fal.ai/models/fal-ai/kling-video/v2.5-turbo/pro/text-to-video |
| `POST /fal-ai/kling-video/v2.5-turbo/pro/image-to-video` | Kling image-to-video | https://fal.ai/models/fal-ai/kling-video/v2.5-turbo/pro/image-to-video |

### General Result Polling

**Endpoint**: `GET /fal-ai/requests/{request_id}` (platform-wide)

- Submit returns `request_id`
- Poll this endpoint until status is `COMPLETED` or `FAILED`
- Result contains `video_url`, `images`, or model-specific output

---

## Vidu Official

Native Vidu endpoints via Lingxi proxy.

| Capability | Description | Official Doc |
|-----------|-------------|--------------|
| Text-to-video | `POST` Vidu text-to-video endpoint | https://platform.vidu.cn/docs/text-to-video |
| Image-to-video | `POST` Vidu image-to-video endpoint | https://platform.vidu.cn/docs/image-to-video |
| Reference-to-video (with subject) | Subject-locked generation | https://platform.vidu.cn/docs/reference-to-video |
| Reference-to-video (without subject) | Style/reference generation | https://platform.vidu.cn/docs/reference-to-video |
| Start-end-to-video | First+last frame video | https://platform.vidu.cn/docs/start-end-to-video |
| Get request results | `GET` by request ID | Poll for completion |

All Vidu tasks are async: submit -> get request ID -> poll -> download.

### Vidu Status Codes

| Status | Meaning |
|--------|---------|
| `created` | Created successfully |
| `queueing` | Queuing |
| `processing` | Processing |
| `success` | Success |
| `failed` | Failed |

---

## Quick Start (Python)

### OpenAI-compatible (Sora / Veo / Grok)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LINGXI_API_KEY"),
    base_url=os.getenv("LINGXI_BASE_URL"),
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

### Veo Unified Format

```python
import requests

headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}
base_url = os.getenv("LINGXI_BASE_URL")

# Create
resp = requests.post(f"{base_url}/v1/video/create", headers=headers, json={
    "model": "veo3.1-fast",
    "prompt": "A drone flying over a tropical beach",
    "aspect_ratio": "16:9",
    "enhance_prompt": True,
}).json()
task_id = resp["id"]

# Poll
for _ in range(60):
    status = requests.get(f"{base_url}/v1/video/query?id={task_id}", headers=headers).json()
    if status["status"] == "completed":
        print("Video URL:", status["video_url"])
        break
    time.sleep(10)
```

### Luma Native Async

```python
import requests
import time

headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}
base_url = os.getenv("LINGXI_BASE_URL")

# Submit
resp = requests.post(f"{base_url}/luma/generations", headers=headers, json={
    "user_prompt": "A neon-lit cyberpunk street at night",
    "model_name": "ray-v2",
    "duration": "5s",
    "resolution": "720p",
}).json()
task_id = resp["data"]["task_id"]

# Poll
for _ in range(60):
    result = requests.get(f"{base_url}/luma/generations/{task_id}", headers=headers).json()
    state = result.get("state")
    if state == "completed":
        print("Video URL:", result["video"]["url"])
        break
    if state == "failed":
        raise RuntimeError("Luma task failed")
    time.sleep(10)
```

### MiniMax (海螺) Native Async

```python
resp = requests.post(f"{base_url}/minimax/v1/video_generation", headers=headers, json={
    "model": "MiniMax-Hailuo-02",
    "prompt": "A koi fish swimming in a pond",
    "duration": 10,
}).json()
task_id = resp["task_id"]

# Poll
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

### Doubao Native Async

```python
resp = requests.post(f"{base_url}/volc/v1/contents/generations/tasks", headers=headers, json={
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
        {"type": "text", "text": "A girl holding a fox, opening her eyes gently --resolution 720p --ratio 16:9 --duration 5"}
    ],
    "generate_audio": True,
}).json()
task_id = resp["id"]

# Poll single task
for _ in range(60):
    result = requests.get(f"{base_url}/volc/v1/contents/generations/tasks/{task_id}", headers=headers).json()
    if result.get("status") == "succeeded":
        print("Video URL:", result["content"]["video_url"])
        break
    time.sleep(10)
```

### Kling Native Async

```python
resp = requests.post(f"{base_url}/kling/text-to-video", headers=headers, json={
    "prompt": "A dragon flying over a mountain",
    "duration": 5,
}).json()
task_id = resp["data"]["task_id"]

for _ in range(30):
    status = requests.get(f"{base_url}/kling/tasks/{task_id}", headers=headers).json()
    if status["data"]["state"] == "completed":
        print("Video URL:", status["data"]["video_url"])
        break
    time.sleep(10)
```

### Kling Multi-modal Video Editing

```python
# 1. Init
resp = requests.post(f"{base_url}/kling/video-edit/init", headers=headers, json={
    "video_url": "https://example.com/source.mp4",
}).json()
session_id = resp["data"]["session_id"]

# 2. Add selection
requests.post(f"{base_url}/kling/video-edit/add-selection", headers=headers, json={
    "session_id": session_id,
    "region": {"x": 100, "y": 100, "w": 200, "h": 200},
    "time_range": [0, 5],
})

# 3. Preview
requests.post(f"{base_url}/kling/video-edit/preview", headers=headers, json={
    "session_id": session_id,
})

# 4. Generate
resp = requests.post(f"{base_url}/kling/video-edit/generate", headers=headers, json={
    "session_id": session_id,
    "prompt": "Replace the selected region with a galaxy background",
}).json()
task_id = resp["data"]["task_id"]
```

### Fal.ai Veo3

```python
resp = requests.post(f"{base_url}/fal-ai/veo3", headers=headers, json={
    "prompt": "A serene lake at sunrise with mist",
}).json()
request_id = resp["request_id"]

# Poll
for _ in range(60):
    result = requests.get(f"{base_url}/fal-ai/veo3/requests/{request_id}", headers=headers).json()
    if result.get("status") == "COMPLETED":
        print("Video URL:", result["video_url"])
        break
    time.sleep(5)
```

---

## Operational Guidance

- Video generation can take minutes; expose progress and allow cancel/retry.
- Cache by `(prompt, model, duration, size, image hash)` to avoid redundant costs.
- Store video assets in object storage and persist only URLs in metadata.
- For Kling, recommended polling interval: 10-15 seconds.
- For Luma, states are: `queued`, `pending`, `processing`, `completed`, `failed`.
- For MiniMax (海螺), supports text-to-video, image-to-video, and keyframe-to-video.
- For Fal.ai, always use `request_id` polling; do not rely on synchronous responses.
- For Replicate, polling interval: 5-10 seconds.
- Set up Kling callback webhooks for production to avoid excessive polling.

## Size & Duration Notes

- Veo: typically 720p or 1080p, 8s default; veo3.1 supports 4K
- Sora: `small` (~720p) or `large` (1080p); durations 10s (sora-2), 15s/25s (sora-2-pro)
- Kling: multiple resolutions, up to 10s per clip (extendable)
- Luma: 5s default, extendable
- Fal.ai Veo3: follows Google's Veo3 specs

## Anti-patterns

- Do not invent model names or aliases; use exact IDs from Lingxi model list.
- Do not block the UI without progress updates.
- Do not retry blindly on 4xx; handle validation failures explicitly.
- Do not forget to poll Fal.ai `request_id` endpoints; submissions are always async.

## Workflow

1) Confirm user intent, target platform/model, and input type (text/image/keyframe).
2) Run one minimal read-only query first to verify connectivity and permissions.
3) Execute the target operation with explicit parameters and bounded scope.
4) Verify results and save output/evidence files.

## References

- See `references/api_reference.md` for platform-specific endpoint mappings.
- Source list: `references/sources.md`
- Kling callback: https://aicso.apifox.cn/doc-8626198.md
- Replicate tutorial: https://aicso.apifox.cn/doc-8626199.md
- Fal.ai tutorial: https://aicso.apifox.cn/doc-8626202.md
- MiniMax docs: https://www.minimax.io/platform/document
- Vidu docs: https://platform.vidu.cn/docs
