# 灵汐 API Gateway Skills

## 快速入口

[快速开始](#快速开始) | [技能索引](#技能索引) | [项目结构](#项目结构)

将多平台 AI 能力折叠进你的代码和工作流。

这是一个精选的 **灵汐 API Gateway Skills** 集合，覆盖聊天、绘画、视频、音频和系统管理，帮助开发者快速对接 OpenAI、Claude、Gemini、Midjourney、Kling、Suno 等数十个模型平台。

## 最新覆盖

- 统一异步轮询器 `scripts/async_polling.py` 已支持 15 个平台的状态码自动适配。
- 所有技能已补充「上传需求表格」，清晰标注每个模型需要什么上传方式（base64 / 本地文件 / URL / 图床）。
- 图床 API 已实测验证可用，无需 API Key，支持 JPG/PNG/GIF/WebP。

## 快速开始

### 1. 获取令牌

1. 访问 [灵汐控制台](https://api.aicso.top) 注册账号
2. 进入「令牌」页面 → 点击「添加令牌」
3. 选择分组（不同分组对应不同模型和价格倍率）
4. 复制生成的 API Key

### 2. 配置环境变量

```bash
export LINGXI_API_KEY="你的令牌"
export LINGXI_BASE_URL="https://api.aicso.top/v1"
```

如果某些客户端无法识别 `/v1` 结尾，也可以尝试：
- `https://api.aicso.top`
- `https://api.aicso.top/v1/chat/completions`

### 3. 安装 SDK（以 Python 为例）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install openai requests
```

### 4. 发起第一个请求

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("LINGXI_API_KEY"),
    base_url=os.getenv("LINGXI_BASE_URL"),
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello, Lingxi!"}],
)
print(response.choices[0].message.content)
```

## 示例（独立技能与提示词）

### 1) 基础对话

- 提示词：
  "用 `lingxi-chat` 发起一个基础对话，模型选 `gpt-4o-mini`，消息内容：'今天天气怎么样？'"

### 2) 流式输出

- 提示词：
  "用 `lingxi-chat` 开启流式对话，模型 `gpt-4o`，问 '讲一个程序员笑话'，逐字输出。"

### 3) Function Calling

- 提示词：
  "用 `lingxi-chat` 演示 Function Calling，查询北京天气，返回函数名和参数。"

### 4) 图片生成（DALL-E 3）

- 提示词：
  "用 `lingxi-image` 生成一张 1024x1024 的赛博朋克城市夜景图。"

### 5) 图生视频（Kling）

- 提示词：
  "用 `lingxi-video` 基于一张猫咪图片生成 5 秒视频，使用 Kling 平台。"

### 6) 音乐生成（Suno）

- 提示词：
  "用 `lingxi-audio` 在 Suno 上以自定义模式生成一首关于太空的电子音乐，提供歌词。"

### 7) 令牌管理

- 提示词：
  "用 `lingxi-system` 列出所有令牌，并创建一个新的默认分组令牌，额度 100 万。"

### 8) 多轮对话 + 图片理解

- 提示词：
  "用 `lingxi-chat` 让 GPT-4o 分析一张图片（URL: ...），描述画面内容。"

### 9)  Claude Code 配置

- 提示词：
  "用 `lingxi-entry` 告诉我如何在 Claude Code 中配置灵汐中转站。"

### 10) 图床上传

- 提示词：
  "用 `lingxi-entry` 的图床 API 上传一张本地图片，返回可用于 Kling 图生视频的 URL。"

## 组合方案（场景与提示词模板）

### 营销素材流水线（图 → 视频 → 配音）

模板：
"按以下流程串联技能：
① `lingxi-image` 生成海报图（主题：{主题}，尺寸：{尺寸}）。
② `lingxi-video` 基于上一步图片生成 {时长}s 视频（平台：Kling，提示词：{镜头描述}）。
③ `lingxi-audio` 用 Suno 生成背景音乐（风格：{风格}）。
请输出最终资产的 URL 列表与对应说明。"

### 客服知识库 + 语音应答

模板：
"用 `lingxi-chat` 加载知识库文档，做 RAG 问答；
然后用 `lingxi-audio` 的 TTS 把答案转成语音，voice=alloy。"

## 技能索引

| Skill | 描述 | 路径 |
|-------|------|------|
| `lingxi-entry` | 入口路由、认证配置、分组说明、价格倍率、多 SDK 配置、图床 API、Realtime API | `skills/lingxi-entry` |
| `lingxi-chat` | 聊天、补全、Embeddings、Function Calling、Vision、音频、Web Search。支持 OpenAI / Claude / Gemini / Responses 格式 | `skills/lingxi-chat` |
| `lingxi-image` | 图片生成与编辑。支持 Midjourney、DALL-E 3、FLUX、Ideogram、Grok、GPT Image-1、Qwen、豆包、Fal.ai、Replicate、腾讯 AIGC | `skills/lingxi-image` |
| `lingxi-video` | 视频生成与编辑。支持 Veo、Luma、Runway、海螺、Sora、Grok、通义万象、腾讯、豆包、Kling、Replicate、Fal.ai、Vidu | `skills/lingxi-video` |
| `lingxi-audio` | 音乐生成、TTS、ASR、语音复刻。支持 Suno、OpenAI TTS/Whisper、MiniMax、Gemini、Realtime | `skills/lingxi-audio` |
| `lingxi-system` | 令牌与账号管理。支持 Token CRUD、批量修改、搜索、用量查询、模型列表 | `skills/lingxi-system` |

## 项目结构

```
lingxi-skills/
├── skills/
│   ├── lingxi-entry/          # 入口 & 路由
│   ├── lingxi-chat/           # 聊天 & 补全
│   ├── lingxi-image/          # 图片生成
│   ├── lingxi-video/          # 视频生成
│   ├── lingxi-audio/          # 音频 & 音乐
│   └── lingxi-system/         # 令牌管理
├── tests/
│   ├── lingxi-entry-test/
│   ├── lingxi-chat-test/
│   ├── lingxi-image-test/
│   ├── lingxi-video-test/
│   ├── lingxi-audio-test/
│   └── lingxi-system-test/
├── scripts/
│   └── async_polling.py       # 统一异步轮询器（支持 15 个平台）
├── examples/
│   ├── basic_chat.py
│   ├── streaming_chat.py
│   └── function_calling.py
├── AGENTS.md                  # 仓库规范
├── LICENSE                    # MIT
├── Makefile                   # 构建脚本
└── README.md                  # 本文件
```

## 测试

每个技能都有对应的冒烟测试：

```bash
# 验证所有 Python 脚本语法
make validate

# 运行 chat skill 测试示例
python -m py_compile skills/lingxi-chat/scripts/chat_demo.py
```

## 备注

- 本仓库聚焦灵汐 API Gateway 的核心能力及其 skill 实现。
- 所有 skill 内容使用英文编写（遵循 AGENTS.md 规范），README 使用中文以便国内开发者阅读。
- 灵汐官网：[api.aicso.top](https://api.aicso.top)
- API 文档门户：[aicso.apifox.cn](https://aicso.apifox.cn)

## 输出规范

- 所有临时文件与生成物必须写入 `output/`。
- 按技能划分子目录，例如 `output/<skill>/...`。
- `output/` 被 git 忽略，不允许提交。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=your-org/lingxi-skills&type=Date)](https://star-history.com/#your-org/lingxi-skills&Date)
