# NOTICE — 第三方素材来源与许可

本项目（[leetcode-whale-reminder](https://github.com/lotusmi01/leetcode-whale-reminder)）的**自有代码**按 [PolyForm Noncommercial License 1.0.0](LICENSE) 授权。

但本仓库中随附的**美术素材（图片 / 音效）与部分文案**来自第三方，**不在本项目的 LICENSE 覆盖范围内**，其权利与许可情况如下。使用这些素材时请遵守下列说明。

## 一、素材来源

| 本项目文件 | 来源 | 说明 |
| --- | --- | --- |
| `whale_girl.png`、`whale_girl_flip.png`、`whale_girl.ico` | [MeteorNOX/DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget) 的 `assets/DSniang1.png`（及其衍生裁切） | 由本项目用 `convert_mascot.py` 去背景 / 裁切 / 缩放，并生成镜像图与图标 |
| `Ya1.mp3`、`Ya2.mp3`、`D1.mp3`、`D2.mp3` | 同上插件的 `assets/` | 插件的内置按压 / 松开音效 |
| `leetcode_whale.py` 中的 `CLICK_PHRASES` 点击台词 | 同上插件的「随机语句」默认文案 | 文字内容 |

## 二、原作者的许可范围（原文摘录）

来自该插件的 [`PROVENANCE.md`](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget/blob/main/PROVENANCE.md)：

> 本仓库的**代码**按 MIT 许可。`assets/` 目录下的**美术素材**（图片 / 动图 / 音效）**不在 MIT 覆盖范围内**，按下面的说明「原样提供」。
>
> | 范围 | 许可 |
> |---|---|
> | `assets/**`（图片 / 动图 / 音效） | **不适用 MIT**：由维护者提供或使用 AI 工具生成，按 **as-is** 随插件分发，仅用于运行本插件；**不授予再许可**，也不声明为原创作品。 |

其中 `DSniang1.png` 被该文档标注为「**AI 工具生成**的图像，经人工挑选与裁切」，生成工具与原始出处**已不可考**（元数据已剥离）。

## 三、重要声明

1. **不构成再授权**：本仓库随附的上述素材，**并未**从原作者处获得再分发的明确许可。本项目的 LICENSE（PolyForm Noncommercial）**不适用于**这些素材，也**不表示**本项目对它们拥有任何权利。
2. **非官方**：本项目是个人学习性质的第三方项目，与 **DeepSeek**、**DeepSeek Harness（DSH）** 及上述插件的作者**均无隶属、赞助或背书关系**。"DeepSeek" 等名称与标识的相关权利归其各自所有者。
3. **仅供个人非商业用途**：请勿将本项目或其素材用于商业用途。
4. **权利主张 / Takedown**：如果你是上述素材的权利人，认为本仓库的使用侵犯了你的权利，请在[本仓库开一条 issue](https://github.com/lotusmi01/leetcode-whale-reminder/issues) 说明**文件名**与**依据**，我们会在核实后**立即替换或移除**，不附加其它条件。
5. **无担保**：素材与代码均按「原样（as-is）」提供，不附带任何明示或默示担保。

## 四、如何自行替换素材

- **鲸鱼娘图**：用 `转换形象.bat` 从你自己的透明底 PNG 生成 `whale_girl.png`，再 `python make_assets.py` 生成镜像图与图标；
- **音效**：把 `Ya1.mp3 / Ya2.mp3 / D1.mp3 / D2.mp3` 替换为你自己拥有权利的音频文件即可（文件名保持不变）。
