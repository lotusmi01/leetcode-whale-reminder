# 🐳 鲸鱼娘 · 每日刷题提醒浮窗

一个常驻桌面的小浮窗，用 **DeepSeek 小鲸鱼娘** 形象提醒你每天做算法题，点击即可打开力扣（LeetCode）。交互与文案**仿照 DeepSeek 小鲸鱼插件**（[MeteorNOX/DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget)）。

## 功能

- ✅ 桌面常驻浮窗：置顶、无边框、透明背景，不遮挡桌面
- ✅ **打开时问候**：`今天也别忘了练习哦`
- ✅ **点击智能判断**：先检测力扣是否已在浏览器打开——
  - 已打开 → 切换鲸鱼娘台词（随机语句，权重抽 1、不连续重复）
  - 未打开 → 用默认浏览器打开力扣
- ✅ **拖拽吸附**：靠近左 / 右 / 下边缘自动贴边；贴左（屏幕左半）时**镜像翻转**朝向屏幕内
- ✅ 每天定时提醒（默认 20:00）：弹气泡 + 响铃 + 鲸鱼跳动，点击气泡打开力扣
- ✅ 已内置 **DeepSeek 小鲸鱼娘** 透明底形象
- ✅ **开机自启 + 桌面快捷方式**（已自动创建）
- ✅ **仅在桌面可见**（右键可开，默认关）：开启后其它窗口最大化/全屏时自动隐藏，不遮挡页面
- ✅ **按压 Q 弹 + 音效**：点击有下压回弹特效 + 小黄鸭音效（右键可关）

## 运行

> 依赖：仅 **Python 标准库**（tkinter 等），无需第三方包。需本机已安装 Python 3（Windows 版自带 tkinter）。

- **桌面快捷方式**：`鲸鱼娘刷题.lnk`（已放到桌面，双击即启动，无黑框）
- 或双击 **`启动浮窗.bat`**
- 或命令行：`python leetcode_whale.py`

## 使用说明

| 操作 | 效果 |
| --- | --- |
| **左键单击鲸鱼娘** | 检测力扣：已打开 → 切换台词；未打开 → 打开力扣 |
| **按住左键拖动** | 移动位置；松手后自动**吸附**到左/右/下边缘（位置自动记住） |
| **拖到屏幕左半** | 鲸鱼娘**镜像翻转**，面向屏幕中心 |
| **右键单击** | 弹出菜单 |
| 右键 → ⏰ 设置提醒时间 | 修改每天提醒时间（默认 20:00） |
| 右键 → 🌐 网址 | 切换 力扣中国 / LeetCode 国际 |
| 右键 → ✅ 今日已打卡 | 手动标记今天已完成，当天不再提醒 |
| 右键 → 🔊 点击音效 | 开关按压音效 |
| 右键 → 🎵 音效组 | 切换 小黄鸭 / 音效1（含试听） |
| 右键 → 🖥 仅桌面显示 | 开关「仅在桌面可见」 |
| 右键 → ❌ 退出 | 关闭浮窗 |

## 开机自启 / 桌面快捷方式（已完成）

已自动创建两个快捷方式（目标为 `pythonw.exe`，无黑框运行）：

- **桌面**：`C:\Users\Administrator\Desktop\鲸鱼娘刷题.lnk`
- **开机自启**：`C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\鲸鱼娘刷题.lnk`

删除开机自启只需删掉「启动」文件夹里的那个快捷方式即可。

## 点击台词（可自定义）

点击时鲸鱼娘随机切换的台词，取自插件默认「随机语句」，直接编辑 `leetcode_whale.py` 顶部的 `CLICK_PHRASES` 列表即可增删改（`(文字, 权重)`，权重越大越常出现）。

## 更换形象（可选）

当前已内置你提供的 **DeepSeek 小鲸鱼娘** 形象（`whale_girl.png`，透明底）。换图：

1. 把新图片路径填进 `转换形象.bat`（默认 `E:\DownLoads\DSniang1.png`）。
2. 双击 **`转换形象.bat`** → 自动去白底、裁剪、缩放，生成新的 `whale_girl.png`。
3. 运行 **`make_assets.py`**（或用 DSH 自带 Python：`python make_assets.py`）→ 重新生成镜像图 `whale_girl_flip.png` 与图标 `whale_girl.ico`。
4. 右键浮窗 → **🖼 重新加载鲸鱼娘形象**（或重启）。

## 配置文件

首次运行自动生成 `config.json`，保存提醒时间、网址、位置等：

```json
{
  "remind_time": "20:00",
  "reminded_date": "",
  "url": "https://leetcode.cn/",
  "pos": null
}
```

## 许可与素材

- **代码**：本项目自有代码按 [**PolyForm Noncommercial License 1.0.0**](LICENSE) 授权——可自由使用 / 修改 / 分享，但**不得用于商业用途**（注意：该许可含非商业条款，不属于 OSI 定义的「开源」许可）。
- **第三方素材**：仓库中的鲸鱼娘图片（`whale_girl*.png` / `.ico`）与音效（`*.mp3`）来自 [DeepSeek 小鲸鱼插件](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget)，**不在本项目 LICENSE 覆盖范围内**。其来源、原作者许可范围、非官方声明与 takedown 方式详见 **[NOTICE.md](NOTICE.md)**。
- 本项目是个人学习性质的第三方项目，与 DeepSeek / DSH / 该插件作者均**无隶属关系**。

## 文件清单

- `leetcode_whale.py` —— 主程序（标准库，无第三方依赖）
- `whale_girl.png` —— 鲸鱼娘形象（透明底）
- `whale_girl_flip.png` —— 镜像形象（贴左翻转用）
- `whale_girl.ico` —— 快捷方式图标
- `Ya1.mp3` / `Ya2.mp3` / `D1.mp3` / `D2.mp3` —— 小黄鸭 / 音效1 按压·松开音效（来自插件）
- `启动浮窗.bat` —— 一键启动（无黑框）
- `convert_mascot.py` + `转换形象.bat` —— 更换形象（去白底 / 裁剪 / 缩放）
- `make_assets.py` —— 生成镜像图与图标
- `config.json` —— 自动生成的配置文件
