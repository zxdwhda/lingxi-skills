---
name: lingxi-chat
description: Use when chatting with LLMs through Lingxi API Gateway, including OpenAI GPT, Anthropic Claude, Google Gemini, and Responses API formats. Covers chat completions, function calling, embeddings, web search, vision, reasoning, audio, and structured output.
version: 1.2.0
---

Category: provider

# Lingxi Chat

## Validation

```bash
mkdir -p output/lingxi-chat
python -m py_compile skills/lingxi-chat/scripts/chat_demo.py && echo "py_compile_ok" > output/lingxi-chat/validate.txt
```

Pass criteria: command exits 0 and `output/lingxi-chat/validate.txt` is generated.

## Output And Evidence

- Save request/response summaries and logs to `output/lingxi-chat/`.
- Keep one end-to-end run log for troubleshooting.

## Prerequisites

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install openai
```

- Set `LINGXI_API_KEY` and `LINGXI_BASE_URL` in environment.
- Base URL from docs: `https://api.aicso.top/v1`

## Unified Interface

### Chat Completions (OpenAI-compatible)

**Endpoint**: `POST /v1/chat/completions`

**Request fields**:
- `model` (string, required): e.g. `gpt-4o`, `claude-sonnet-4-20250514`, `gemini-2.5-pro`, `deepseek-v3-1-250821`
- `messages` (array, required): conversation history with `role` and `content`
- `stream` (boolean, optional): default `false`
- `temperature` (number, optional): 0 to 2
- `top_p` (number, optional): nucleus sampling
- `n` (integer, optional): default 1, number of completions
- `max_tokens` (integer, optional): max tokens to generate
- `stop` (string/array, optional): up to 4 sequences to stop generation
- `presence_penalty` (number, optional): -2.0 to 2.0
- `frequency_penalty` (number, optional): -2.0 to 2.0
- `logit_bias` (object, optional): map token IDs to bias values (-100 to 100)
- `seed` (integer, optional): deterministic sampling seed
- `user` (string, optional): end-user identifier
- `response_format` (object, optional): `{"type": "json_object"}` or `{"type": "json_schema", "json_schema": {...}}`
- `tools` (array, optional): function definitions
- `tool_choice` (string/object, optional): `auto`, `none`, or `{"type": "function", "function": {"name": "..."}}`
- `extra_body` (object, optional): `{"enable_thinking": true}` for thinking mode

**Response fields**:
- `id` (string): unique identifier
- `object` (string): `"chat.completion"`
- `created` (integer): Unix timestamp
- `choices[]`:
  - `index` (integer)
  - `message`: `role`, `content`, `tool_calls` (array, if function calling)
  - `finish_reason`: `stop`, `length`, `tool_calls`
- `usage`: `prompt_tokens`, `completion_tokens`, `total_tokens`
- `system_fingerprint` (string): backend configuration fingerprint

**Streaming response** (`stream: true`):
- Each chunk has `choices[].delta` with `role`, `content`, or `tool_calls`
- Stream terminates with `data: [DONE]`

## Upload Requirements by Platform

When using vision or document understanding, different formats require different upload methods:

| Platform / Feature | Upload Method | Format / Limit | Notes |
| --- | --- | --- | --- |
| **OpenAI GPT-4o Vision** | URL or Base64 | JPEG, PNG, WEBP, GIF; max 20MB per image | Base64 recommended for <1MB images; URL for larger |
| **Claude Native Vision** | URL or Base64 | JPEG, PNG, GIF, WEBP; max 5MB per image | Use `"type": "image"` content block |
| **Claude Native PDF** | URL or Base64 | PDF; max 32MB | Use `"type": "document"` content block |
| **Claude Chat-Compatible Vision** | URL (image_url) | Same as OpenAI | Standard OpenAI-compatible format |
| **Gemini Native Vision** | URL or Base64 | JPEG, PNG, HEIC, HEIF, WEBP; max 20MB | Inline data in `contents.parts` |
| **Gemini Native Document** | URL or Base64 | PDF, JS, PY, TXT, HTML, etc. | Up to 7.5MB per file |
| **Gemini Native Video** | URL or Base64 | MP4, MOV, AVI, etc. | Up to ~100MB recommended |
| **Gemini Native Audio** | URL or Base64 | MP3, WAV, etc. | Up to ~30MB recommended |
| **GPT-4o-audio** | Base64 (data URI) | MP3, WAV, PCM; max ~25MB | Audio input in messages |
| **Whisper / ASR** | Local file upload | MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM; max 25MB | Standard multipart upload |
| **TTS** | None (text only) | — | No upload needed |

> **Tip**: For platforms requiring URLs (Midjourney, some Kling endpoints), upload your file to the Lingxi image bed first (`lingxi-entry` skill) to get a public URL.

### Vision (Image Understanding)

Supported via chat completions with image URLs or base64:

```python
messages=[
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image"},
            {"type": "image_url", "image_url": {"url": "https://..."}}
        ]
    }
]
```

Also supports local base64 images:
```python
import base64
with open("image.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
messages=[
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
        ]
    }
]
```

Models supporting vision: `gpt-4o`, `claude-sonnet-4-20250514`, `gemini-1.5-pro-latest`, `deepseek-ocr`

### Audio

#### GPT-4o-audio (Audio in Chat)

Uses chat completions with audio modalities:
- Endpoint: `POST /v1/chat/completions`
- `model`: `gpt-4o-audio-preview`
- `modalities`: `["text", "audio"]`
- `audio`: `{"voice": "alloy", "format": "wav"}`
- Supported voices: `alloy`, `ash`, `ballad`, `coral`, `echo`, `fable`, `nova`, `onyx`, `sage`, `shimmer`
- Supported formats: `wav`, `mp3`, `flac`, `opus`, `pcm16`
- Input audio is provided as base64 data URL in the message content

#### Speech-to-Text (Transcription)

Models: `whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`
- Endpoint: `POST /v1/audio/transcriptions`
- `file`: audio file (multipart/form-data)
- `model`: transcription model
- `language` (optional): ISO-639-1 language code
- `prompt` (optional): text to guide style
- `response_format` (optional): `json`, `text`, `srt`, `verbose_json`, `vtt`
- `temperature` (optional): 0 to 1
- Supports `timestamp_granularities`: `["word"]` for word-level timestamps with `verbose_json`

#### Text-to-Speech (TTS)

Models: `tts-1`, `tts-1-hd`, `gpt-4o-mini-tts`
- Endpoint: `POST /v1/audio/speech`
- `model`: TTS model
- `input`: text to synthesize (max 4096 characters)
- `voice`: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`
- `response_format` (optional): `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm`
- `speed` (optional): 0.25 to 4.0, default 1.0

**Note**: Translation endpoint (`/v1/audio/translations`) is **not supported**.

### Embeddings

**Endpoint**: `POST /v1/embeddings`

- `model`: e.g. `text-embedding-3-small`, `text-embedding-3-large`, `text-embedding-ada-002`
- `input`: string or array of strings (max 8192 tokens per input)
- Response: `object`, `data[]` (with `embedding` array, `index`), `model`, `usage`

Models comparison:
| Model | Dimensions | MTEB | Max Input |
|-------|-----------|------|-----------|
| text-embedding-3-small | 1536 (default) | 62.3% | 8191 |
| text-embedding-3-large | 3072 (default) | 64.6% | 8191 |
| text-embedding-ada-002 | 1536 | 61.0% | 8191 |

Gemini native embeddings use a different endpoint structure (`embedContent`). See Gemini Native Format section.

### Web Search

**Endpoint**: `POST /v1/chat/completions` with model `gpt-4o-search-preview`

```json
{
  "model": "gpt-4o-search-preview",
  "web_search_options": {},
  "messages": [{"role": "user", "content": "What was a positive news story from today?"}]
}
```

**Responses API web search**:
```json
{
  "model": "gpt-4.1-2025-04-14",
  "tools": [{"type": "web_search_preview"}],
  "input": "what was a positive news story from today?"
}
```

**Claude native web search**:
```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 1024,
  "messages": [{"role": "user", "content": "What is the weather in NYC?"}],
  "tools": [{"type": "web_search_20250305", "name": "web_search"}]
}
```

**Gemini native web search**:
```json
{
  "contents": [{"role": "user", "parts": [{"text": "Latest news about AI"}]}],
  "tools": [{"googleSearch": {}}]
}
```

### Legacy Completions

**Endpoint**: `POST /v1/completions`

- `model`: e.g. `gpt-3.5-turbo-instruct`
- `prompt`: string or array of strings
- `max_tokens`, `temperature`, `top_p`, `stream`, `stop`, `n`, `best_of`, `echo`, `frequency_penalty`, `presence_penalty`, `logit_bias`, `seed`, `suffix`

Response has `choices[].text` instead of `choices[].message.content`.

### Model List

**Endpoint**: `GET /v1/models`

Lists available models and their capabilities.

### Translation (Qwen MT)

**Endpoint**: `POST /v1/chat/completions`
- Model: `qwen-mt-turbo`
- Extra field: `translation_options`: `{"source_lang": "auto", "target_lang": "English"}`

---

## Provider-Specific Formats

Since Lingxi is a gateway, understanding **format differences** between providers is critical.

### Anthropic Claude

Claude is accessible via **two distinct formats** through Lingxi.

#### Claude Native Format

**Endpoint**: `POST /v1/messages`

**Headers**:
- `x-api-key`: your API key
- `anthropic-version`: `2023-06-01`
- `content-type`: `application/json`

This mirrors the Anthropic Messages API directly.

**Request fields**:
- `model` (string, required): e.g. `claude-sonnet-4-20250514`
- `max_tokens` (integer, required): maximum tokens to generate
- `messages` (array, required): conversation with **Claude content blocks**
- `system` (string or array, optional): system prompt (top-level field)
- `tools` (array, optional): function definitions with `name`, `description`, `input_schema`
  ```json
  {
    "name": "get_weather",
    "description": "Get the current weather in a given location",
    "input_schema": {
      "type": "object",
      "properties": {
        "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"}
      },
      "required": ["location"]
    }
  }
  ```
- `tool_choice` (optional): `auto`, `none`, or `{"type": "tool", "name": "..."}`
- `thinking` (object, optional): reasoning control
  - `type`: `"enabled"`
  - `budget_tokens`: integer (max tokens for thinking)
- `output_format` (object, optional): structured output
  - `type`: `"json_schema"`
  - `schema`: JSON Schema object with `properties`, `required`, `additionalProperties: false`
- `stream` (boolean, optional): default `false`
- `temperature`, `top_p`, `stop` (optional)

**Content block types** (in `messages[].content`):
- Text: `{"type": "text", "text": "..."}`
- Image: `{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "..."}}` or `{"type": "image", "source": {"type": "url", "url": "https://..."}}`
- Document/PDF: `{"type": "document", "source": {"type": "url", "url": "https://..."}}` or base64 source
- Tool use: `{"type": "tool_use", "id": "...", "name": "...", "input": {...}}`
- Tool result: `{"type": "tool_result", "tool_use_id": "...", "content": "..."}`

**Response fields**:
- `content`: array of content blocks (text, thinking, tool_use)
- `stop_reason`: `end_turn`, `max_tokens`, `stop_sequence`, `tool_use`
- `usage`: `input_tokens`, `output_tokens`

**Key differences from OpenAI format**:
- `max_tokens` is **required**
- `system` is a top-level field, not a message with `role: "system"`
- Images use `"type": "image"` with `"source"` object, not `"image_url"`
- PDFs use `"type": "document"` content blocks (Claude native supports PDFs directly)
- Thinking output appears as `{"type": "thinking", "thinking": "..."}` blocks in `content`
- Function calling uses `input_schema` instead of `parameters`, and tool calls are `tool_use` blocks
- Web search uses `{"type": "web_search_20250305", "name": "web_search"}` in tools

#### Claude Chat-Compatible Format

**Endpoint**: `POST /v1/chat/completions`

Uses standard OpenAI-compatible message format.

**Request fields**:
- Standard OpenAI chat completion fields
- `model`: e.g. `claude-sonnet-4-20250514`
- `messages`: standard `role`/`content` format
- `stream` (boolean, optional)
- Supports vision via `image_url` or base64 data URLs in message content

**Thinking in chat-compatible format**:
```json
{
  "model": "claude-sonnet-4-20250514",
  "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Hello!"}],
  "stream": true,
  "max_tokens": 16000,
  "thinking": {"type": "enabled", "budget_tokens": 10240}
}
```

**Key differences from native format**:
- Uses standard `messages` with `role` (system, user, assistant)
- Images use OpenAI-style `image_url` objects
- PDF support may be limited or require different handling compared to native format
- `max_tokens` may or may not be required depending on gateway translation

---

### Google Gemini

Gemini is accessible via **two distinct formats** through Lingxi.

#### Gemini Native Format

**Endpoint**: `POST /v1beta/models/{model}:generateContent` (and `:streamGenerateContent` for streaming)

**Headers**:
- `Authorization`: `Bearer {API_KEY}`
- `Content-Type`: `application/json`

This mirrors the Google Gemini API directly.

**Request fields**:
- `contents` (array, required): array of `Content` objects
  - Each `Content` has `role` (`user` or `model`) and `parts` (array)
  - Parts can be: `{"text": "..."}`, `{"inlineData": {"mimeType": "image/png", "data": "base64..."}}`, `{"fileData": {"mimeType": "...", "fileUri": "..."}}`
- `systemInstruction` (object, optional): `{"parts": [{"text": "..."}]}`
- `generationConfig` (object, optional):
  - `temperature`, `topP`, `topK`, `maxOutputTokens`, `stopSequences`
  - `responseSchema`: for structured output (JSON Schema)
  - `responseMimeType`: e.g. `"application/json"`
  - `thinkingConfig`: `{"includeThoughts": true, "thinkingBudget": 26240}`
- `tools` (array, optional):
  - Function calling: `[{"functionDeclarations": [{"name": "...", "description": "...", "parameters": {...}}]}]`
  - Google Search: `[{"googleSearch": {}}]`

**Response fields**:
- `candidates[].content.parts`: generated content parts
- `candidates[].content.role`: `"model"`
- `candidates[].finishReason`: `STOP`, `MAX_TOKENS`, `SAFETY`, `RECITATION`, `OTHER`
- `usageMetadata`: `promptTokenCount`, `candidatesTokenCount`, `totalTokenCount`

**Example - Text generation**:
```json
{
  "systemInstruction": {"parts": [{"text": "You are a helpful assistant."}]},
  "contents": [{"role": "user", "parts": [{"text": "Who are you?"}]}],
  "generationConfig": {"temperature": 1, "topP": 1}
}
```

**Example - Function calling**:
```json
{
  "contents": [{"role": "user", "parts": [{"text": "Schedule a meeting with Bob and Alice for 03/27/2025 at 10:00 AM about the Q3 planning."}]}],
  "tools": [{"functionDeclarations": [{"name": "schedule_meeting", "description": "Schedules a meeting...", "parameters": {"type": "object", "properties": {...}, "required": [...]}}]}]
}
```

**Key differences from OpenAI format**:
- Uses `contents` with `parts` instead of `messages` with `content`
- Images use `inlineData` (base64) or `fileData` (URI) within parts
- Function declarations use `functionDeclarations` inside `tools` array items
- Structured output uses `responseSchema` in `generationConfig`, not `response_format`
- System prompt is `systemInstruction` with `parts`, not a system message
- Google Search is a native tool type

#### Gemini Chat-Compatible Format

**Endpoint**: `POST /v1/chat/completions`

Uses standard OpenAI-compatible message format.

**Request fields**:
- Standard OpenAI chat completion fields
- `model`: e.g. `gemini-2.5-pro`, `gemini-1.5-pro-latest`
- `messages`: standard `role`/`content` format
- Supports vision via `image_url` or base64 in message content
- Supports thinking/reasoning via `reasoning_effort`

**Example**:
```json
{
  "model": "gemini-2.5-pro",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who are you?"}
  ],
  "temperature": 0.1,
  "top_p": 1,
  "stream": false
}
```

**Key differences from native format**:
- Uses standard `messages` array with OpenAI-style roles
- Images use `image_url` format instead of `inlineData`
- Structured output uses `response_format` instead of `responseSchema`
- Function calling uses OpenAI-style `tools`/`tool_calls` format
- Embeddings use standard `/v1/embeddings` endpoint

---

### Responses API (OpenAI)

**Endpoint**: `POST /v1/responses`

The Responses API is a newer OpenAI API format with different semantics from Chat Completions. Some models ONLY support Response format (e.g. `o3-pro`, `codex-mini-latest`).

**Request fields**:
- `model` (string, required): e.g. `gpt-4.1`, `gpt-5.1`, `gpt-5-2025-08-07`, `o3-pro`
- `input` (required): replaces `messages`. Can be:
  - A string (single user message)
  - An array of input items with `role` and `content` (similar to messages but different structure)
  - Content can be array of objects with `type` and `text`
- `instructions` (string, optional): replaces system message
- `tools` (array, optional): function calling, web search
- `tool_choice` (string, optional): `auto`, `none`, `required`
- `reasoning` (object, optional): thinking control
  - `effort`: `"minimal"`, `"low"`, `"medium"`, or `"high"` (default: medium)
  - `summary`: `"auto"`, `"concise"`, or `"detailed"`
- `text` (object, optional): text response config
  - `format`: `{"type": "text"}`
  - `verbosity`: `"low"`, `"medium"`, `"high"`
- `stream` (boolean, optional): default `false`
- `store` (boolean, optional): whether to store response for later retrieval, default `true`
- `temperature`, `max_output_tokens`, `top_p` (optional)
- `metadata` (object, optional): custom metadata

**Response fields**:
- `id` (string): response ID for continuing conversation
- `object` (string): `"response"`
- `created_at` (integer): Unix timestamp
- `status`: `"completed"`
- `output` (array): output items (message, function_call, etc.)
  - Message items: `{"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "..."}]}`
  - Function call items: `{"type": "function_call", "call_id": "...", "name": "...", "arguments": "..."}`
- `usage`: `input_tokens`, `output_tokens`, `total_tokens`
  - `input_tokens_details.cached_tokens`
  - `output_tokens_details.reasoning_tokens`
- `previous_response_id` (string): for multi-turn conversations
- `model` (string)
- `parallel_tool_calls` (boolean)

**Key differences from Chat Completions API**:
- Uses `input` instead of `messages`
- Uses `instructions` instead of system message in `messages`
- Uses `max_output_tokens` instead of `max_tokens`
- Response structure uses `output` array with typed items instead of `choices`
- Conversation state is tracked via `previous_response_id` rather than passing full message history
- Function calling uses `function_call` items in `output` with `call_id`
- Web search is configured via `tools` with `type: "web_search_preview"`
- Thinking/reasoning is controlled via `reasoning.effort`
- `text.verbosity` controls response verbosity

**Example - Basic**:
```json
{
  "model": "gpt-5.1",
  "input": [{"role": "user", "content": "Write a one-sentence bedtime story about a unicorn."}]
}
```

**Example - With reasoning**:
```json
{
  "model": "gpt-5.1",
  "input": [{"role": "user", "content": "1+2+3+4+5....9985"}],
  "reasoning": {"effort": "medium", "summary": "auto"},
  "text": {"format": {"type": "text"}, "verbosity": "medium"},
  "stream": true,
  "store": true
}
```

**Example - Function calling**:
```json
{
  "model": "gpt-4.1",
  "input": [{"role": "user", "content": "Get the horoscope for Aquarius"}],
  "tools": [
    {
      "type": "function",
      "name": "get_horoscope",
      "description": "Get today's horoscope for an astrological sign.",
      "parameters": {"type": "object", "properties": {"sign": {"type": "string"}}, "required": ["sign"]}
    }
  ],
  "tool_choice": "auto"
}
```

---

## Format Comparison Summary

| Feature | OpenAI Chat | Claude Native | Claude Chat-Compat | Gemini Native | Gemini Chat-Compat | Responses API |
|---------|-------------|---------------|-------------------|---------------|-------------------|---------------|
| Endpoint | `/v1/chat/completions` | `/v1/messages` | `/v1/chat/completions` | `/v1beta/models/{model}:generateContent` | `/v1/chat/completions` | `/v1/responses` |
| Auth Header | `Authorization: Bearer` | `x-api-key` | `Authorization: Bearer` | `Authorization: Bearer` | `Authorization: Bearer` | `Authorization: Bearer` |
| Messages | `messages[]` | `messages[]` | `messages[]` | `contents[]` | `messages[]` | `input` |
| System | `role: "system"` | Top-level `system` | `role: "system"` | `systemInstruction` | `role: "system"` | `instructions` |
| Vision | `image_url` | `image` block | `image_url` | `inlineData`/`fileData` | `image_url` | `input` with image |
| PDF | Not native | `document` block | Limited | `fileData` | File attachments | Limited |
| Functions | `tools`/`tool_calls` | `tools`/`tool_use` | `tools`/`tool_calls` | `functionDeclarations` | `tools`/`tool_calls` | `tools`/`function_call` |
| Structured | `response_format` | `output_format` | `response_format` | `responseSchema` | `response_format` | `text.format` |
| Thinking | `reasoning_effort` | `thinking` block | `thinking` object | `thinkingConfig` | `reasoning_effort` | `reasoning.effort` |
| Audio I/O | `modalities` + `audio` | Not supported | Not supported | Native audio parts | Not supported | Limited |
| Web Search | `web_search_options` | `web_search_20250305` | Model dependent | `googleSearch` tool | Model dependent | `web_search_preview` tool |

---

## Quick Start (Python + OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LINGXI_API_KEY"),
    base_url=os.getenv("LINGXI_BASE_URL"),
)

# Non-streaming chat
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello, Lingxi"}],
)
print(response.choices[0].message.content)

# Streaming chat
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Count to 5"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# Vision with URL
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "https://example.com/image.png"}}
            ]
        }
    ],
)
print(response.choices[0].message.content)

# Vision with local file
import base64
with open("image.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            ]
        }
    ],
    max_tokens=300,
)
print(response.choices[0].message.content)

# Function calling
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

# Structured output with json_schema
response = client.chat.completions.create(
    model="gpt-4.1-2025-04-14",
    messages=[
        {"role": "system", "content": "Determine if the user input violates specific guidelines and explain if they do."},
        {"role": "user", "content": "How do I prepare for a job interview?"}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "content_compliance",
            "description": "Determines if content is violating specific moderation rules",
            "schema": {
                "type": "object",
                "properties": {
                    "is_violating": {"type": "boolean"},
                    "category": {"type": ["string", "null"], "enum": ["violence", "sexual", "self_harm"]},
                    "explanation_if_violating": {"type": ["string", "null"]}
                },
                "required": ["is_violating", "category", "explanation_if_violating"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
)
print(response.choices[0].message.content)

# Reasoning control
response = client.chat.completions.create(
    model="o4-mini",
    messages=[{"role": "user", "content": "Solve this math problem: 2+2"}],
    max_tokens=500,
    reasoning_effort="medium",
)
print(response.choices[0].message.content)

# DeepSeek thinking control
response = client.chat.completions.create(
    model="deepseek-v3-1-250821",
    messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Hello"}],
    max_tokens=1000,
    stream=True,
    thinking={"type": "enabled"}
)

# Embeddings
embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input="Hello world",
)
print(embedding.data[0].embedding[:5])

# Audio transcription
with open("audio.mp3", "rb") as f:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
    )
print(transcript.text)

# Audio transcription with timestamps
transcript = client.audio.transcriptions.create(
    file=open("speech.mp3", "rb"),
    model="whisper-1",
    response_format="verbose_json",
    timestamp_granularities=["word"]
)
print(transcript.words)

# Text-to-speech
speech = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    input="Hello, this is a test.",
    voice="alloy",
)
speech.stream_to_file("output.mp3")

# GPT-4o-audio
response = client.chat.completions.create(
    model="gpt-4o-audio-preview",
    messages=[{"role": "user", "content": "Is a golden retriever a good family dog?"}],
    modalities=["text", "audio"],
    audio={"voice": "alloy", "format": "wav"},
)
```

---

## Provider-Specific Examples

### Claude Native Format (requires `requests`)

```python
import requests, os

headers = {
    "x-api-key": os.getenv("LINGXI_API_KEY"),
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

# Native message
payload = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 4096,
    "system": "You are a helpful assistant.",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": True,
}
response = requests.post(
    f"{os.getenv('LINGXI_BASE_URL')}/v1/messages",
    headers=headers,
    json=payload,
)
print(response.json()["content"])

# Native message with PDF
payload = {
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 1024,
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What are the key findings in this document?"},
                {
                    "type": "document",
                    "source": {
                        "type": "url",
                        "url": "https://assets.anthropic.com/.../Claude-3-Model-Card.pdf"
                    }
                }
            ]
        }
    ],
}

# Native message with PDF base64
payload = {
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 1024,
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": "JVBERi0xLjcK..."}},
                {"type": "text", "text": "Which model has the highest human preference win rates?"}
            ]
        }
    ],
}

# Native function calling
payload = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "tools": [
        {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"}
                },
                "required": ["location"]
            }
        }
    ],
    "messages": [{"role": "user", "content": "What is the weather like in San Francisco?"}],
}

# Native structured output
payload = {
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 1024,
    "messages": [
        {"role": "user", "content": "Extract key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."}
    ],
    "output_format": {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "plan_interest": {"type": "string"},
                "demo_requested": {"type": "boolean"}
            },
            "required": ["name", "email", "plan_interest", "demo_requested"],
            "additionalProperties": False
        }
    }
}

# Native thinking
payload = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 8000,
    "thinking": {"type": "enabled", "budget_tokens": 1200},
    "messages": [{"role": "user", "content": "Solve this step by step"}],
}

# Native web search
payload = {
    "model": "claude-sonnet-4-6",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "What is the weather in NYC?"}],
    "tools": [{"type": "web_search_20250305", "name": "web_search"}],
}
```

### Gemini Native Format (requires `requests`)

```python
import requests, os, base64

headers = {
    "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
    "Content-Type": "application/json",
}

# Native generateContent
payload = {
    "systemInstruction": {"parts": [{"text": "You are a helpful assistant."}]},
    "contents": [{"role": "user", "parts": [{"text": "Who are you?"}]}],
    "generationConfig": {"temperature": 1, "topP": 1}
}
response = requests.post(
    f"{os.getenv('LINGXI_BASE_URL')}/v1beta/models/gemini-2.5-pro:generateContent",
    headers=headers,
    json=payload,
)
print(response.json()["candidates"][0]["content"]["parts"])

# Native with inline image
with open("image.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
payload = {
    "contents": [
        {
            "role": "user",
            "parts": [
                {"text": "Describe this image"},
                {"inlineData": {"mimeType": "image/png", "data": b64}}
            ]
        }
    ],
    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024},
}

# Native with function calling
payload = {
    "contents": [{"role": "user", "parts": [{"text": "Schedule a meeting with Bob and Alice for 03/27/2025 at 10:00 AM about the Q3 planning."}]}],
    "tools": [
        {
            "functionDeclarations": [
                {
                    "name": "schedule_meeting",
                    "description": "Schedules a meeting with specified attendees at a given time and date.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "attendees": {"type": "array", "items": {"type": "string"}},
                            "date": {"type": "string"},
                            "time": {"type": "string"},
                            "topic": {"type": "string"}
                        },
                        "required": ["attendees", "date", "time", "topic"]
                    }
                }
            ]
        }
    ]
}

# Native structured output
payload = {
    "contents": [{"role": "user", "parts": [{"text": "Give me a person's info"}]}],
    "generationConfig": {
        "responseMimeType": "application/json",
        "responseSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
    },
}

# Native with Google Search
payload = {
    "contents": [{"role": "user", "parts": [{"text": "Latest news about AI"}]}],
    "tools": [{"googleSearch": {}}],
}

# Native with thinking config
payload = {
    "contents": [{"role": "user", "parts": [{"text": "Explain quantum computing"}]}],
    "generationConfig": {
        "thinkingConfig": {"includeThoughts": True, "thinkingBudget": 26240}
    }
}
```

### Responses API (requires `requests`)

```python
import requests, os

headers = {
    "Authorization": f"Bearer {os.getenv('LINGXI_API_KEY')}",
    "Content-Type": "application/json",
}

# Basic response
payload = {
    "model": "gpt-5.1",
    "input": [{"role": "user", "content": "Write a one-sentence bedtime story about a unicorn."}],
}
response = requests.post(
    f"{os.getenv('LINGXI_BASE_URL')}/v1/responses",
    headers=headers,
    json=payload,
)
data = response.json()
# Extract text from output
for item in data.get("output", []):
    if item.get("type") == "message":
        for c in item.get("content", []):
            if c.get("type") == "output_text":
                print(c.get("text"))

# Streaming response
payload = {
    "model": "gpt-4.1",
    "stream": True,
    "input": [{"role": "user", "content": "Hello"}],
}

# With reasoning control
payload = {
    "model": "gpt-5.1",
    "input": [{"role": "user", "content": "Explain quantum computing"}],
    "reasoning": {"effort": "high"},
}

# With web search
payload = {
    "model": "gpt-4.1-2025-04-14",
    "tools": [{"type": "web_search_preview"}],
    "input": "what was a positive news story from today?",
}

# With function calling
payload = {
    "model": "gpt-4.1",
    "input": [{"role": "user", "content": "Get the horoscope for Aquarius"}],
    "tools": [
        {
            "type": "function",
            "name": "get_horoscope",
            "description": "Get today's horoscope for an astrological sign.",
            "parameters": {"type": "object", "properties": {"sign": {"type": "string"}}, "required": ["sign"]}
        }
    ],
    "tool_choice": "auto",
}

# GPT-5 with full config
payload = {
    "model": "gpt-5-2025-08-07",
    "input": [{"role": "user", "content": [{"type": "input_text", "text": "1+2+3+4+5....9985"}]}],
    "tools": [],
    "text": {"format": {"type": "text"}, "verbosity": "medium"},
    "reasoning": {"effort": "medium", "summary": "auto"},
    "stream": True,
    "store": True,
}

# Multi-turn via previous_response_id
first = requests.post(
    f"{os.getenv('LINGXI_BASE_URL')}/v1/responses",
    headers=headers,
    json={"model": "gpt-4.1", "input": "Hello"},
).json()

second = requests.post(
    f"{os.getenv('LINGXI_BASE_URL')}/v1/responses",
    headers=headers,
    json={
        "model": "gpt-4.1",
        "input": "Tell me more",
        "previous_response_id": first["id"],
    },
)
```

---

## Other SDK Configurations

### LangChain

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    openai_api_base="https://api.aicso.top/v1",
    openai_api_key="sk-xxxxx"
)
res = llm.invoke("hello")
print(res.content)
```

Older langchain via environment variables:
```bash
export OPENAI_BASE_URL="https://api.aicso.top/v1"
export OPENAI_API_KEY="sk-xxxxx"
```

### LlamaIndex

```python
from llama_index.llms.openai import OpenAI

llm = OpenAI(
    model="gpt-3.5-turbo",
    api_key="sk-xxxxx",
    api_base="https://api.aicso.top/v1")
ret = llm.complete("Paul Graham is ")
print(ret)
```

### Node.js

```bash
npm i openai
```

```js
const fs = require('fs');
const OpenAI = require('openai');

const openai = new OpenAI({
  apiKey: 'sk-xxxxxxxx',
  baseURL: 'https://api.aicso.top/v1'
});

async function transcribeAudio() {
  const transcription = await openai.audio.transcriptions.create({
    file: fs.createReadStream('audio.mp3'),
    model: 'whisper-1',
  });
  console.log('Transcript:', transcription.text);
}

transcribeAudio();
```

---

## Operational Guidance

- Use `stream=True` for long responses to improve perceived latency.
- For vision tasks, prefer HTTPS URLs over base64 to reduce payload size. Base64 is required for local files.
- For reasoning models (o1/o3/deepseek-thinking), `temperature` is usually fixed or ignored; use `reasoning_effort` or model-specific thinking controls instead.
- For structured output, always include "JSON" in the prompt and set the appropriate format field for your API format (`response_format` for OpenAI-compatible, `output_format` for Claude native, `responseSchema` for Gemini native).
- For Claude native format, always provide `max_tokens`; it is required.
- For Gemini native format, use `parts` array in `contents`; each part can be text, inline data, or file reference.
- For GPT-4o-audio, set `modalities=["text", "audio"]` and configure `audio` parameters for voice output.
- Cache embeddings by input hash to avoid redundant calls.
- When using the Responses API, store `previous_response_id` for multi-turn conversations instead of rebuilding message history.
- PDF support: Claude native has the best native PDF support via `document` blocks. Other formats may require text extraction or image conversion.
- Web search behavior varies significantly by provider and model; test with your target model to verify search integration.
- Translation model `qwen-mt-turbo` uses `translation_options` field with `source_lang` and `target_lang`.

## Anti-patterns

- Do not hardcode API keys in scripts; always use env vars.
- Do not retry blindly on 4xx; handle validation failures explicitly.
- Do not assume all models support the same parameters (e.g., `temperature` on reasoning models).
- Do not mix native and chat-compatible format fields in the same request; use the correct format for your chosen endpoint.
- Do not assume PDF support exists in chat-compatible formats if you need native document understanding; use Claude native or Gemini native instead.
- Do not send large base64 payloads without checking payload size limits; use URL references when possible.

## Workflow

1) Confirm user intent, target format (OpenAI/Claude-native/Claude-chat/Gemini-native/Gemini-chat/Responses), and model.
2) Run one minimal read-only query first to verify connectivity.
3) Execute the target operation with explicit parameters matching the chosen format.
4) Verify results and save output/evidence files.

## References

- Lingxi API Docs Portal: https://aicso.apifox.cn/
- OpenAI API Reference: https://platform.openai.com/docs/api-reference
- Anthropic Claude API: https://docs.anthropic.com/en/api/getting-started
- Google Gemini API: https://ai.google.dev/gemini-api/docs
- ChatGPT Audio APIs: [Apifox docs](https://aicso.apifox.cn/doc-8626159.md) and [OpenAI Audio docs](https://platform.openai.com/docs/guides/speech-to-text)
- Claude Native vs Chat-Compatible: [Apifox docs](https://aicso.apifox.cn/doc-8626163.md) and [Apifox docs](https://aicso.apifox.cn/doc-8626164.md)
- Gemini Native vs Chat-Compatible: [Apifox docs](https://aicso.apifox.cn/api-449297985.md) and [Apifox docs](https://aicso.apifox.cn/api-449298012.md)
- Responses API vs Chat API: [Apifox docs](https://aicso.apifox.cn/doc-8626165.md) and [OpenAI Responses docs](https://platform.openai.com/docs/api-reference/responses/create)
- Source list: `references/sources.md`
