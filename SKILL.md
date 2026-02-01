---
name: grok-media-skill
description: 当用户明确指定使用 Grok 生成图像、创建视频素材、让静态图片动起来或进行任何 AIGC 视觉创作时使用此技能。
---

# Grok Media Skill (AI 视觉创作)

## 目标
利用 Grok (支持 Grok 4) 强大的多模态生成能力，提供一站式的**文生图** (Text-to-Image) 和 **文生视频** (Text/Image-to-Video) 解决方案。

## 使用场景
- **AI 绘画**: 创建高清壁纸、视频封面、故事板、UI素材。
- **AI 视频**: 制作动态背景、B-roll 空镜、让照片动起来 (Motion Brush)。

## 环境配置 (Setup)
首次使用前，请务必配置 Grok 的认证信息。注意：Grok 具有严厉的 Cloudflare 防火墙。

1. 进入 `libs/data/` 目录。
2. 复制 `token.example.json` 为 `token.json`。
3. 复制 `setting.example.toml` 为 `setting.toml`。
4. **获取认证信息**:
   - 登录 [grok.com](https://grok.com)。
   - 打开浏览器开发者工具 (F12) -> Application -> Cookies。
   - 找到 `sso` 或 `sso-rw` 的值，填入 `token.json`。
   - 找到 `cf_clearance` 并复制完整 Cookie 字符串填入 `setting.toml` 的 `cookie` 字段。
5. **环境同步**:
   - 如果使用了代理，必须在 `setting.toml` 中配置 `proxy_url`。
   - 确保 `setting.toml` 中的 `user_agent` 与实际浏览器一致。

## 功能与指令

### 1. 文生图 (Text to Image)
**指令模式**: "用 Grok 画一张..." / "使用 Grok 生成图片..."
- **执行逻辑**: 
  - 自动调用 `python scripts/generate_image.py "{Prompt}" "{Ratio}"`
  - **Prompt**: 核心描述词。
  - **Ratio**: 宽高比 (e.g., `16:9`, `9:16`)。

### 2. 文生视频 (Text to Video)
**指令模式**: "用 Grok 生成一段视频..." / "Grok 制作关于...的视频"
- **执行逻辑**:
  - 调用 `python scripts/generate_video.py "{Prompt}" "{Ratio}"`

### 3. 图生视频 (Image to Video)
**指令模式**: "让这张图用 Grok 动起来..." / "基于这张图用 Grok 生成视频..."
- **执行逻辑**:
  - 调用 `python scripts/generate_video.py "{MotionPrompt}" "{ImagePath}"`

## 注意事项
- **Cloudflare 拦截**: 如果脚本运行报错 403，通常是由于 IP 变动或 Cookie 失效。请检查 `setting.toml` 中的 `proxy_url` 是否与浏览器一致。
- **生成时长**: 生成过程可能需要 1-2 分钟，请耐心等待。
- **本地存储**: 生成的素材保存在工作区的 `generated_assets` 文件夹中。

## 示例
**场景**: 制作一个赛博朋克城市的动态背景。
1. **文生图**: "Use Grok to generate a cyberpunk city street at night, neon lights, 16:9"
2. **图生视频**: "Using Grok, make the camera move forward through the street, rain falling" (指向上一步生成的图片)
