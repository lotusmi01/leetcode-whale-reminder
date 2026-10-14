# -*- coding: utf-8 -*-
"""生成浮窗附属资源：镜像图（贴左翻转用）与 .ico 图标（快捷方式用）。"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "whale_girl.png")
FLIP = os.path.join(HERE, "whale_girl_flip.png")
ICO = os.path.join(HERE, "whale_girl.ico")


def main():
    from PIL import Image, ImageOps

    if not os.path.exists(SRC):
        print("[错误] 找不到 whale_girl.png")
        return False

    img = Image.open(SRC).convert("RGBA")

    # 1) 镜像图
    ImageOps.mirror(img).save(FLIP, "PNG")
    print(f"[完成] {FLIP}  ({img.size[0]}x{img.size[1]})")

    # 2) 图标（正方形透明底，居中放缩）
    size = 256
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ratio = min(size / img.width, size / img.height)
    w = max(1, int(img.width * ratio))
    h = max(1, int(img.height * ratio))
    thumb = img.resize((w, h), Image.LANCZOS)
    canvas.paste(thumb, ((size - w) // 2, (size - h) // 2), thumb)
    canvas.save(ICO, "ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"[完成] {ICO}")
    return True


if __name__ == "__main__":
    ok = main()
    if ok:
        print("资源生成完毕。")
