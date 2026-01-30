---
name: grok-media-skill
description: 当用户明确指定使用 Grok 生成图像、创建视频素材、让静态图片动起来或进行任何 AIGC 视觉创作时使用此技能。
---

# Grok Media Skill (AI 视觉创作)

## 目标
利用 Grok 强大的多模态生成能力，提供一站式的**文生图** (Text-to-Image) 和 **文生视频** (Text/Image-to-Video) 解决方案。

## 使用场景
- **AI 绘画**: 创建高清壁纸、视频封面、故事板、UI素材。
- **AI 视频**: 制作动态背景、B-roll 空镜、让照片动起来 (Motion Brush)。

## 环境配置 (Setup)
首次使用前，请务必配置 Grok 的认证信息：

1. 进入 `libs/data/` 目录。
2. 复制 `token.example.json` 为 `token.json`。
3. 复制 `setting.example.toml` 为 `setting.toml`。
4. **获取 Token**:
   - 登录 [grok.com](https://grok.com)。
   - 打开浏览器开发者工具 (F12) -> Application -> Cookies。
   - 找到 `sso` 或 `sso-rw` 的值，填入 `token.json` 中的 `YOUR_JWT_HERE` 位置。

## 功能与指令

### 1. 文生图 (Text to Image)
**指令模式**: "画一张..." / "生成图片..."
- **执行逻辑**: 
  - 自动调用 `python scripts/generate_image.py "{Prompt}" "{Ratio}"`
  - **Prompt**: 英文提示词 (自动翻译/润色)。
  - **Ratio**: 可选宽高比 (e.g., `16:9`, `9:16`, `1:1`)。

### 2. 文生视频 (Text to Video)
**指令模式**: "生成一段视频..." / "制作关于...的视频"
- **执行逻辑**:
  - 调用 `python scripts/generate_video.py "{Prompt}" "{Ratio}"`
  - 流程: `Prompt` -> 自动生成底图 -> 转化为视频。

### 3. 图生视频 (Image to Video)
**指令模式**: "让这张图动起来..." / "基于这张图生成视频..."
- **执行逻辑**:
  - 调用 `python scripts/generate_video.py "{MotionPrompt}" "{ImagePath}"`
  - **MotionPrompt**: 描述动作 (e.g., "Camera pans left, slow motion")。
  - **ImagePath**: 本地图片路径 (必须是绝对路径)。

## 注意事项
- 生成过程可能需要 1-2 分钟，请耐心等待。
- 生成的素材将保存在当前工作区的 `generated_assets` 文件夹中。
- **Token 配置**: 请确保 `libs/data/token.json` 配置正确。

## 示例
**场景**: 制作一个赛博朋克城市的动态背景。
1. **文生图**: "Generate a cyberpunk city street at night, neon lights, 16:9"
   -> 输出: `.../output/grok_172000.jpg`
2. **图生视频**: "Camera moves forward through the street, rain falling" (使用上一步的图片)
   -> 输出: `.../output/video_172005.mp4`
