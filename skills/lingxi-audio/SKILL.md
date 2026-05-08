---
name: lingxi-audio
description: Use when generating or processing audio through Lingxi API Gateway, including Suno music generation, text-to-speech (TTS), speech-to-text (ASR/Whisper), voice cloning, MiniMax audio APIs, Vidu audio/TTS, and OpenAI Realtime speech.
version: 1.2.0
---

Category: provider

# Lingxi Audio

## Validation

```bash
mkdir -p output/lingxi-audio
python -m py_compile skills/lingxi-audio/scripts/audio_demo.py && echo "py_compile_ok" > output/lingxi-audio/validate.txt
```

Pass criteria: command exits 0 and `output/lingxi-audio/validate.txt` is generated.

## Output And Evidence

- Save generated audio URLs, lyrics, and metadata to `output/lingxi-audio/`.
- Keep one end-to-end run log for troubleshooting.

## Prerequisites

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install openai requests
```

- Set `LINGXI_API_KEY` and `LINGXI_BASE_URL` in environment.

## Supported Platforms

| Platform | Capabilities | Format |
|----------|-------------|--------|
| Suno | Music generation (inspiration, custom, continuation, singer style, upload extend, concat), lyrics gen | Native |
| OpenAI TTS | `gpt-4o-mini-tts`, `tts-1` | OpenAI |
| OpenAI ASR | `whisper-1`, `gpt-4o-transcribe` | OpenAI |
| MiniMax (Official) | Async TTS V2, sync TTS V2, voice clone, voice design, upload clone audio | Native |
| Vidu (Official) | Text-to-audio, TTS | Native |
| Rerank | `qwen3-rerank` etc. | OpenAI-compatible |

---

## Upload Requirements by Platform

| Platform / Task | Upload Method | Format / Limit | Notes |
| --- | --- | --- | --- |
| **Suno Inspiration** | None (text only) | — | No upload needed |
| **Suno Custom** | None (text only) | — | Lyrics provided as text |
| **Suno Continuation** | None (uses existing task) | — | Reference existing Suno task |
| **Suno Singer Style** | Audio file | MP3, WAV; 10-60s | Upload via S3 presigned URL flow |
| **Suno Remix (Upload)** | Audio file | MP3, WAV; 10-60s | Upload via S3 presigned URL flow |
| **Suno Concat** | None (uses existing tasks) | — | Reference existing Suno tasks |
| **OpenAI TTS** | None (text only) | — | No upload needed |
| **OpenAI ASR/Whisper** | Local file upload | MP3, WAV, M4A, etc.; <25MB | Standard multipart upload |
| **MiniMax Sync TTS** | None (text only) | — | No upload needed |
| **MiniMax Async TTS** | None (text only) | — | No upload needed |
| **MiniMax Voice Clone** | Audio file | MP3, WAV; 10-30s, clear voice | Upload clone audio file |
| **MiniMax Voice Design** | None (text only) | — | Describe voice in text |
| **Vidu TTS** | None (text only) | — | No upload needed |
| **Vidu Text-to-Audio** | None (text only) | — | No upload needed |
| **Realtime Speech** | Microphone stream | PCM 16-bit, 24kHz | WebSocket streaming |

> **Suno Upload Flow**: For singer style or remix tasks, you must first upload the audio file via the S3 presigned URL flow (init → get auth → upload to S3 → report done). See the Suno section below for details.

## Suno Music Generation

Suno uses asynchronous task-based API. All tasks return a task ID string for polling.

Base URL pattern: `https://{BASE_URL}`

### Task Submission Endpoints

| Mode | Endpoint | Description |
|------|----------|-------------|
| **Inspiration** (`灵感模式`) | `POST /suno/submit/music` | AI generates lyrics and music from a topic/prompt |
| **Custom** (`自定义模式`) | `POST /suno/submit/music` | Provide lyrics, title, tags, style manually |
| **Continuation** (`续写模式`) | `POST /suno/submit/music` | Extend an existing song from a clip |
| **Singer Style** (`歌手风格`) | `POST /suno/submit/music` | Generate in a specific artist/singer style |
| **Upload Extend** (`上传歌曲二次创作`) | `POST /suno/submit/music` | Extend/remix an uploaded audio file |
| **Concatenation** (`拼接歌曲`) | `POST /suno/submit/concat` | Join multiple song clips into one |
| **Lyrics Generation** (`生成歌词`) | `POST /suno/submit/lyrics` | Generate lyrics only (no music) |

### Request Fields by Mode

**Inspiration mode** (`POST /suno/submit/music`):
- `gpt_description_prompt` (string, **required**): topic or description, e.g. `"一首动听的情歌"`
- `make_instrumental` (boolean): `true` for instrumental only
- `mv` (string, **required**): model version, e.g. `chirp-v4`, `chirp-v3-5`, `chirp-v3-0`
- `prompt` (string): lyrics content (used in custom mode)
- `notify_hook` (string): callback URL on task completion

**Custom mode** (`POST /suno/submit/music`):
- `prompt` (string, **required**): full lyrics
- `title` (string, **required**): song title
- `mv` (string, **required**): model version
- `tags` (string): style tags separated by half-width commas, e.g. `"electronic, pop"`
- `continue_at` (integer): timestamp in seconds to continue from
- `continue_clip_id` (string): clip ID to continue
- `task` (string): default `"generate"`

**Continuation mode** (`POST /suno/submit/music`):
- `prompt` (string, **required**): lyrics for the continuation part
- `title` (string, **required**): song title
- `mv` (string, **required**): model version
- `tags` (string): style tags
- `continue_at` (integer, **required**): continue timestamp in seconds
- `continue_clip_id` (string, **required**): clip ID to continue from
- `task` (string, **required**): `"extend"`

**Singer style mode** (`POST /suno/submit/music`):
- `prompt` (string, **required**): lyrics content
- `generation_type` (string, **required**): e.g. `"TEXT"`
- `mv` (string, **required**): model version (use `chirp-v4-tau` or `chirp-v3-5-tau`)
- `title` (string, **required**): song title
- `tags` (string): style tags
- `negative_tags` (string): negative style tags
- `task` (string): `"artist_consistency"`
- `persona_id` (string, **required**): persona ID created from a clip
- `artist_clip_id` (string, **required**): reference audio clip ID
- `vocal_gender` (string): `"m"` or `"f"`

**Upload extend mode** (`POST /suno/submit/music`):
- `prompt` (string, **required**): lyrics to sing next
- `mv` (string, **required**): model version
- `title` (string, **required**): title
- `continue_clip_id` (string, **required**): uploaded audio clip ID
- `continue_at` (integer, **required**): extend start timestamp
- `task` (string, **required**): `"upload_extend"`
- `tags` (string): style tags
- `negative_tags` (string): negative tags

**Concat mode** (`POST /suno/submit/concat`):
- `clip_id` (string, **required**): extended song clip ID
- `is_infill` (boolean/string): whether infill

**Lyrics generation** (`POST /suno/submit/lyrics`):
- `prompt` (string, **required**): topic or theme for lyrics
- `notify_hook` (string): callback URL

### Response (Submission)

```json
{
  "code": "success",
  "data": "950bf3af-78a6-420e-8c01-3bde0bbb3ef9",
  "message": ""
}
```

`data` is the `task_id` string.

### Query Endpoints

- **Batch query**: `POST /suno/fetch`
  - Body: `ids` (array of task ID strings)
- **Single query**: `GET /suno/fetch/{task_id}`
- **Get WAV**: `GET /suno/act/wav/{clip_id}`
- **Timing/Lyrics timeline**: `GET /suno/act/timing/{id}`
- **Scene details**: `GET /suno/feed/{task_id}`

All query responses wrap data in `{ "code": "success", "data": "...", "message": "" }`.

### Supported Models

- `chirp-v3-0` (v3.0)
- `chirp-v3-5` (v3.5)
- `chirp-v4` (v4.0)
- `chirp-auk` (v4.5)
- `chirp-v5` (v5.0)
- For upload/cover tasks: `chirp-v3-5-tau` or `chirp-v4-tau`

### Task Status Values

`NOT_START`, `SUBMITTED`, `QUEUED`, `IN_PROGRESS`, `FAILURE`, `SUCCESS`

---

## Suno Upload Flow (for Remix / Extend)

To upload custom audio for remix or continuation:

1. **Request upload authorization**: `POST /suno/uploads/audio`
   - Body: `{ "extension": "mp3" }`
   - Returns: `id` (upload_id), `url` (S3 presigned URL), `fields` (S3 form fields: `Content-Type`, `key`, `AWSAccessKeyId`, `policy`, `signature`), `is_file_uploaded`

2. **Upload to S3**: `POST` to the presigned `url`
   - Form fields: include all `fields` plus the binary `file`
   - Client uploads directly to S3, not through the API gateway

3. **Report upload done**: `POST /suno/uploads/audio/{id}/upload-finish`
   - Body: `{ "upload_type": "file_upload", "upload_filename": "my_audio.mp3" }`

4. **Query upload status**: `GET /suno/uploads/audio/{id}`
   - Poll every 2-3 seconds until `status` is `complete`
   - Response: `{ "id": "...", "status": "complete", "error_message": null, "s3_id": "...", "title": "...", "image_url": "..." }`

5. **Initialize audio clip**: `POST /suno/uploads/audio/{id}/initialize-clip`
   - Returns: `{ "clip_id": "..." }`

6. **Use the clip**: The returned `clip_id` can be used as `continue_clip_id` in `upload_extend` tasks or for remix/continuation.

---

## Text-to-Speech (TTS)

### OpenAI-compatible

**Endpoint**: `POST /v1/audio/speech`

- `model`: `gpt-4o-mini-tts`, `tts-1`, `tts-1-hd`
- `voice`: e.g. `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`
- `input`: text to speak
- `response_format`: `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm`
- `speed`: 0.25 to 4.0

### MiniMax Official Async TTS V2

**Endpoint**: `POST /minimax/v1/t2a_async_v2`

Request body fields:
- `model` (string): e.g. `speech-02-hd`, `speech-2.8-hd`, `speech-2.8-turbo`
- `text` (string): text to synthesize (up to ~50k characters). Either `text` or `text_file_id` is required.
- `text_file_id` (string): uploaded TXT/ZIP file ID for batch processing
- `language_boost` (string): `auto` or specific language
- `voice_setting` (object):
  - `voice_id` (string): voice ID
  - `speed` (number): default `1`
  - `vol` (number): default `1`
  - `pitch` (number): default `0`
  - `emotion` (string): e.g. `calm`, `happy`
- `pronunciation_dict` (object):
  - `tone` (array): e.g. `["危险/dangerous"]`
- `audio_setting` (object):
  - `audio_sample_rate` (integer): e.g. `32000`, `44100`
  - `bitrate` (integer): e.g. `128000`, `256000`
  - `format` (string): `mp3`, `flac`
  - `channel` (integer): `1` or `2`
- `voice_modify` (object): `pitch`, `intensity`, `timbre`, `sound_effects`
- `aigc_watermark` (boolean): default `false`

Response:
```json
{
  "task_id": "95157322514444",
  "task_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "file_id": "95157322514444",
  "usage_characters": 101,
  "base_resp": { "status_code": 0, "status_msg": "success" }
}
```

### MiniMax Official Sync TTS V2

**Endpoint**: `POST /minimax/v1/t2a_v2`

Request body fields:
- `model` (string): e.g. `speech-02-hd`, `speech-2.8-hd`, `speech-2.8-turbo`
- `text` (string): text to synthesize
- `stream` (boolean): `true` for streaming output
- `stream_options` (object): `{ "exclude_aggregated_audio": false }`
- `voice_setting` (object): same as async
- `pronunciation_dict` (object): same as async
- `audio_setting` (object): `sample_rate`, `bitrate`, `format`, `channel`, `force_cbr`
- `subtitle_enable` (boolean): enable subtitle file output
- `timber_weights` (array): mixed voice weights, e.g. `[{ "voice_id": "female-chengshu", "weight": 30 }, ...]`
- `voice_modify` (object): `pitch`, `intensity`, `timbre`, `sound_effects`

Response (non-streaming):
```json
{
  "data": { "audio": "2f2f2f2f504b0304...", "status": 2 },
  "extra_info": {
    "audio_length": 9900,
    "audio_sample_rate": 32000,
    "audio_size": 160323,
    "bitrate": 128000,
    "word_count": 52,
    "usage_characters": 26,
    "audio_format": "mp3",
    "audio_channel": 1
  },
  "trace_id": "...",
  "base_resp": { "status_code": 0, "status_msg": "success" }
}
```

### MiniMax Async TTS Query

**Endpoint**: `GET /minimax/v1/query/t2a_async_query_v2?task_id={task_id}`

Response:
```json
{
  "task_id": 95157322514444,
  "status": "Processing",
  "file_id": 95157322514496,
  "base_resp": { "status_code": 0, "status_msg": "success" }
}
```

Status values: `Processing`, `SUCCESS`, etc.

### MiniMax File Retrieve (for async audio/video download)

**Endpoint**: `GET /minimax/v1/files/retrieve?file_id={file_id}`

Response:
```json
{
  "file": {
    "file_id": "...",
    "bytes": 0,
    "created_at": 1700469398,
    "filename": "output_aigc.mp4",
    "purpose": "video_generation",
    "download_url": "www.downloadurl.com"
  },
  "base_resp": { "status_code": 0, "status_msg": "success" }
}
```

### Vidu Official TTS

**Endpoint**: `POST /ent/v2/audio-tts`

Request body fields:
- `text` (string, **required**): text to synthesize (< 10000 characters). Supports pause tags `<#x#>` where x is seconds [0.01, 99.99]. Paragraph breaks use newline.
- `voice_setting_voice_id` (string, **required**): voice ID
- `voice_setting_speed` (string): range [0.5, 2], default `1.0`
- `voice_setting_volume` (string): range 0-10, default `0`
- `voice_setting_pitch` (string): range [-12, 12], default `0`
- `voice_setting_emotion` (string): `happy`, `sad`, `angry`, `fearful`, `disgusted`, `surprised`, `calm`
- `pronunciation_dict_tone` (string): multi-tone definitions, e.g. `["燕少飞/(yan4)(shao3)(fei1)"]`
- `payload` (string): passthrough data

Response:
```json
{
  "task_id": "911094612548939776",
  "state": "created",
  "model": "audio1.0",
  "prompt": "...",
  "duration": 5,
  "seed": 0,
  "created_at": "2026-01-20T07:16:38.094635957Z",
  "credits": 10
}
```

### Vidu Official Text-to-Audio

**Endpoint**: `POST /ent/v2/text2audio`

Request body fields:
- `model` (string, **required**): `audio1.0`
- `prompt` (string, **required**): audio description (< 1500 characters)
- `duration` (string): default `10`, range 2-10 seconds
- `seed` (string): random seed, `0` for auto
- `callback_url` (string): callback URL

Response:
```json
{
  "task_id": "911094612548939776",
  "state": "created",
  "model": "audio1.0",
  "prompt": "雨滴落在窗户上的声音，伴随着轻柔的雷声",
  "duration": 5,
  "seed": 0,
  "created_at": "2026-01-20T07:16:38.094635957Z",
  "credits": 10
}
```

### Vidu Query Result

**Endpoint**: `GET /ent/v2/tasks/{id}/creations`

Returns task status and output URLs. Example response contains `Status`, `TaskType`, `AigcImageTask`/`AigcVideoTask` output with `FileUrl`.

---

## Speech-to-Text (ASR / Whisper)

### OpenAI-compatible

**Endpoint**: `POST /v1/audio/transcriptions`

- `model`: `whisper-1`, `gpt-4o-transcribe`
- `file`: audio file (max 25 MB)
- `language`: optional ISO code
- `response_format`: `json`, `text`, `srt`, `verbose_json`, `vtt`
- `timestamp_granularities`: `word`, `segment`

Supported formats: `mp3`, `mp4`, `mpeg`, `mpg`, `m4a`, `wav`, `webm`

**Endpoint**: `POST /v1/audio/translations` (translate to English)

---

## Voice Clone & Design

### MiniMax Voice Clone

1. **Upload clone audio**: `POST /minimax/v1/files`
   - `multipart/form-data`
   - `purpose`: `voice_clone`
   - `file`: audio file (`mp3`/`m4a`/`wav`, 10s-5min, <20MB)
   - Returns: `file_id`

2. **Upload sample audio** (optional, for prompt audio): `POST /minimax/v1/files`
   - `purpose`: `prompt_audio`

3. **Quick clone**: `POST /minimax/v1/voice_clone`
   - `file_id` (integer, **required**): uploaded audio file ID
   - `voice_id` (string, **required**): custom voice ID (8-256 chars, starts with letter, alphanumeric/- allowed, no trailing -/)
   - `clone_prompt` (object): `{ "prompt_audio": integer, "prompt_text": string }` (both required if used)
   - `text` (string): preview text (<= 1000 chars, supports emotion tags)
   - `model` (string): preview model, e.g. `speech-2.8-hd`, `speech-2.6-hd`
   - `language_boost` (string): e.g. `English`, `auto`
   - `need_noise_reduction` (boolean)
   - `need_volume_normalization` (boolean)
   - `aigc_watermark` (boolean)

### MiniMax Voice Design

**Endpoint**: `POST /minimax/v1/voice_design`

- `prompt` (string): voice description, e.g. `"讲述悬疑故事的播音员，声音低沉富有磁性。"`
- `preview_text` (string): preview text for the designed voice
- `voice_id` (string): custom voice ID to assign
- `aigc_watermark` (boolean)

---

## Rerank

**Endpoint**: `POST /v1/rerank`

Request body:
- `model` (string, **required**): e.g. `qwen3-rerank`
- `documents` (array of strings, **required**)
- `query` (string, **required**)
- `top_n` (integer, **required**)
- `instruct` (string, **required**): e.g. `"Given a web search query, retrieve relevant passages that answer the query."`

Response:
```json
{
  "results": [
    { "document": { "text": "..." }, "index": 0, "relevance_score": 0.9155 },
    ...
  ],
  "usage": { "prompt_tokens": 107, "completion_tokens": 0, "total_tokens": 107 }
}
```

---

## Quick Start (Python)

### Suno Custom Mode

```python
import os
import requests
import time

headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}
base_url = os.getenv("LINGXI_BASE_URL")

# Submit custom mode task
resp = requests.post(f"{base_url}/suno/submit/music", headers=headers, json={
    "prompt": "[Verse]\nNeon lights reflect on rain-wet streets...",
    "title": "Cyberpunk Dreams",
    "tags": "electronic, synthwave",
    "mv": "chirp-v4",
})
resp.raise_for_status()
task_id = resp.json()["data"]

# Poll
for _ in range(60):
    status = requests.get(f"{base_url}/suno/fetch/{task_id}", headers=headers).json()
    if status["data"]["status"] == "SUCCESS":
        print("Audio URL:", status["data"].get("audio_url"))
        print("Lyrics:", status["data"].get("lyrics"))
        break
    time.sleep(10)
```

### Suno Lyrics Generation

```python
resp = requests.post(f"{base_url}/suno/submit/lyrics", headers=headers, json={
    "prompt": "A song about space exploration",
})
lyrics_data = resp.json()["data"]
print("Generated lyrics task ID:", lyrics_data)
```

### Suno Upload Flow (for Remix)

```python
# 1. Request upload auth
init_resp = requests.post(f"{base_url}/suno/uploads/audio", headers=headers,
                          json={"extension": "mp3"}).json()
upload_id = init_resp["data"]["id"]
presigned_url = init_resp["data"]["url"]
fields = init_resp["data"]["fields"]

# 2. Upload to S3 directly
with open("my_song.mp3", "rb") as f:
    files = {**{k: (None, v) for k, v in fields.items()}, "file": f}
    requests.post(presigned_url, files=files)

# 3. Report upload done
requests.post(f"{base_url}/suno/uploads/audio/{upload_id}/upload-finish",
              headers=headers, json={"upload_type": "file_upload", "upload_filename": "my_song.mp3"})

# 4. Poll upload status
for _ in range(30):
    st = requests.get(f"{base_url}/suno/uploads/audio/{upload_id}", headers=headers).json()
    if st["data"]["status"] == "complete":
        s3_id = st["data"]["s3_id"]
        break
    time.sleep(3)

# 5. Initialize clip
clip_resp = requests.post(f"{base_url}/suno/uploads/audio/{upload_id}/initialize-clip",
                          headers=headers, json={}).json()
clip_id = clip_resp["data"]["clip_id"]

# 6. Use in upload_extend task
remix_resp = requests.post(f"{base_url}/suno/submit/music", headers=headers, json={
    "task": "upload_extend",
    "continue_clip_id": clip_id,
    "continue_at": 10,
    "prompt": "lyrics to sing next",
    "mv": "chirp-v4",
    "title": "Remix Title",
}).json()
print("Remix task:", remix_resp["data"])
```

### MiniMax Async TTS

```python
resp = requests.post(f"{base_url}/minimax/v1/t2a_async_v2", headers=headers, json={
    "model": "speech-02-hd",
    "text": "你好，欢迎使用语音合成服务！",
    "voice_setting": { "voice_id": "moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85", "speed": 1, "vol": 1, "pitch": 0 },
    "audio_setting": { "format": "mp3", "audio_sample_rate": 32000, "bitrate": 128000, "channel": 2 },
})
resp.raise_for_status()
data = resp.json()
task_id = data["task_id"]

# Poll async status
for _ in range(30):
    st = requests.get(f"{base_url}/minimax/v1/query/t2a_async_query_v2",
                      headers=headers, params={"task_id": task_id}).json()
    if st["status"] == "SUCCESS":
        # Retrieve file
        file_resp = requests.get(f"{base_url}/minimax/v1/files/retrieve",
                                 headers=headers, params={"file_id": st["file_id"]}).json()
        print("Download URL:", file_resp["file"]["download_url"])
        break
    time.sleep(5)
```

### MiniMax Sync TTS

```python
resp = requests.post(f"{base_url}/minimax/v1/t2a_v2", headers=headers, json={
    "model": "speech-02-hd",
    "text": "你好，欢迎使用语音合成服务！",
    "stream": False,
    "voice_setting": { "voice_id": "moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85" },
})
resp.raise_for_status()
data = resp.json()
print("Audio hex:", data["data"]["audio"][:100])
print("Usage chars:", data["extra_info"]["usage_characters"])
```

### MiniMax Voice Clone

```python
# Upload audio
with open("clone_sample.mp3", "rb") as f:
    upload = requests.post(f"{base_url}/minimax/v1/files", headers=headers,
                           files={"file": f}, data={"purpose": "voice_clone"}).json()
file_id = upload["file"]["file_id"]

# Clone
clone = requests.post(f"{base_url}/minimax/v1/voice_clone", headers=headers, json={
    "file_id": file_id,
    "voice_id": "MyCustomVoice001",
    "text": "A gentle breeze sweeps across the soft grass.",
    "model": "speech-2.8-hd",
}).json()
print("Clone result:", clone)
```

### Vidu Text-to-Audio

```python
resp = requests.post(f"{base_url}/ent/v2/text2audio", headers=headers, json={
    "model": "audio1.0",
    "prompt": "雨滴落在窗户上的声音，伴随着轻柔的雷声",
    "duration": "5",
}).json()
print("Task ID:", resp["task_id"])
```

### Vidu TTS

```python
resp = requests.post(f"{base_url}/ent/v2/audio-tts", headers=headers, json={
    "text": "人工智能正在改变我们的生活方式。",
    "voice_setting_voice_id": "male-qn-daxuesheng",
    "voice_setting_speed": "1.0",
}).json()
print("Task ID:", resp["task_id"])
```

### TTS (OpenAI-compatible)

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LINGXI_API_KEY"),
    base_url=os.getenv("LINGXI_BASE_URL"),
)

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello from Lingxi audio gateway.",
)
response.stream_to_file("output.mp3")
```

### ASR

```python
audio_file = open("speech.mp3", "rb")
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    response_format="text",
)
print(transcript)
```

---

## Operational Guidance

- Suno generation can take 1-3 minutes; expose progress and allow cancel/retry.
- Cache TTS results by `(text, model, voice, speed)` to avoid redundant costs.
- For ASR, prefer compressed formats (MP3, OGG) to reduce upload size.
- For MiniMax async TTS, polling interval: 5-10 seconds. Use `/minimax/v1/files/retrieve` with `file_id` to get the final download URL.
- For MiniMax sync TTS, `data.audio` is hex-encoded; decode to bytes before saving.
- For voice clone, ensure reference audio is clear and 10-30 seconds long (mp3/m4a/wav, <20MB).
- For Suno upload flow, S3 URLs are time-limited; upload immediately after getting the presigned URL.
- Use `GET /suno/act/timing/{id}` to get synchronized lyrics for karaoke-style apps.
- Use `POST /suno/fetch` with `ids` array to batch-query multiple tasks.

## Anti-patterns

- Do not invent model names or voice IDs; use exact values from Lingxi model list.
- Do not block the UI without progress updates for async tasks.
- Do not upload excessively large audio files for ASR; compress first.
- Do not reuse expired S3 presigned URLs; request a new one if upload fails.
- Do not pass both `text` and `text_file_id` to MiniMax async TTS; provide exactly one.

## Workflow

1) Confirm user intent: music generation, TTS, ASR, or voice clone/design.
2) Run one minimal read-only query first to verify connectivity.
3) Execute the target operation with explicit parameters.
4) Verify results and save output/evidence files.

## References

- Suno docs: https://aicso.apifox.cn/doc-8626179.md (overview), https://aicso.apifox.cn/doc-8626180.md (parameters)
- MiniMax TTS async: https://platform.minimaxi.com/docs/api-reference/speech-t2a-async-create
- MiniMax TTS sync: https://platform.minimaxi.com/docs/api-reference/speech-t2a-http
- MiniMax voice clone: https://platform.minimaxi.com/docs/api-reference/voice-cloning-clone
- Vidu audio: https://platform.vidu.cn/docs/text-to-audio
- Vidu TTS: https://platform.vidu.cn/docs/text-to-speech
