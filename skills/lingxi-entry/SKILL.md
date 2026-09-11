---
name: lingxi-entry
description: Use when the user needs help with Lingxi API Gateway setup, configuration, or routing. Trigger when the user asks to (1) configure or set up the Lingxi API, (2) upload a local image file to the image bed, (3) choose a token group or model, (4) check pricing or group differences, or (5) the user's request is vague and needs routing to the correct skill (chat, image, video, audio).
---

Category: task

# Lingxi Entry

> This skill handles configuration, image upload, and routing for the Lingxi API Gateway. It is a third-party skill, not affiliated with Lingxi official.

## When to Use

- User asks how to set up or configure the Lingxi API
- User provides a local image file that needs uploading before use with other skills
- User asks which model or token group to choose
- User's request is vague (e.g., "use Lingxi" without specifying chat/image/video/audio)
- User needs token/key management operations

## Configuration

### API Key

1. Check environment variable `LINGXI_API_KEY`. If not set, ask the user:
   > "请提供你的灵汐 API Key（从 https://api.aicso.top 注册后，在「控制台 → API 令牌」页面创建）"
2. Key format: starts with `sk-`
3. Base URL: `https://api.aicso.top/v1`

### Token Group Quick Guide

If the user asks which group to choose, give a simple recommendation:

| Use Case | Recommended Group | Why |
|----------|------------------|-----|
| General chat, cheapest option | default (默认) | ×1 rate, covers most models |
| Must use official OpenAI API | Official Relay (官转) | ×3 rate, official source |
| Claude Code | Claude Code Exclusive | ×1.5 rate, designed for Claude Code |
| Gemini models | Premium Gemini (优质gemini) | ×1 rate, Google channel |
| Domestic models (DeepSeek, Qwen) | Enterprise High-Availability | ×1 rate, stable |
| Budget constrained | Limited-Time Special (限时特价) | ×0.6 rate, covers basics |

> Full group details are available at `https://api.aicso.top`. Most users should just use **default**.

### Claude Code Setup

If user asks how to configure Claude Code with Lingxi:

```bash
export ANTHROPIC_AUTH_TOKEN=sk-...
export ANTHROPIC_BASE_URL=https://api.aicso.top
export API_TIMEOUT_MS=300000
```

Token group: **Claude Code Exclusive** or **Official Relay Claude 3**.

## Image Bed Upload

**Use this whenever a local image file needs to be used with any Lingxi skill.**

The image bed converts local files to public URLs automatically. **No API key required.**

### Upload

```python
import requests

def upload_image(file_path: str) -> str:
    """Upload a local image to the Lingxi image bed and return the public URL."""
    url = "https://imageproxy.zhongzhuan.chat/api/upload"
    with open(file_path, "rb") as f:
        response = requests.post(url, files={"file": f}, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["url"]  # e.g., "https://imageproxy.zhongzhuan.chat/api/proxy/image/..."
```

### Usage Notes

- Supported formats: JPG, PNG, GIF, WebP
- Recommended max size: 10MB
- Returned URLs are long-term valid and support cross-origin access
- Use the returned URL directly in `image_url` fields for Midjourney, Kling, Vidu, etc.
- When downloading the image URL, use GET (HEAD may return 404)

## Routing Table

When the user's intent is clear, route to the appropriate skill:

| User Needs | Skill | Example Prompt |
|-----------|-------|---------------|
| Chat, vision, web search, embeddings, TTS/ASR | `lingxi-chat` | "和 GPT-4o 聊天" / "分析这张图片" |
| Generate/edit images | `lingxi-image` | "生成一张赛博朋克城市图" |
| Generate/edit videos | `lingxi-video` | "基于这张图生成 5 秒视频" |
| Music, TTS, voice clone | `lingxi-audio` | "生成一段太空电子音乐" |
| Token management, usage query | `lingxi-system` | "查余额" / "新建令牌" |

## Error Handling

| Code / Message | Meaning | What to Do |
|------|---------|-----------|
| 401 | API Key invalid | Ask user to check their key |
| 429 | Rate limited | Wait a few seconds and retry |
| 413 | File too large | Compress image or use a smaller file |
| 500/503 | Server error | Retry once; if persists, inform user it's an upstream issue |
| "无可用渠道" | Group doesn't support this model | Suggest switching token group or using a different model |
| "Invalid URL" | Wrong endpoint path | OpenAI-compatible uses `/v1/...`; native endpoints use root path without `/v1` |
| "上游负载已饱和" | Upstream overloaded | Retry later |

## Scenario Workflows (Examples)

> The following are example automation ideas. They are not hardcoded pipelines—Claude should adapt them based on the user's actual request.

### Marketing Asset Pipeline (Image → Video → Audio)

When user says: "帮我做营销素材" / "我要做广告视频" / "生成推广内容"

1. Ask user for theme, style, and duration (default 5s for video)
2. Call `lingxi-image` to generate a poster image
3. Upload the generated image via image bed if needed
4. Call `lingxi-video` with the image URL (platform: Kling by default)
5. Call `lingxi-audio` for background music if user wants (platform: Suno)
6. Return all asset URLs to the user with descriptions

### Knowledge Base + Voice Response

When user says: "做个客服问答" / "语音回复" / "知识库加语音"

1. Ask user for knowledge base documents or topics
2. Use `lingxi-chat` with RAG/context to answer questions
3. Use `lingxi-audio` TTS to convert answers to speech
4. Return both text answer and audio file URL

### Image Analysis Pipeline

When user says: "分析这张图" / "看懂这张截图" / "提取图片里的文字"

1. If user provides a local image path, upload via image bed first
2. Call `lingxi-chat` vision with the URL
3. If structured extraction needed, ask user what fields they want
4. Return analysis results

## Validation

```bash
mkdir -p output/lingxi-entry
echo "validation_ok" > output/lingxi-entry/validate.txt
```

Pass criteria: command exits 0.

## Output And Evidence

- Save configuration notes and upload results to `output/lingxi-entry/`
- Include uploaded image URLs in evidence for traceability

## References

- Lingxi dashboard: https://api.aicso.top
- API docs: https://aicso.apifox.cn
- Image bed docs: https://aicso.apifox.cn/doc-8626237.md
