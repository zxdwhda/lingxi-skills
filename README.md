# Claude Code × 灵汐 API 技能包

> ⚠️ **第三方社区项目，与灵汐（Lingxi）官方无关。**
> **内容已通过 API 实测验证，但模型可用性随时可能变化，请以灵汐控制台实时状态为准。**

一套面向 **Claude Code / 小龙虾** 用户的技能集合。安装后，用自然语言对话即可调用 GPT-4o、Claude、Gemini、Kling、Suno 等模型，无需手写代码、无需自己配图床。

**核心卖点**：
- 🔌 放入 `.claude/skills/` 直接生效
- 🖼️ 本地图片自动上传图床，**无需配置 OSS**
- 🇨🇳 国内直连，无需代理
- 🤖 统一 OpenAI 格式调用多平台，小白只需学一种写法

---

## 适合谁用 / 不适合谁用

| ✅ 适合 | ❌ 不适合 |
|--------|----------|
| 想让 Claude 直接帮你调用各种 AI 模型 | 需要 100% 官方保证的开发者 |
| 不想配图床、不想写代码 | 需要批量管理 API Token 的高级用户 |
| 国内网络，不想翻墙 | 对模型名/端点精确度要求极高的生产环境 |

---

## 快速安装

```bash
# 1. 克隆到本地
git clone https://github.com/your-org/lingxi-skills.git

# 2. 复制技能到 Claude Code skills 目录
cp -r lingxi-skills/skills/* ~/.claude/skills/

# 3. 设置 API Key（从 https://api.aicso.top 注册获取）
export LINGXI_API_KEY="sk-xxxxx"
```

完成。现在可以直接对 Claude 说：

> "帮我生成一张赛博朋克风格的图片"  
> "用 GPT-4o 分析这张截图"  
> "基于这张图生成一段 5 秒的视频"

---

## 包含技能

| Skill | 触发话术 | 能力 |
|-------|---------|------|
| `lingxi-entry` | "怎么配置？" / "上传这张图片" | 入口配置、图床上传、路由引导 |
| `lingxi-chat` | "聊天" / "识图" / "联网搜索" | 文本对话、图片理解、TTS、ASR、Embeddings |
| `lingxi-image` | "生成图片" / "画一张..." | DALL-E 3、FLUX、Midjourney 等 |
| `lingxi-video` | "生成视频" / "图生视频" | Kling、Sora、Veo、MiniMax 等 |
| `lingxi-audio` | "生成音乐" / "文字转语音" | Suno、TTS、语音克隆 |
| `lingxi-system` | "查余额" / "新建令牌" | 令牌管理、用量查询（需管理员 Key） |

---

## 使用示例

**图片理解（直接拖拽本地图片）**
> "分析这张截图里的数据表格，告诉我哪个季度增长最快。"

**多模态内容生成**
> "我要做一个咖啡广告：先画一张海报，然后基于海报生成 5 秒视频，再配一段轻音乐。"

**语音合成**
> "把这段文字转成语音，用温柔的女声。"

---

## ⚠️ 已知限制

1. **分组影响模型可用性**  
   灵汐的不同令牌分组支持不同模型。如果调用返回"无可用渠道"，说明当前分组不支持该模型，需要换分组或换模型。

2. **端点分两类**
   - **OpenAI 兼容**：`https://api.aicso.top/v1/...`（聊天、图片生成、TTS、Embeddings）
   - **Native 原生**：`https://api.aicso.top/...`（Kling、Suno、MiniMax、Midjourney 等）  
   Skill 里已自动区分，Claude 会按正确格式调用。

3. **图片生成返回 base64**  
   灵汐中转站大多数图片模型返回 base64 编码而非 URL，Skill 已包含自动解码保存逻辑。

4. **视频生成均为异步任务**  
   所有视频平台都需要"提交 → 轮询 → 获取结果"，Claude 会自动处理轮询。

5. **非官方项目**  
   本仓库由社区维护，与灵汐官方无隶属关系。如有 API 层面的问题，请直接联系灵汐客服。

---

## 项目结构

```
skills/
├── lingxi-entry/     # 配置入口 + 图床上传
├── lingxi-chat/      # 聊天 / 识图 / 搜索 / 语音
├── lingxi-image/     # 图片生成
├── lingxi-video/     # 视频生成
├── lingxi-audio/     # 音乐 / TTS / 语音克隆
└── lingxi-system/    # 令牌管理
```

---

## 相关链接

- 灵汐控制台（获取 API Key）：https://api.aicso.top
- 灵汐 API 文档：https://aicso.apifox.cn
- 端点速查表（本项目整理）：[相关文档.md](相关文档.md)
- 本项目 License：MIT
