# -*- coding: utf-8 -*-
"""
把 DeepSeek 小鲸鱼娘图片转成「透明底 PNG」，供浮窗使用。

用法：
  双击「转换形象.bat」，或
  python convert_mascot.py [源图路径] [输出路径]

默认：源图 E:\\DownLoads\\DSniang1.png -> 输出 本目录 whale_girl.png

说明：
  - 自动从图片四边做「flood-fill」只去除白色/近白背景，
    因此会保留角色内部的白色部分（女仆头饰、领结、眼白等）。
  - 若图片本身已带透明通道，则跳过去背景，直接裁剪 + 缩放保存。
  - 输出统一缩放到不超过 240x272，保持长宽比。
"""

import os
import sys
from collections import deque


def convert(src, dst, max_w=240, max_h=272):
    try:
        from PIL import Image
    except ImportError:
        print("[错误] 未安装 Pillow，请先执行: python -m pip install pillow")
        return False

    if not os.path.exists(src):
        print(f"[错误] 找不到源图: {src}")
        return False

    print(f"读取源图: {src}")
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    print(f"原始尺寸: {w}x{h}")
    px = img.load()

    # 判断是否已经带透明通道
    amin, amax = img.getchannel("A").getextrema()
    if amin < 250:
        print("检测到已有透明通道，跳过去背景，直接裁剪缩放。")
        out = img
    else:
        # 从四边 flood-fill 去除白色/近白背景
        mask = bytearray(w * h)  # 0=保留, 1=背景(转透明)
        q = deque()
        for x in range(w):
            q.append((x, 0))
            q.append((x, h - 1))
        for y in range(h):
            q.append((0, y))
            q.append((w - 1, y))

        while q:
            x, y = q.popleft()
            if not (0 <= x < w and 0 <= y < h):
                continue
            idx = y * w + x
            if mask[idx]:
                continue
            r, g, b, a = px[x, y]
            # 背景判定：接近白色且低饱和（避免误删浅蓝头发/高光）
            if r >= 240 and g >= 240 and b >= 240 and (max(r, g, b) - min(r, g, b)) <= 20:
                mask[idx] = 1
                q.append((x + 1, y))
                q.append((x - 1, y))
                q.append((x, y + 1))
                q.append((x, y - 1))

        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        opx = out.load()
        removed = 0
        for y in range(h):
            for x in range(w):
                if mask[y * w + x]:
                    removed += 1
                else:
                    opx[x, y] = px[x, y]
        print(f"已去除白色背景（{removed} 像素）。")

    # 裁剪到内容边界，并留一点边距
    bbox = out.getbbox()
    if not bbox:
        print("[错误] 图片内容为空，未生成。")
        return False
    margin = 6
    l = max(0, bbox[0] - margin)
    t = max(0, bbox[1] - margin)
    r = min(out.size[0], bbox[2] + margin)
    b = min(out.size[1], bbox[3] + margin)
    out = out.crop((l, t, r, b))

    # 缩放到目标尺寸以内
    cw, ch = out.size
    scale = min(max_w / cw, max_h / ch)
    if scale < 1:
        out = out.resize((int(cw * scale), int(ch * scale)), Image.LANCZOS)

    out.save(dst, "PNG")
    print(f"[完成] 已生成 {dst}  (尺寸 {out.size[0]}x{out.size[1]})")
    return True


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv) > 1 else r"E:\DownLoads\DSniang1.png"
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "whale_girl.png")
    ok = convert(src, dst)
    if ok:
        print("\n现在双击「启动浮窗.bat」即可看到鲸鱼娘形象。")
    try:
        input("\n按回车退出...")
    except Exception:
        pass
