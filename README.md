# Grok Media Skill (AI 视觉创作)

本技能利用 Grok (目前已支持 Grok 4) 强大的多模态及视频生成能力，提供一站式的 **文生图**、**文生视频** 及 **图生视频** 解决方案。

## ⚠️ 重要说明
该技能**仅在用户明确指定使用 "Grok"** 时被调用。由于 Grok 官方具有极强的 Cloudflare 防护，配置不当会导致 403 被拦截。

## 🌟 核心能力
- **文生图**: 极高审美风格的 AI 绘画（默认使用 Grok 4 模型）。
- **文生视频**: 自动完成 "提示词 -> 底图 -> 动画" 的完整流，支持各种画幅。
- **图生视频**: 支持 Motion Brush 逻辑，利用 Grok 的视频生成能力让静态图片动起来。

## 🛠️ 环境与配置指南

### 1. 安装 Skill

请在您的项目根目录下，打开终端 (Terminal) 运行以下命令：
```bash
git clone https://github.com/luoluoluo22/grok-media-skill.git .agent/skills/grok-media-skill
```

### 2. 配置文件准备
进入 `.agent/skills/grok-media-skill/libs/data/` 目录：
- 将 `token.example.json` 复制并重命名为 `token.json`。
- 将 `setting.example.toml` 复制并重命名为 `setting.toml`。

### 3. 获取认证信息 (Cookie & Token)
1. 登录 [grok.com](https://grok.com)。
2. 按 `F12` 打开开发者工具 -> **Application** -> **Cookies**：
    - **`sso` / `sso-rw`**: 复制其 JWT 字符串，填入 `token.json`。
    - **`cf_clearance`**: 复制该值，填入 `setting.toml` 的 `cf_clearance` 字段。
3. **获取完整 Cookie 字符串** (推荐):
    - 在网络请求 (Network) 中找到任意一个 `new` 或 `conversations` 请求。
    - 复制请求头中的完整 `Cookie: ...` 字符串，填入 `setting.toml` 的 `cookie` 字段，这能极大地提高稳定性。

### 4. 环境同步 (防拦截关键)
Grok 会校验请求指纹，请务必在 `setting.toml` 中配置以下项：
- **`proxy_url`**: 如果您在浏览器端使用了代理，请在此处填入相同的代理地址 (如 `http://127.0.0.1:7890`)。
- **`user_agent`**: 将其更新为您当前浏览器的真实 UA (可在控制台输入 `navigator.userAgent` 获取)。
- **`dynamic_statsig`**: 建议设为 `true` 以自动绕过静态特征检测。

## 🔍 连接验证
配置完成后，运行测试脚本进行验证：
```powershell
python .agent/skills/grok-media-skill/scripts/test_chat.py "Hello, Grok 4!"
```
如果能看到文字输出，说明连接成功。

## 📖 技能使用 (AI 对话)
请注意，该技能具有最高针对性，只有当您**明确指出使用 Grok** 时才会生效。

### 🗣️ 试试这样问 AI
- **文生图**: "用 Grok 画一幅油画风格的森林，16:9 画幅。"
- **文生视频**: "使用 Grok 制作一段赛博朋克城市延时摄影视频，16:9。"
- **图生视频**: "参考这张图片，用 Grok 让它动起来，镜头向左横移。"

## 📂 目录结构
- `scripts/`: 文生图、文生视频核心逻辑，及测试脚本。
- `libs/`: Grok API 客户端封装与认证库。
- `generated_assets/`: 生成的图片与视频默认保存路径。
- `libs/data/`: 存放 Token 和 Setting 的敏感数据目录（已加入 .gitignore）。

## ❓ 常见问题 (FAQ)
- **Q: 遇到 403 错误怎么办？**
  A: 通常是 IP 发生了变动或 `cf_clearance` 失效。请重新获取 Cookie，并确保 `proxy_url` 配置正确，使脚本出口 IP 与浏览器一致。
- **Q: 生成速度慢？**
  A: Grok 生成模型通常需要 30-60 秒，尤其是视频生成。请耐心等待进度提示。
