---
name: lingxi-audio
description: Use when the user wants to generate or process audio through the Lingxi API Gateway. Trigger when the user asks to (1) generate music or songs, (2) convert text to speech (TTS), (3) transcribe audio to text (ASR), (4) clone or design a custom voice, or (5) mentions Suno, Whisper, MiniMax, or audio generation.
---

Category: provider

# Lingxi Audio

## When to Use

- User wants to generate music or songs
- User wants text-to-speech (TTS) or speech-to-text (ASR/transcription)
- User wants to clone a voice or design a custom voice
- User mentions Suno, TTS, Whisper, voice clone, music generation

## Configuration

1. Read `LINGXI_API_KEY` from environment. If not set, ask the user.
2. Base URL: `https://api.aicso.top/v1`
3. Install if needed: `pip install openai requests`

## Intent Routing

| User Says | Platform | Model | Sync/Async |
|-----------|----------|-------|-----------|
| "Generate music", "Create song", "Suno" | Suno | `chirp-v4` | Async |
| "Text to speech", "Read aloud", "TTS" | OpenAI TTS | `gpt-4o-mini-tts` | Sync |
| "Speech to text", "Transcribe" | OpenAI Whisper | `whisper-1` | Sync |
| "Voice clone", "Clone my voice" | MiniMax | `speech-2.8-hd` | Async |
| "Custom voice", "Design voice" | MiniMax | voice design | Async |
| "Audio effects", "Sound effects" | Vidu | `audio1.0` | Async |

> **Default recommendation**: Use OpenAI TTS for speech (fastest, simplest). Use Suno for music.

## Core Code Templates

### Text-to-Speech (OpenAI)

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("LINGXI_API_KEY"),
    base_url="https://api.aicso.top/v1",
)

speech = client.audio.speech.create(
    model="gpt-4o-mini-tts",  # or "tts-1", "tts-1-hd"
    voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
    input="Hello, this is a test of text to speech.",
    response_format="mp3",
)
speech.stream_to_file("output.mp3")
```

### Speech-to-Text / Transcription (OpenAI)

```python
with open("audio.mp3", "rb") as f:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",  # or "gpt-4o-transcribe"
        file=f,
        response_format="text",  # text, json, srt, verbose_json, vtt
    )
print(transcript.text)
```

### Transcription with Timestamps

```python
transcript = client.audio.transcriptions.create(
    file=open("speech.mp3", "rb"),
    model="whisper-1",
    response_format="verbose_json",
    timestamp_granularities=["word"],
)
print(transcript.words)
```

### Suno Music Generation (Async)

```python
import requests
import time

base_url = "https://api.aicso.top"
headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}

# Custom mode (provide lyrics)
resp = requests.post(f"{base_url}/suno/submit/music", headers=headers, json={
    "prompt": "[Verse]\nNeon lights reflect on rain-wet streets...",
    "title": "Cyberpunk Dreams",
    "tags": "electronic, synthwave",
    "mv": "chirp-v4",
}).json()
task_id = resp["data"]

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
}).json()
print("Lyrics task ID:", resp["data"])
```

### Suno Inspiration Mode (AI generates lyrics + music)

```python
resp = requests.post(f"{base_url}/suno/submit/music", headers=headers, json={
    "gpt_description_prompt": "一首动听的情歌",
    "make_instrumental": False,
    "mv": "chirp-v4",
}).json()
task_id = resp["data"]
# Poll same as above
```

### MiniMax Async TTS

```python
resp = requests.post(f"{base_url}/minimax/v1/t2a_async_v2", headers=headers, json={
    "model": "speech-02-hd",
    "text": "你好，欢迎使用语音合成服务！",
    "voice_setting": {
        "voice_id": "moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85",
        "speed": 1, "vol": 1, "pitch": 0,
    },
    "audio_setting": {
        "format": "mp3",
        "audio_sample_rate": 32000,
        "bitrate": 128000,
        "channel": 2,
    },
}).json()
task_id = resp["task_id"]

# Poll
for _ in range(30):
    st = requests.get(f"{base_url}/minimax/v1/query/t2a_async_query_v2",
                      headers=headers, params={"task_id": task_id}).json()
    if st["status"] == "SUCCESS":
        file_resp = requests.get(f"{base_url}/minimax/v1/files/retrieve",
                                 headers=headers, params={"file_id": st["file_id"]}).json()
        print("Download URL:", file_resp["file"]["download_url"])
        break
    time.sleep(5)
```

### MiniMax Voice Clone

```python
# 1. Upload audio
with open("clone_sample.mp3", "rb") as f:
    upload = requests.post(f"{base_url}/minimax/v1/files", headers=headers,
                           files={"file": f}, data={"purpose": "voice_clone"}).json()
file_id = upload["file"]["file_id"]

# 2. Clone
clone = requests.post(f"{base_url}/minimax/v1/voice_clone", headers=headers, json={
    "file_id": file_id,
    "voice_id": "MyCustomVoice001",
    "text": "A gentle breeze sweeps across the soft grass.",
    "model": "speech-2.8-hd",
}).json()
print("Clone result:", clone)
```

## Platform Notes

| Platform | Best For | Speed | Special Notes |
|----------|----------|-------|---------------|
| OpenAI TTS | General speech | Instant | Simplest, 6 voices |
| OpenAI ASR | Transcription | Instant | 25MB max, supports timestamps |
| Suno | Music generation | 1-3 min | Must poll async |
| MiniMax TTS | Chinese TTS | 5-30s (async) | Rich voice controls |
| MiniMax Clone | Voice cloning | Minutes | 10-30s clear audio needed |

## Error Handling

- **"无可用渠道"** → Current token group does not support this model. Switch group or model.
- **"Invalid URL"** → Native endpoints (Suno, MiniMax) use `https://api.aicso.top` without `/v1` prefix.
- **"上游负载已饱和"** → Upstream provider is temporarily overloaded. Retry later.
- **"all_retries_failed"** → Async task upstream failure. The task may succeed on retry, or the provider may be down.

## Anti-patterns

- Do NOT block the UI without progress updates for async tasks (Suno, MiniMax)
- Do NOT upload excessively large audio files for ASR; compress first (max 25MB)
- Do NOT invent model names or voice IDs; use exact values from the model list
- Do NOT pass both `text` and `text_file_id` to MiniMax async TTS

## Workflow

1. Identify intent: music, TTS, ASR, or voice clone
2. Choose platform based on intent routing table
3. For async tasks (Suno, MiniMax): submit, poll, report progress
4. For sync tasks (OpenAI TTS/ASR): execute immediately
5. Return result URL or file to user
