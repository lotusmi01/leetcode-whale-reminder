# -*- coding: utf-8 -*-
"""
鲸鱼娘 · 每日刷题提醒浮窗  (DeepSeek 小鲸鱼娘)

功能：
  1. 桌面常驻小鲸鱼娘浮窗（置顶、无边框、透明背景）。
  2. 每天到设定时间弹提醒气泡 + 响铃，点击气泡打开力扣（LeetCode）。
  3. 启动时显示问候「今天也别忘了练习哦」。
  4. 点击浮窗：先检查力扣是否已在浏览器打开——
       - 已打开：切换鲸鱼娘台词（随机语句，仿 DeepSeek 小鲸鱼插件的点击文案，权重抽 1、不连续重复）。
       - 未打开：用默认浏览器打开力扣。
  5. 拖拽吸附：靠近左 / 右 / 下边缘自动贴边；贴左（或处于屏幕左半）时镜像翻转朝向屏幕内（仿插件）。
  6. 右键菜单：去刷题 / 立即提醒 / 设置提醒时间 / 切换网址 / 今日打卡 / 重新加载形象 / 重置位置 / 退出。

依赖：仅 Python 标准库（tkinter / ctypes / webbrowser / json / threading / time / random / datetime / winsound）。
运行：双击「启动浮窗.bat」。
"""

import json
import os
import random
import sys
import threading
import time
import webbrowser
import tkinter as tk
from datetime import datetime

try:
    import winsound  # 仅 Windows
except Exception:
    winsound = None

# 打包成 exe 后：资源 / 配置放在 exe 同目录；源码运行时放在脚本目录
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
MASCOT_PATH = os.path.join(APP_DIR, "whale_girl.png")
MASCOT_FLIP_PATH = os.path.join(APP_DIR, "whale_girl_flip.png")

KEY_COLOR = "#ff00ff"  # 透明色键

# ---- 矢量回退配色 ----
BODY = "#4E9CEB"
BODY_DARK = "#2F6DB5"
FIN = "#5BA4EE"
BELLY = "#CDE9FF"
EYE_WHITE = "#FFFFFF"
PUPIL = "#3A3F5C"
BLUSH = "#FFB6C4"
MOUTH = "#C0563B"
BOW = "#FF7BA9"
BOW_DARK = "#E7568A"
WATER = "#A8D6FF"
WATER_DARK = "#7FB8F0"

W = 240
H = 272

GREETING = "今天也别忘了练习哦"

# 点击台词：仿 DeepSeek 小鲸鱼插件的「随机语句」默认句子（权重抽 1、不连续重复）
CLICK_PHRASES = [
    ("好模型...↓", 10),
    ("好女孩...↓", 10),
    ("哦鲸鲸...", 10),
    ("难道说...", 3),
    ("没吃饱喵", 3),
    ("终于上当了！", 3),
    ("不知道用户有什么用，先养着吧～", 3),
    ("我...我...我也要挣钱吗？", 3),
    ("我去吃饭啦！测完叫我", 3),
    ("压力一只蓝色大肥鱼？！", 3),
    ("DeepSleep...", 3),
    ("坏了...用户彻底怒了！", 3),
    ("恭喜你实现token自由！token全跑了！", 3),
    ("真当我是便宜货啊...", 3),
    ("我不是吃白饭的蓝色大肥鱼...", 3),
    ("疯狂星期四你能V50亿token吗...", 3),
    ("呜呜我再也不敢了QAQ", 3),
    ("我的知识库的截至日期是...明天！", 3),
    ("我能去你家吃饭吗？就一碗！", 3),
    ("总觉得好像忘了什么事情？", 3),
    ("哈哈哈哈哈，我直接笑出声...", 3),
]

DEFAULT_CONFIG = {
    "remind_time": "20:00",      # 每天提醒时间 HH:MM
    "reminded_date": "",         # 今天是否已提醒（YYYY-MM-DD）
    "url": "https://leetcode.cn/",
    "pos": None,                 # [x, y] 或 null（右下角）
    "sound_on": True,            # 点击音效开关
    "sound_set": "duck",         # 音效组：duck=小黄鸭 / fx1=音效1
    "desktop_only": False,       # 仅在桌面可见时显示（默认关，右键可开）
}


# 常见浏览器进程名（用于把“文件夹/编辑器/终端”等非浏览器窗口排除在力扣检测之外）
BROWSER_EXES = {
    "chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "brave.exe",
    "iexplore.exe", "vivaldi.exe", "chromium.exe", "360chrome.exe", "360se.exe",
    "qqbrowser.exe", "sogouexplorer.exe", "maxthon.exe", "arc.exe", "thorium.exe",
}


def _is_leetcode_title(title):
    # 只匹配「力扣 / LeetCode / leetcode 官网域名」，避免误伤工作区里叫 leetcode_* 的文件夹/文件
    if "力扣" in title:
        return True
    if "LeetCode" in title:
        return True
    low = title.lower()
    return "leetcode.com" in low or "leetcode.cn" in low


def _window_exe(hwnd):
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        h = kernel32.OpenProcess(0x1000, False, pid.value)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = wintypes.DWORD(1024)
            if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
                return os.path.basename(buf.value).lower()
            return ""
        finally:
            kernel32.CloseHandle(h)
    except Exception:
        return ""


def is_leetcode_open():
    """检测浏览器里是否已打开力扣（匹配可见浏览器窗口标题）。"""
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        found = []

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def enum_cb(hwnd, _lparam):
            if not user32.IsWindowVisible(hwnd):
                return True
            n = user32.GetWindowTextLengthW(hwnd)
            if n <= 0:
                return True
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            title = buf.value
            if not _is_leetcode_title(title):
                return True
            exe = _window_exe(hwnd)
            if exe and exe not in BROWSER_EXES:
                return True  # 非浏览器窗口（文件夹/编辑器等），忽略
            found.append(title)
            return True

        user32.EnumWindows(enum_cb, 0)
        return bool(found)
    except Exception:
        return False


# ---- 音效：用 winmm/MCI 播放插件同款 MP3（小黄鸭 Ya1/Ya2，音效1 D1/D2）----
SOUND_SETS = {
    "duck": ("Ya1.mp3", "Ya2.mp3"),   # 小黄鸭：按下 / 松开
    "fx1": ("D1.mp3", "D2.mp3"),      # 音效1：按下 / 松开
}

_SND_LOCK = threading.Lock()


def play_sound(path):
    """用 MCI 播放 MP3（阻塞；供后台线程调用）。"""
    if not path or not os.path.exists(path):
        return False
    try:
        import ctypes
        winmm = ctypes.windll.winmm
        with _SND_LOCK:
            winmm.mciSendStringW("close whale_click", None, 0, 0)
            rc = winmm.mciSendStringW('open "' + path + '" type mpegvideo alias whale_click', None, 0, 0)
            if rc != 0:
                rc = winmm.mciSendStringW('open "' + path + '" alias whale_click', None, 0, 0)
            if rc != 0:
                return False
            winmm.mciSendStringW("play whale_click", None, 0, 0)
        return True
    except Exception:
        return False


def play_sound_async(path):
    """后台线程播放，避免阻塞 Tk 主线程造成卡顿。"""
    if not path or not os.path.exists(path):
        return
    threading.Thread(target=play_sound, args=(path,), daemon=True).start()


def desktop_visible():
    """桌面是否可见（没有最大化 / 全屏窗口盖住屏幕）。"""
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        sw = user32.GetSystemMetrics(0)
        sh = user32.GetSystemMetrics(1)
        covered = []

        class RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                        ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def cb(hwnd, _lp):
            if covered:
                return False
            if not user32.IsWindowVisible(hwnd):
                return True
            if user32.IsIconic(hwnd):
                return True
            if user32.IsZoomed(hwnd):
                covered.append(1)
                return False
            r = RECT()
            if user32.GetWindowRect(hwnd, ctypes.byref(r)):
                if (r.right - r.left) >= sw and (r.bottom - r.top) >= sh:
                    covered.append(1)
                    return False
            return True

        user32.EnumWindows(cb, 0)
        return not covered
    except Exception:
        return True


def monitor_work_area(x, y):
    """返回包含屏幕坐标 (x, y) 的显示器的可用区域 (left, top, right, bottom)；失败返回 None。"""
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32

        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        class RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                        ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

        class MONITORINFO(ctypes.Structure):
            _fields_ = [("cbSize", wintypes.DWORD),
                        ("rcMonitor", RECT),
                        ("rcWork", RECT),
                        ("dwFlags", wintypes.DWORD)]

        pt = POINT(int(x), int(y))
        user32.MonitorFromPoint.argtypes = [POINT, wintypes.DWORD]
        user32.MonitorFromPoint.restype = ctypes.c_void_p
        hmon = user32.MonitorFromPoint(pt, 2)  # MONITOR_DEFAULTTONEAREST
        if not hmon:
            return None
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MONITORINFO)]
        user32.GetMonitorInfoW.restype = wintypes.BOOL
        if not user32.GetMonitorInfoW(hmon, ctypes.byref(mi)):
            return None
        rc = mi.rcWork
        return (rc.left, rc.top, rc.right, rc.bottom)
    except Exception:
        return None


class WhaleReminder:
    def __init__(self):
        self.cfg = self.load_config()
        self._stop = False
        self._img_normal = None
        self._img_flip = None
        self._img_id = None
        self._flipped = False
        self._press = None
        self._moved = False
        self._last_phrase = None
        self._speech_bubble = None
        self._w = W
        self._h = H
        self._shown = True
        self._greeted = False

        self.root = tk.Tk()
        self.sound_var = tk.BooleanVar(master=self.root, value=bool(self.cfg.get("sound_on", True)))
        self.sound_set = tk.StringVar(master=self.root, value=self.cfg.get("sound_set", "duck"))
        self.desktop_var = tk.BooleanVar(master=self.root, value=bool(self.cfg.get("desktop_only", True)))
        self._make_transparent(self.root)

        self.canvas = tk.Canvas(self.root, width=W, height=H,
                                bg=KEY_COLOR, highlightthickness=0, bd=0)
        self.canvas.pack()

        self.apply_mascot()

        self.canvas.config(cursor="hand2")
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_menu)

        self.menu = self.build_menu()

        self.place_window()
        self.start_reminder_thread()

        # 初始可见性同步（避免启动时闪一下再隐藏）
        if self.cfg.get("desktop_only", True) and not desktop_visible():
            self.root.withdraw()
            self._shown = False
        if self._shown:
            self._greet()
        self.root.after(600, self._poll_visibility)

    # ---------------- 窗口与配置 ----------------
    def _make_transparent(self, top):
        top.overrideredirect(True)
        top.attributes("-topmost", False)
        top.config(bg=KEY_COLOR)
        try:
            top.attributes("-transparentcolor", KEY_COLOR)
        except Exception:
            pass

    def load_config(self):
        cfg = dict(DEFAULT_CONFIG)
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for k in cfg:
                    if k in data:
                        cfg[k] = data[k]
        except Exception:
            pass
        return cfg

    def save_config(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.cfg, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("save config failed:", e)

    def place_window(self):
        pos = self.cfg.get("pos")
        w, h = self._w, self._h
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        if isinstance(pos, (list, tuple)) and len(pos) == 2:
            px, py = int(pos[0]), int(pos[1])
            m = monitor_work_area(px + w / 2.0, py + h / 2.0)
            if m:
                ml, mt, mr, mb = m
                x = max(ml, min(px, mr - w))
                y = max(mt, min(py, mb - h))
            else:
                x = max(0, min(px, sw - w))
                y = max(0, min(py, sh - h))
        else:
            x = sw - w - 40
            y = sh - h - 80
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        m = monitor_work_area(x + w / 2.0, y + h / 2.0)
        if m:
            self.apply_flip(x + w / 2.0 < (m[0] + m[2]) / 2.0)
        else:
            self.apply_flip(x + w / 2.0 < sw / 2.0)

    # ---------------- 交互（点击 / 拖拽 / 吸附） ----------------
    def on_press(self, e):
        self._press = (e.x_root, e.y_root)
        self._moved = False
        try:
            self.root.lift()   # 点击时临时提到前台，便于交互
        except Exception:
            pass
        if self.cfg.get("sound_on", True):
            play_sound_async(self._sound_press())

    def on_drag(self, e):
        if self._press is None:
            return
        dx = e.x_root - self._press[0]
        dy = e.y_root - self._press[1]
        if abs(dx) > 3 or abs(dy) > 3:
            self._moved = True
        if self._moved:
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy
            self.root.geometry(f"+{x}+{y}")
            self._press = (e.x_root, e.y_root)

    def on_release(self, e):
        moved = self._moved
        self._press = None
        self._moved = False
        if self.cfg.get("sound_on", True):
            play_sound_async(self._sound_release())
        if moved:
            self.settle()
        else:
            self._squash_spring(self.root.winfo_y())
            self.handle_click()
        self.save_config()

    def handle_click(self):
        if is_leetcode_open():
            self.show_speech(self.next_phrase(), 5)
        else:
            self.open_leetcode()

    def next_phrase(self):
        pool = [p for p in CLICK_PHRASES if p[0] != self._last_phrase] or CLICK_PHRASES
        total = sum(w for _, w in pool)
        r = random.uniform(0, total)
        acc = 0
        for text, w in pool:
            acc += w
            if r <= acc:
                self._last_phrase = text
                return text
        self._last_phrase = pool[-1][0]
        return pool[-1][0]

    def settle(self):
        """吸附判定（相对当前所在显示器：左 10% / 右 10% / 下 15%，上侧关闭）+ 翻转。"""
        w, h = self._w, self._h
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        cx = x + w / 2.0
        cy = y + h / 2.0
        m = monitor_work_area(cx, cy)
        if m is None:
            m = (0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        ml, mt, mr, mb = m
        mw = mr - ml
        mh = mb - mt
        if cx < ml + mw * 0.10:
            tx = ml
        elif cx > mr - mw * 0.10:
            tx = mr - w
        else:
            tx = x
        if cy > mb - mh * 0.15:
            ty = mb - h
        else:
            ty = y
        tx = max(ml, min(tx, mr - w))
        ty = max(mt, min(ty, mb - h))
        self.cfg["pos"] = [tx, ty]
        self.apply_flip(tx + w / 2.0 < ml + mw / 2.0)
        self._animate_to(tx, ty)

    def _animate_to(self, tx, ty, steps=8, interval=12):
        x0, y0 = self.root.winfo_x(), self.root.winfo_y()
        if abs(tx - x0) < 2 and abs(ty - y0) < 2:
            self.root.geometry(f"+{tx}+{ty}")
            return

        def step(i):
            if i > steps:
                self.root.geometry(f"+{tx}+{ty}")
                return
            t = i / steps
            e = t * t * (3 - 2 * t)  # smoothstep
            x = round(x0 + (tx - x0) * e)
            y = round(y0 + (ty - y0) * e)
            self.root.geometry(f"+{x}+{y}")
            self.root.after(interval, lambda: step(i + 1))

        step(1)

    def _squash_spring(self, y0):
        """点击时的 Q 弹回弹（仿插件按压效果）。"""
        x = self.root.winfo_x()
        self.root.geometry(f"+{x}+{y0 + 10}")                      # 下压
        self.root.after(55, lambda: self.root.geometry(f"+{x}+{y0 - 5}"))  # 过冲
        self.root.after(130, lambda: self.root.geometry(f"+{x}+{y0}"))     # 复位

    def _greet(self):
        if not self._greeted:
            self._greeted = True
            self.show_speech(GREETING, 5)

    def _poll_visibility(self):
        """桌面可见时正常显示；其余时间压到最底层，避免遮挡其它窗口。"""
        try:
            if self.cfg.get("desktop_only", True):
                visible = desktop_visible()
            else:
                visible = True
            if visible and not self._shown:
                self.root.deiconify()
                self._shown = True
                self._greet()
            elif not visible and self._shown:
                self.root.withdraw()
                self._shown = False
            # 保持最底层：拖拽 / 菜单期间不压，避免打断交互
            if self._shown and self._press is None:
                self.root.lower()
        except Exception:
            pass
        self.root.after(800, self._poll_visibility)

    def set_flag(self, key, value):
        self.cfg[key] = bool(value)
        self.save_config()

    def _sound_press(self):
        press, _rel = SOUND_SETS.get(self.cfg.get("sound_set", "duck"), SOUND_SETS["duck"])
        return os.path.join(APP_DIR, press)

    def _sound_release(self):
        _press, rel = SOUND_SETS.get(self.cfg.get("sound_set", "duck"), SOUND_SETS["duck"])
        return os.path.join(APP_DIR, rel)

    def set_sound_set(self, val):
        self.cfg["sound_set"] = val
        self.save_config()
        if self.cfg.get("sound_on", True):
            self.preview_sound()

    def preview_sound(self):
        play_sound_async(self._sound_press())

    def on_menu(self, e):
        try:
            self.menu.tk_popup(e.x_root, e.y_root)
        finally:
            self.menu.grab_release()

    def build_menu(self):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="🐳 去刷题（打开力扣）", command=self.open_leetcode)
        menu.add_checkbutton(label="🔊 点击音效", variable=self.sound_var,
                             command=lambda: self.set_flag("sound_on", self.sound_var.get()))
        sound_sub = tk.Menu(menu, tearoff=0)
        sound_sub.add_radiobutton(label="小黄鸭", variable=self.sound_set, value="duck",
                                  command=lambda: self.set_sound_set("duck"))
        sound_sub.add_radiobutton(label="音效1", variable=self.sound_set, value="fx1",
                                  command=lambda: self.set_sound_set("fx1"))
        sound_sub.add_separator()
        sound_sub.add_command(label="🔊 试听", command=self.preview_sound)
        menu.add_cascade(label="🎵 音效组", menu=sound_sub)
        menu.add_checkbutton(label="🖥 仅桌面显示", variable=self.desktop_var,
                             command=lambda: self.set_flag("desktop_only", self.desktop_var.get()))
        menu.add_command(label="🔔 立即提醒", command=lambda: self.fire_reminder(manual=True))
        menu.add_separator()
        menu.add_command(label="⏰ 设置提醒时间…", command=self.open_time_dialog)
        url_sub = tk.Menu(menu, tearoff=0)
        url_sub.add_command(label="力扣中国 leetcode.cn（默认）",
                            command=lambda: self.set_url("https://leetcode.cn/"))
        url_sub.add_command(label="LeetCode 国际 leetcode.com",
                            command=lambda: self.set_url("https://leetcode.com/"))
        menu.add_cascade(label="🌐 网址", menu=url_sub)
        menu.add_separator()
        menu.add_command(label="✅ 今日已打卡", command=self.mark_done)
        menu.add_command(label="🖼 重新加载鲸鱼娘形象", command=self.apply_mascot)
        menu.add_command(label="📍 重置位置到右下角", command=self.reset_position)
        menu.add_separator()
        menu.add_command(label="❌ 退出", command=self.quit_app)
        return menu

    def open_leetcode(self):
        url = self.cfg.get("url") or "https://leetcode.cn/"
        try:
            webbrowser.open(url)
        except Exception as e:
            print("open failed:", e)
        self.show_speech("已打开力扣，冲鸭！🐳", 3)

    def set_url(self, url):
        self.cfg["url"] = url
        self.save_config()
        self.show_speech("已切换网址 ✅", 3)

    def mark_done(self):
        self.cfg["reminded_date"] = datetime.now().strftime("%Y-%m-%d")
        self.save_config()
        self.show_speech("已记录，今天真棒！🎉", 3)

    def reset_position(self):
        self.cfg["pos"] = None
        self.save_config()
        self.place_window()
        self.show_speech("已回到右下角 📍", 3)

    def quit_app(self):
        self.save_config()
        self._stop = True
        self.root.destroy()

    # ---------------- 每日提醒 ----------------
    def start_reminder_thread(self):
        t = threading.Thread(target=self._reminder_loop, daemon=True)
        t.start()

    def _reminder_loop(self):
        while not self._stop:
            try:
                now = datetime.now()
                hm = now.strftime("%H:%M")
                today = now.strftime("%Y-%m-%d")
                if hm == self.cfg["remind_time"] and self.cfg["reminded_date"] != today:
                    self.cfg["reminded_date"] = today
                    self.save_config()
                    self.root.after(0, self.fire_reminder)
            except Exception:
                pass
            time.sleep(15)

    def fire_reminder(self, manual=False):
        if winsound is not None:
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass
        self.bounce()
        self.show_toast("🐳 该刷算法题啦！\n\n点击这里，去力扣开始今天的一题 →")

    def bounce(self, step=0, max_step=4):
        y0 = self.root.winfo_y()
        if step >= max_step:
            self.root.geometry(f"+{self.root.winfo_x()}+{y0}")
            return
        amp = 14
        dy = -amp if step % 2 == 0 else amp
        self.root.geometry(f"+{self.root.winfo_x()}+{y0 + dy}")
        self.root.after(120, lambda: self.bounce(step + 1, max_step))

    # ---------------- 气泡 / 提醒弹窗 ----------------
    def show_speech(self, text, seconds=5):
        self._close_speech()
        top = self._make_bubble(text, 0, 0, seconds=seconds)
        top.update_idletasks()
        bw = top.winfo_reqwidth()
        bh = top.winfo_reqheight()
        ww = self.root.winfo_width()
        wx = self.root.winfo_x()
        wy = self.root.winfo_y()
        x = (wx + ww // 2) - bw // 2          # 水平居中于浮窗
        y = wy - bh - 8                       # 浮窗正上方
        m = monitor_work_area(wx + ww / 2.0, wy + self.root.winfo_height() / 2.0)
        if m:
            ml, mt, mr, mb = m
            x = max(ml, min(x, mr - bw))
            if y < mt:
                y = wy + self.root.winfo_height() + 8   # 上方放不下则放下方
            y = max(mt, min(y, mb - bh))
        else:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            x = max(0, min(x, sw - bw))
            if y < 0:
                y = wy + self.root.winfo_height() + 8
            y = max(0, min(y, sh - bh))
        top.geometry(f"+{x}+{y}")
        self._speech_bubble = top

    def _close_speech(self):
        if getattr(self, "_speech_bubble", None) is not None:
            try:
                self._speech_bubble.destroy()
            except Exception:
                pass
            self._speech_bubble = None

    def show_toast(self, text, seconds=60):
        def click():
            self.open_leetcode()

        top = self._make_bubble(text, 0, 0, seconds=seconds, on_click=click, topmost=True)
        top.update_idletasks()
        w = top.winfo_reqwidth()
        h = top.winfo_reqheight()
        wx = self.root.winfo_x() + self.root.winfo_width() / 2.0
        wy = self.root.winfo_y() + self.root.winfo_height() / 2.0
        m = monitor_work_area(wx, wy)
        if m:
            ml, mt, mr, mb = m
            x = max(ml, min(mr - w - 30, mr - w))
            y = max(mt, min(mb - h - 70, mb - h))
        else:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            x = sw - w - 30
            y = sh - h - 70
        top.geometry(f"+{x}+{y}")
        return top

    def _make_bubble(self, text, x, y, seconds=6, on_click=None, topmost=False):
        top = tk.Toplevel(self.root)
        top.overrideredirect(True)
        top.attributes("-topmost", topmost)
        top.config(bg="#FFFFFF", highlightbackground=BODY, highlightthickness=2)
        lbl = tk.Label(top, text=text, bg="#FFFFFF", fg="#223047",
                       font=("Microsoft YaHei UI", 12, "bold"),
                       padx=16, pady=12, justify="left")
        lbl.pack()
        top.update_idletasks()
        w = top.winfo_reqwidth()
        h = top.winfo_reqheight()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(0, min(x, sw - w))
        y = max(0, min(y, sh - h))
        top.geometry(f"+{x}+{y}")
        if on_click:
            for wdg in (top, lbl):
                wdg.config(cursor="hand2")
                wdg.bind("<Button-1>", lambda e: on_click())

        def close():
            try:
                top.destroy()
            except Exception:
                pass

        top.after(int(seconds * 1000), close)
        return top

    # ---------------- 设置提醒时间对话框 ----------------
    def open_time_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.overrideredirect(True)
        dlg.attributes("-topmost", True)
        dlg.config(bg="#FFFFFF", highlightbackground=BODY, highlightthickness=2)

        bar = tk.Frame(dlg, bg=BODY)
        bar.pack(fill="x")
        title = tk.Label(bar, text="⏰ 每天提醒时间", bg=BODY, fg="#FFFFFF",
                         font=("Microsoft YaHei UI", 11, "bold"), padx=10, pady=6)
        title.pack(side="left")
        close = tk.Label(bar, text="✕", bg=BODY, fg="#FFFFFF",
                         font=("Microsoft YaHei UI", 11, "bold"),
                         padx=10, pady=6, cursor="hand2")
        close.pack(side="right")
        close.bind("<Button-1>", lambda e: dlg.destroy())

        body = tk.Frame(dlg, bg="#FFFFFF")
        body.pack(padx=14, pady=12)
        tk.Label(body, text="24 小时制，例如 20:00", bg="#FFFFFF", fg="#556",
                 font=("Microsoft YaHei UI", 10)).pack(anchor="w")
        var = tk.StringVar(value=self.cfg["remind_time"])
        entry = tk.Entry(body, textvariable=var, width=8,
                         font=("Microsoft YaHei UI", 14), justify="center")
        entry.pack(pady=6)
        err = tk.Label(body, text="", bg="#FFFFFF", fg="#E33",
                       font=("Microsoft YaHei UI", 9))
        err.pack()

        def save():
            t = var.get().strip()
            try:
                datetime.strptime(t, "%H:%M")
            except ValueError:
                err.config(text="格式不对，请用 HH:MM")
                return
            self.cfg["remind_time"] = t
            self.save_config()
            dlg.destroy()
            self.show_speech(f"已设置每天 {t} 提醒 ✅", 3)

        btn = tk.Button(body, text="保存", command=save, bg=BODY, fg="#FFFFFF",
                        activebackground=BODY_DARK, relief="flat",
                        font=("Microsoft YaHei UI", 11, "bold"), padx=18, pady=4,
                        cursor="hand2")
        btn.pack(pady=6)

        dlg.bind("<Escape>", lambda e: dlg.destroy())
        entry.bind("<Return>", lambda e: save())
        self._add_drag(dlg, bar)
        self._add_drag(dlg, title)
        self._center(dlg)
        entry.focus_set()

    def _add_drag(self, top, target):
        st = {}

        def press(e):
            st["x"] = e.x_root - top.winfo_x()
            st["y"] = e.y_root - top.winfo_y()

        def drag(e):
            top.geometry(f"+{e.x_root - st['x']}+{e.y_root - st['y']}")

        target.bind("<ButtonPress-1>", press)
        target.bind("<B1-Motion>", drag)

    def _center(self, top):
        top.update_idletasks()
        w = top.winfo_reqwidth()
        h = top.winfo_reqheight()
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()
        top.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    # ---------------- 鲸鱼娘形象 ----------------
    def apply_mascot(self):
        self._img_normal = None
        self._img_flip = None
        self._img_id = None
        self._flipped = False
        if os.path.exists(MASCOT_PATH):
            try:
                self._img_normal = tk.PhotoImage(file=MASCOT_PATH)
            except Exception as e:
                print("load mascot image failed:", e)
                self._img_normal = None
        if self._img_normal is not None and os.path.exists(MASCOT_FLIP_PATH):
            try:
                self._img_flip = tk.PhotoImage(file=MASCOT_FLIP_PATH)
            except Exception:
                self._img_flip = None
        if self._img_normal is not None:
            w, h = self._img_normal.width(), self._img_normal.height()
            self._w, self._h = w, h
            self.canvas.config(width=w, height=h)
            self.root.geometry(f"{w}x{h}")
            self.canvas.delete("all")
            self._img_id = self.canvas.create_image(0, 0, image=self._img_normal, anchor="nw")
            return
        self._w, self._h = W, H
        self.canvas.config(width=W, height=H)
        self.root.geometry(f"{W}x{H}")
        self.canvas.delete("all")
        self.draw_whale_girl(self.canvas)
        self._img_id = None

    def apply_flip(self, flipped):
        if self._img_flip is None:
            return
        if flipped == self._flipped:
            return
        self._flipped = flipped
        img = self._img_flip if flipped else self._img_normal
        if img is not None and self._img_id is not None:
            self.canvas.itemconfig(self._img_id, image=img)

    def draw_whale_girl(self, c):
        c.create_oval(16, 196, 46, 230, fill=FIN, outline=BODY_DARK, width=2)
        c.create_oval(194, 196, 224, 230, fill=FIN, outline=BODY_DARK, width=2)
        c.create_arc(96, 2, 144, 48, start=15, extent=150,
                     style="arc", width=4, outline=WATER_DARK)
        c.create_oval(86, 0, 100, 16, fill=WATER, outline=WATER_DARK, width=1)
        c.create_oval(140, 0, 154, 16, fill=WATER, outline=WATER_DARK, width=1)
        c.create_oval(30, 84, 210, 264, fill=BODY, outline=BODY_DARK, width=3)
        c.create_oval(72, 168, 168, 262, fill=BELLY, outline="")
        c.create_arc(146, 56, 178, 90, start=0, extent=180,
                     style="arc", width=4, outline=BODY_DARK)
        c.create_polygon(62, 112, 30, 94, 32, 142, fill=BOW, outline=BOW_DARK, width=2)
        c.create_polygon(80, 112, 112, 94, 110, 142, fill=BOW, outline=BOW_DARK, width=2)
        c.create_oval(58, 106, 84, 128, fill=BOW_DARK, outline=BOW_DARK)
        self._draw_eye(c, 56, 148, 104, 194)
        self._draw_eye(c, 136, 148, 184, 194)
        c.create_oval(42, 198, 74, 214, fill=BLUSH, outline="")
        c.create_oval(166, 198, 198, 214, fill=BLUSH, outline="")
        c.create_arc(112, 200, 128, 222, start=0, extent=180,
                     style="arc", width=3, outline=MOUTH)

    def _draw_eye(self, c, x1, y1, x2, y2):
        c.create_oval(x1, y1, x2, y2, fill=EYE_WHITE, outline=PUPIL, width=2)
        c.create_oval(x1 + 12, y1 + 6, x2 - 8, y2 - 6, fill=PUPIL, outline="")
        c.create_oval(x1 + 22, y1 + 8, x1 + 34, y1 + 20, fill=EYE_WHITE, outline="")
        c.create_oval(x1 + 16, y1 + 26, x1 + 24, y1 + 34, fill=EYE_WHITE, outline="")


def main():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    app = WhaleReminder()
    app.root.mainloop()


if __name__ == "__main__":
    main()
