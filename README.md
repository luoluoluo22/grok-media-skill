# Grok Media Skill (AI 视觉创作)

本技能利用 Grok 3 的多模态能力，提供一站式的 **文生图**、**文生视频** 及 **图生视频** 解决方案。

## ⚠️ 重要说明
该技能**仅在用户明确指定使用 "Grok"** 时被调用。常规对话或通用绘图请求将优先分配给 `antigravity-api-skill`。

## 🌟 核心能力
- **文生图**: 高审美风格的 AI 绘画。
- **文生视频**: 自动完成 "提示词 -> 底图 -> 动画" 的完整流。
- **图生视频**: 支持 Motion Brush，让静态图片动起来。

## 🛠️ 配置指南

### 1. 安装 Skill

请在您的项目根目录下，打开终端 (Terminal) 运行以下命令：
```bash
git clone https://github.com/luoluoluo22/grok-media-skill.git .agent/skills/grok-media-skill
```

### 2. 获取 Token
*   登录 [grok.com](https://grok.com)。
*   在 F12 控制台 -> Application -> Cookies 中找到 `sso` 或 `sso-rw` 的值。

### 3. 填入配置
*   进入 `libs/data/` 目录。
*   将 Token 填入 `token.json` 中的 `YOUR_JWT_HERE` 字段。

### 4. 连接验证
配置完成后，您可以直接在 AI 助手中发送指令：
> "Grok 插件配置好了吗？画一个酷炫的机器人试试。"

---

## 📖 技能使用 (AI 对话)
请注意，该技能具有最高针对性，只有当您**明确指出使用 Grok** 时才会生效。

### 🗣️ 试试这样问 AI
- **文生图**: "用 Grok 画一幅油画风格的森林，16:9 画幅。"
- **文生视频**: "使用 Grok 制作一段赛博朋克城市延时摄影视频，16:9。"
- **图生视频**: "参考这张图片，用 Grok 让它动起来，镜头向左横移。"

## 📂 目录结构
- `scripts/`: 文生图、文生视频核心逻辑。
- `libs/`: Grok API 客户端封装。
- `generated_assets/`: 默认输出路径。
