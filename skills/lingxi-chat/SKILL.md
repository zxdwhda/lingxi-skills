---
name: lingxi-chat
description: Use when the user wants to interact with AI models through the Lingxi API Gateway. Trigger when the user asks to (1) chat or generate text with any model (GPT-4o, Claude, Gemini, DeepSeek, Qwen, etc.), (2) analyze or understand image content, (3) search the web for latest information, (4) use function calling or structured output, (5) convert speech to text (ASR/transcription), (6) convert text to speech (TTS), or (7) generate text embeddings.
---

Category: provider

# Lingxi Chat

## When to Use

Activate this skill when the user wants to:
- Chat with AI models (GPT-4o, Claude, Gemini, DeepSeek, etc.)
- Analyze or understand image content
- Search the web for latest information
- Use function calling / structured output
- Convert speech to text (ASR) or text to speech (TTS)
- Generate text embeddings

## Configuration

1. Read `LINGXI_API_KEY` from environment variables. If not set, ask the user for it.
2. Base URL is always `https://api.aicso.top/v1`.
3. Install dependency if needed: `pip install openai requests`.

## Intent Routing

| User Says | Endpoint | Default Model |
|-----------|----------|---------------|
| "Chat", "Ask", "Generate text" | `POST /v1/chat/completions` | `gpt-4o` |
| "Use Claude" (native) | `POST /v1/messages` | `claude-sonnet-4-20250514` |
| "Use Gemini" (native) | `POST /v1beta/models/{model}:generateContent` | `gemini-2.5-pro` |
| "Analyze image", "Look at this picture" | `POST /v1/chat/completions` + vision | `gpt-4o` |
| "Search web", "Latest news" | `POST /v1/chat/completions` + `web_search_options` | `gpt-4o-search-preview` |
| "Transcribe audio", "Speech to text" | `POST /v1/audio/transcriptions` | `whisper-1` |
| "Text to speech", "Read this aloud" | `POST /v1/audio/speech` | `gpt-4o-mini-tts` |
| "Embedding", "Vectorize" | `POST /v1/embeddings` | `text-embedding-3-small` |

## Image Handling

**For remote image URLs**: Pass directly via `image_url` in the message content.

**For local image files**: Do NOT send base64 directly. Instead:
1. Use the `lingxi-entry` image bed tool to upload the local file and get a public URL
2. Use that URL in the vision request

This ensures compatibility with all platforms (Kling, Midjourney, etc.) that require URLs.

## Core Code Templates

### Basic Chat
```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("LINGXI_API_KEY"),
    base_url="https://api.aicso.top/v1",
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "USER_QUERY_HERE"}],
)
print(response.choices[0].message.content)
```

### Streaming Chat
```python
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "USER_QUERY_HERE"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Vision (Image URL)
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image"},
            {"type": "image_url", "image_url": {"url": "IMAGE_URL_HERE"}}
        ]
    }],
)
print(response.choices[0].message.content)
```

### Web Search
```python
response = client.chat.completions.create(
    model="gpt-4o-search-preview",
    messages=[{"role": "user", "content": "USER_QUERY_HERE"}],
    web_search_options={},
)
print(response.choices[0].message.content)
```

### Function Calling
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Beijing?"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {"type": "object", "properties": {"city": {"type": "string"}}}
        }
    }],
)
print(response.choices[0].message.tool_calls)
```

### Speech-to-Text
```python
with open("audio.mp3", "rb") as f:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
    )
print(transcript.text)
```

### Text-to-Speech
```python
speech = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input="Text to speak here",
)
speech.stream_to_file("output.mp3")
```

### Embeddings
```python
embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input="Hello world",
)
print(embedding.data[0].embedding[:5])
```

## Provider-Specific Formats (Advanced)

Only use these when the user explicitly requests the native format of a specific provider.

### Claude Native
```python
import requests, os

headers = {
    "x-api-key": os.getenv("LINGXI_API_KEY"),
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}
payload = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Hello!"}],
}
response = requests.post(
    f"{os.getenv('LINGXI_BASE_URL', 'https://api.aicso.top/v1')}/v1/messages",
    headers=headers, json=payload,
)
print(response.json()["content"])
```

Key differences from OpenAI format:
- `max_tokens` is **required**
- `system` is a top-level field, not a message with `role: "system"`
- Images use `"type": "image"` with `"source"` object
- PDFs use `"type": "document"` content blocks

### Gemini Native
```python
import requests, os

headers = {"Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}"}
payload = {
    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
    "generationConfig": {"temperature": 0.7},
}
response = requests.post(
    "https://api.aicso.top/v1beta/models/gemini-2.5-pro:generateContent",
    headers=headers, json=payload,
)
print(response.json()["candidates"][0]["content"]["parts"])
```

Key differences:
- Uses `contents` with `parts` instead of `messages`
- Images use `inlineData` (base64) or `fileData` (URI) within parts

## Operational Notes

- Use `stream=True` for long responses to improve perceived latency
- For vision tasks, prefer HTTPS URLs over base64 to reduce payload size
- For reasoning models (o1/o3/deepseek-thinking), `temperature` is usually ignored; use `reasoning_effort` instead
- For structured output, include "JSON" in the prompt and set `response_format`
- Cache embeddings by input hash to avoid redundant calls
- Claude native format always requires `max_tokens`

## Error Handling

If the API returns **"无可用渠道"** (no available distributor), it means the current token group does not support the requested model. Do NOT retry blindly. Instead:
1. Suggest the user switch to a different token group in the Lingxi dashboard
2. Or fall back to a different model from the same category
3. Or use `client.models.list()` to check which models are available in the current group

Other common errors:
- **401**: API Key invalid → Ask user to check their key
- **429**: Rate limited → Wait a few seconds and retry
- **500/503**: Upstream error → Retry once; if persists, inform user it's an upstream issue

## Anti-patterns

- Do NOT hardcode API keys in scripts; always use env vars
- Do NOT send large base64 payloads without checking limits; use URL references when possible
- Do NOT retry blindly on 4xx; handle validation failures explicitly
- Do NOT mix native and chat-compatible format fields in the same request

## Workflow

1. Identify user intent (chat/vision/search/audio/embedding/specific model)
2. Confirm/obtain `LINGXI_API_KEY`
3. Route to the correct model and endpoint based on the intent table above
4. If local image files are involved, upload via image bed first (see `lingxi-entry`)
5. Execute the call and present results to the user
6. Report token usage / estimated cost if relevant
