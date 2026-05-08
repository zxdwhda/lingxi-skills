---
name: lingxi-entry
description: Use when routing Lingxi API Gateway requests to the right local skill (chat, image, video, audio, system). Use when the user asks for Lingxi without specifying a capability, or needs authentication setup, base URL configuration, token management overview, rerank, or help center features.
version: 1.2.0
---

Category: task

# Lingxi API Gateway Entry (Routing)

Lingxi (灵汐) is a unified AI API gateway that aggregates multiple model providers behind a single endpoint. It provides direct mainland China access without a VPN, zero ban risk, connection speeds up to 1200x faster than official APIs, and coverage across seven global regions (US, Japan, Korea, UK, Hong Kong, Philippines, Russia).

## Base Configuration

- **Base URL**: `https://api.aicso.top`
- **Authentication**: Bearer token via `Authorization` header
- **Token management**: Create and manage tokens via the Lingxi dashboard (Console → API Tokens)

### Environment Setup

```bash
export LINGXI_API_KEY="your-lingxi-token"
export LINGXI_BASE_URL="https://api.aicso.top/v1"
```

Or in Python:

```python
import os
os.environ["LINGXI_API_KEY"] = "your-lingxi-token"
os.environ["LINGXI_BASE_URL"] = "https://api.aicso.top/v1"
```

### Alternative BASE_URL Variants

Different clients may require different BASE_URL formats. Try these in order:

```
https://api.aicso.top
https://api.aicso.top/v1
https://api.aicso.top/v1/chat/completions
```

> **Note**: All proxy endpoint addresses share the same data. The documented addresses for domestic and international access all resolve to `https://api.aicso.top`.

## Routing Table

| Need | Target skill |
| --- | --- |
| Text chat / completions / function calling / embeddings | `skills/lingxi-chat/` |
| Image generation / editing (Midjourney, DALL-E, FLUX, Ideogram, etc.) | `skills/lingxi-image/` |
| Video generation / editing (Veo, Luma, Runway, Sora, Kling, etc.) | `skills/lingxi-video/` |
| Music generation / TTS / ASR (Suno, MiniMax, etc.) | `skills/lingxi-audio/` |
| Token / key management | `skills/lingxi-system/` |
| Rerank / re-ranking | Native endpoint (see below) |

## Supported Provider Formats

Lingxi supports multiple API formats through a single gateway:

- **OpenAI-compatible** (`/v1/chat/completions`, `/v1/images/generations`, etc.)
- **Claude-compatible** (Anthropic native format + chat-compatible format)
- **Gemini-compatible** (Google native format + chat-compatible format)
- **Responses API** (OpenAI responses format)
- **Platform-native** (Midjourney, Replicate, Fal.ai, Kling official, MiniMax official, Vidu official, etc.)

## Group Overview

Tokens can be bound to specific model groups (分组) for cost control and routing. Different groups have different pricing multipliers and model availability.

### Price Transparency

Lingxi uses an "official rate × multiplier" pricing model for full transparency:

- When group rate = 1: $1 official price = $1 deducted on the platform
- When group rate = 1.65: $1 official price = $1.65 deducted on the platform
- When group rate = 0.6: $1 official price = $0.60 deducted on the platform

Users can choose the group that best fits their needs and budget.

### All 15 Groups

| Group | Type | Rate Multiplier | Supported Models |
| :--- | :--- | :--- | :--- |
| default (默认) | Mixed ChatGPT (Azure) + Claude (reverse) + MJ (fast) + Domestic (DeepSeek+Qwen) | official × 1 | OpenAI, Claude, Domestic |
| Enterprise High-Availability Large Models (企业级高可用大模型) | Domestic models (DeepSeek+Qwen) | official × 1 | Domestic |
| Premium Grok (优质grok) | Grok models (partial) | official × 5 | Grok |
| Premium Gemini (优质gemini) | Gemini (Google channel) | official × 1 | Gemini |
| Official Gemini (官转gemini) | Gemini (Google channel), more expensive (more accounts, higher cost) | official × 3 | Gemini |
| Pure Azure (纯AZ) | Only ChatGPT (Azure) + Domestic (Doubao+DeepSeek) | official × 1.5 | OpenAI, Claude, Domestic |
| Official Relay (官转) | ChatGPT (Azure) + ChatGPT (official relay) + Domestic (fallback from Azure to official relay) | official × 3 | OpenAI, Domestic |
| Official Relay OpenAI (官转OPENAI) | ChatGPT (official relay) + Azure (fallback) | official × 6 | OpenAI |
| Premium Official Relay OpenAI (优质官转OPENAI) | ChatGPT (official relay), more expensive (more accounts) | official × 8 | OpenAI |
| Reverse (逆向) | GPT + Claude + Gemini + Grok | official × 1.4 | OpenAI, Claude |
| Limited-Time Special (限时特价) | Domestic (DeepSeek+Qwen) + Gemini (Google) + ChatGPT (Azure) | official × 0.6 | Gemini, Domestic |
| Official Relay Claude 2 (官转克劳德2) | Claude (AWS official relay) | official × 6 | Claude |
| Official Relay Claude 3 (官转克劳德3) | Claude (AWS official relay + Anthropic official relay) | official × 12 | Claude |
| Direct Claude (直连克劳德) | Claude (Anthropic official relay) | official × 16 | Claude |
| Claude Code Exclusive (Claude code专属) | Claude Code | official × 1.5 | Claude Code |

### Group Comparison Summary

| Feature | Reverse | Default (Mixed) | Azure | Official Relay | Premium Official OpenAI | Premium Gemini | Official Gemini | Official Relay Claude | Direct Claude |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Pros** | Same as ChatGPT official, smarter, good price, but response differs slightly from API | Same as ChatGPT official, smarter, good price | Multiple channels, abundant backup, high volume/concurrency, no moderation, supports FC/TC | High speed, high volume/concurrency, no moderation, supports FC/TC | Same as ChatGPT official, high speed, high volume/concurrency, more accounts, more stable | Same as official, smarter, good price, high volume, stable | Same as official, smarter, good price, high volume, more stable, more accounts | From Amazon + Anthropic official, multiple channels, abundant backup, high volume/concurrency | From Anthropic official, more accounts, more stable |
| **Cons** | Non-official interface | Non-official interface | Sometimes Azure lags | Affected by official API stability | Affected by official API stability | Affected by official API stability | Higher cost, higher multiplier, affected by official API stability | Affected by official API stability | Affected by official API stability |

### Model Support by Channel

| Model Type | Reverse | Default (Mixed) | Azure | Official Relay |
|----------|------|--------------|---------------------|--------------|
| GPT-4 | Reverse, all supported | Reverse, all supported | Azure, all supported | OpenAI, all supported |
| GPT-3.5 | Reverse, all supported | Reverse, all supported | Azure, all supported | OpenAI, all supported |
| OpenAI other base models | All supported | All supported | All supported | All supported |
| Midjourney | Not supported | All supported | Not supported | Not supported |
| Domestic models | Not supported | All supported | Partially supported | Not supported |
| Claude | Reverse, all supported | All supported | All supported | Reverse, all supported |

### Channel Sources

- **ChatGPT Official Relay**: from openai.com
- **Azure Channel**: from Microsoft Azure
- **Gemini Google Channel**: from Google
- **Domestic Models**: from respective official sources
- **Claude AWS Official Relay**: from Amazon
- **Claude Anthropic Official Relay**: from Anthropic official

## How to Create a Token Bound to a Specific Group

1. Log in to the Lingxi dashboard at `https://api.aicso.top`
2. Navigate to **Console → API Tokens**
3. Click **Add Token**
4. Select the desired **Group** from the dropdown (this determines pricing and model availability)
5. Set a token name (any name you prefer)
6. Set quota (recommended: unlimited for development)
7. Keep other options as default
8. Save the token — the key starts with `sk-`

> **Important**: Some tools (e.g., Codex, Claude Code) require tokens bound to specific groups. Codex requires the "codex exclusive" group; Claude Code requires "Claude Code exclusive" or "Official Relay Claude 3" or higher.

## Standard API Request

### cURL Example

```bash
curl https://api.aicso.top/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -d '{
  "model": "gpt-4o",
  "messages": [{"role": "user", "content": "Say this is a test!"}],
  "temperature": 0.7
}'
```

### Response

```json
{
   "id":"chatcmpl-abc123",
   "object":"chat.completion",
   "created":1677858242,
   "model":"gpt-4o",
   "usage":{
      "prompt_tokens":13,
      "completion_tokens":7,
      "total_tokens":20
   },
   "choices":[
      {
         "message":{
            "role":"assistant",
            "content":"\n\nThis is a test!"
         },
         "finish_reason":"stop",
         "index":0
      }
   ]
}
```

## Python

### Basic Chat

```bash
pip install openai
```

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.aicso.top/v1",
    api_key="sk-xxxx"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Hello?"}
    ],
    timeout=100,
)
print(response)
```

### Using Environment Variables

```python
import openai

openai.api_base = "https://api.aicso.top/v1"
openai.api_key = "sk-xxxxxxxxx"
```

Or set environment variables:

```bash
export OPENAI_API_BASE=https://api.aicso.top/v1
export OPENAI_API_KEY=sk-xxxxx
```

### Responses API

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.aicso.top/v1",
    api_key='your-api-key',
    timeout=120
)

response = client.responses.create(
    model="gpt-5",
    input="Write a one-sentence bedtime story about a unicorn."
)
print(response.output_text)
```

### Function Calling

```python
from openai import OpenAI
import json

client = OpenAI(
    base_url="https://api.aicso.top/v1",
    api_key="sk-xxxxx"
)

def get_current_weather(location, unit="fahrenheit"):
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

messages = [{"role": "user", "content": "What's the weather like in San Francisco?"}]
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)
print(response.choices[0].message)
```

## LangChain

```bash
pip install langchain_openai langchain
```

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    openai_api_base="https://api.aicso.top/v1",
    openai_api_key="sk-xxxxx"
)

res = llm.invoke("hello")
print(res.content)
```

Legacy LangChain (via environment variables):

```bash
export OPENAI_BASE_URL="https://api.aicso.top/v1"
export OPENAI_API_KEY="sk-xxxxx"
```

## LlamaIndex

```python
from llama_index.llms.openai import OpenAI

llm = OpenAI(
    model="gpt-3.5-turbo",
    api_key="sk-xxxxx",
    api_base="https://api.aicso.top/v1"
)
ret = llm.complete("Paul Graham is ")
print(ret)
```

## Claude Code Configuration

### System Requirements
- Node.js ≥ 18.0
- macOS, Linux, or Windows (WSL)

### Installation

```bash
npm install -g @anthropic-ai/claude-code
```

### Environment Variables

Linux/macOS:
```bash
export ANTHROPIC_AUTH_TOKEN=sk-...
export ANTHROPIC_BASE_URL=https://api.aicso.top
export API_TIMEOUT_MS=300000  # 300 seconds
```

Windows PowerShell:
```powershell
$env:ANTHROPIC_BASE_URL = "https://api.aicso.top"
$env:ANTHROPIC_AUTH_TOKEN = "sk-..."
$env:API_TIMEOUT_MS = "300000"
```

Windows CMD:
```cmd
set ANTHROPIC_BASE_URL=https://api.aicso.top
set ANTHROPIC_AUTH_TOKEN=sk-...
set API_TIMEOUT_MS=300000
```

### Token Setup Notes
- Group: select "Claude Code exclusive" or "Official Relay Claude 3" or higher
- Quota: recommended unlimited
- The gateway only supports Claude Code API traffic, not general API calls

## Gemini CLI Configuration

### Installation

```bash
# Global install
npm install -g @google/gemini-cli

# Or via Homebrew (macOS/Linux)
brew install gemini-cli

# Or run without installing
npx https://github.com/google-gemini/gemini-cli
```

### Environment Variables

```bash
export GEMINI_API_KEY=sk-xxxxx
export GOOGLE_GEMINI_BASE_URL=https://api.aicso.top
```

Windows CMD:
```cmd
set GEMINI_API_KEY=sk-xxxxx
set GOOGLE_GEMINI_BASE_URL=https://api.aicso.top
```

### Basic Usage

```bash
# Start in current directory
gemini

# Use specific model
gemini -m gemini-2.5-flash

# Non-interactive mode
gemini -p "Explain this codebase architecture"
```

## Other Client Configurations

### Cline
- API URL: `https://api.aicso.top`
- **Note**: Only Pure Azure, Official Relay Claude 2, Official Relay Claude 3, and Direct Claude groups support function calling.

### Cursor
- API URL: `https://api.aicso.top`

### ChatBox (Recommended)
- Download: https://github.com/Bin-Huang/chatbox/releases
- Set proxy to `https://api.aicso.top` and enter your API key in settings.

### OpenClaw
1. Install: `npm install -g openclaw@latest`
2. Run onboard: `openclaw onboard`
3. Configure `~/.openclaw/openclaw.json` with provider base URLs pointing to `https://api.aicso.top/v1` or `https://api.aicso.top`
4. Set API keys in `auth-profiles.json`
5. Start gateway: `openclaw gateway --port 18789`

## Realtime API (WebSocket)

```python
# pip install websocket-client
import json
import websocket

url = "ws://api.aicso.top/v1/realtime?model=gpt-4o-realtime-preview"
headers = [
    "Authorization: Bearer sk-xxx",
    "OpenAI-Beta: realtime=v1"
]

def on_open(ws):
    event = {
        "type": "response.create",
        "response": {
            "modalities": ["text"],
            "instructions": "Please assist the user."
        }
    }
    ws.send(json.dumps(event))

def on_message(ws, message):
    data = json.loads(message)
    print(json.dumps(data, ensure_ascii=False, indent=2))

ws = websocket.WebSocketApp(
    url,
    header=headers,
    on_open=on_open,
    on_message=on_message
)
ws.run_forever()
```

## Rerank Model

**Endpoint**: Native rerank endpoint via Lingxi proxy

- Given a prompt/query and a list of documents, returns reordered results with relevance scores.
- Model: rerank model (check the Lingxi model list for exact model names)
- Request: `query` + `documents` array
- Response: ranked list with `index`, `score`, `document`

Reference: https://aicso.apifox.cn/api-449298156.md

## HTTP Status Codes

| Status Code | Meaning | Explanation |
|-------------|---------|-------------|
| 400 | Bad Request | Request format is incorrect or cannot be understood by the server. Usually a client-side error. |
| 401 | Unauthorized | API key verification failed. Verify your API key is correct; other causes include token expiration. |
| 403 | Forbidden | Generally indicates insufficient permissions. |
| 404 | Not Found | The requested resource was not found. You may be trying to access a non-existent endpoint. |
| 413 | Request Entity Too Large | Request body is too large. Reduce your request body size. |
| 429 | Too Many Requests | Rate limit exceeded due to frequent requests. |
| 500 | Internal Server Error | Server internal error. Usually an upstream provider issue, not your fault. |
| 503 | Service Unavailable | Server temporarily unavailable. May be due to maintenance or server overload. |

> **Note**: The above is a partial list. Some status codes may vary depending on server implementation.

## AI Thinking Fields

Some models return thinking/reasoning content alongside the final response.

In streaming responses:

```json
{
  "choices": [{
    "delta": {
      "content": "",
      "reasoning_content": "thinking content...",
      "role": "assistant"
    },
    "index": 0
  }]
}
```

- `reasoning_content`: The model's chain-of-thought / reasoning content
- `content`: The final reply content
- `reasoning`: Gemini models return thinking content in this field

Reverse-engineered models wrap thinking content with `<think>` tags:
```
<think>thinking content</think>
```

## Image Bed API

Upload images to Lingxi's hosted image bed for use in subsequent API calls.

**Endpoint**: `POST https://imageproxy.zhongzhuan.chat/api/upload`
**Content-Type**: `multipart/form-data`

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | File | Yes | Image file to upload |

### cURL Example

```bash
curl -X POST \
  https://imageproxy.zhongzhuan.chat/api/upload \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/your/image.jpg'
```

### Python Example

```python
import requests

url = "https://imageproxy.zhongzhuan.chat/api/upload"
files = {'file': open('image.jpg', 'rb')}

response = requests.post(url, files=files)
print(response.json())
```

### Response

```json
{
    "url": "https://imageproxy.zhongzhuan.chat/api/proxy/image/2316ce07a01000cf14a628c8b29e97a8",
    "created": 1757403998946
}
```

- `url` (string): Publicly accessible image URL (long-term valid)
- `created` (number): Creation timestamp in milliseconds

### Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Request parameter error (e.g., no file provided) |
| 413 | File too large |
| 415 | Unsupported file format |
| 500 | Server internal error |

### Notes
- Supported formats: JPG, PNG, GIF, WebP, and other common image formats
- Recommended max file size: 10MB per file
- Returned URLs support cross-origin access
- **No API key required** for upload
- **Access with GET**: When downloading the image URL, use a GET request (HEAD requests may return 404)
- **User-Agent**: Include a `User-Agent` header if you encounter access issues
- Use this URL directly in `image_url` fields for Midjourney, Kling, Vidu, and other platforms requiring image URLs
- Images are processed through a proxy service for stable access

## Help Center Features

### New User Benefits
- New users receive **$0.20** free trial credit upon registration
- Minimum recharge amount: **$1**
- Register at: `https://api.aicso.top/register`

### Token Features
- One API key works for all models
- API keys can have usage time and quota limits
- 100% value-preserving rebind support
- Usage records viewable in real-time, retained for 30 days

## Validation

```bash
mkdir -p output/lingxi-entry
echo "validation_placeholder" > output/lingxi-entry/validate.txt
```

Pass criteria: command exits 0 and `output/lingxi-entry/validate.txt` is generated.

## Output And Evidence

- Save artifacts, command outputs, and API response summaries under `output/lingxi-entry/`.
- Include key parameters (model, endpoint, time range) in evidence files for reproducibility.

## Workflow

1) Confirm user intent, target format (OpenAI/Claude/Gemini/native), and whether the operation is read-only or mutating.
2) Run one minimal read-only query first to verify connectivity and permissions.
3) Execute the target operation with explicit parameters and bounded scope.
4) Verify results and save output/evidence files.

## References

- API docs portal: `https://aicso.apifox.cn/`
- Token dashboard: `https://api.aicso.top`
- Rerank: https://aicso.apifox.cn/api-449298156.md
- HTTP status codes: https://aicso.apifox.cn/doc-8626236.md
- AI thinking fields: https://aicso.apifox.cn/doc-8626235.md
- Image bed: https://aicso.apifox.cn/doc-8626237.md
