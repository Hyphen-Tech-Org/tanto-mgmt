# -*- coding: utf-8 -*-
"""
デスクトップ常駐アナログ時計ウィジェット（Windows / macOS 対応）
- 標準ライブラリ tkinter のみ（追加インストール不要 / 管理者権限不要 / ポータブル）
- frameless / 常に最前面 / ドラッグ移動 / 右クリックで終了 / 単一起動
- デザインは Tailwind "Catalyst" UI kit に準拠:
    フォント=Inter / ニュートラル=zinc / アクセント=blue-500 / ダークサーフェス / hover=blue-500
"""

import tkinter as tk
import tkinter.font as tkfont
import math
import os
import json
import sys
from datetime import datetime

IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"

# ============================================================
# Catalyst デザイントークン（Tailwind zinc + blue-500 / Inter）
# ============================================================
CT = {
    "zinc950": "#09090b", "zinc900": "#18181b", "zinc800": "#27272a",
    "zinc700": "#3f3f46", "zinc600": "#52525b", "zinc500": "#71717a",
    "zinc400": "#a1a1aa", "zinc300": "#d4d4d8", "zinc100": "#f4f4f5",
    "white": "#ffffff", "blue500": "#3b82f6", "red500": "#ef4444",
    "green500": "#22c55e",
}

# 見た目（ダーク Catalyst）への割り当て
FACE_COLOR   = CT["zinc900"]   # 文字盤
RING_COLOR   = CT["zinc700"]   # 外枠（subtle ring）
TICK_COLOR   = CT["zinc600"]   # 分目盛り
TICK_MAJOR   = CT["zinc300"]   # 時目盛り
HOUR_COLOR   = CT["white"]     # 時針
MIN_COLOR    = CT["white"]     # 分針
SEC_COLOR    = CT["blue500"]   # 秒針（アクセント）
CENTER_COLOR = CT["white"]     # 中心
DIGITAL_COLOR = CT["white"]    # デジタル時刻
TEXT_COLOR   = CT["zinc400"]   # 日付
COUNT_COLOR  = CT["zinc500"]   # 完了数
# メニュー（Catalyst Dropdown 準拠）
MENU_BG          = CT["zinc800"]
MENU_FG          = CT["white"]
MENU_ACTIVE_BG   = CT["blue500"]
MENU_ACTIVE_FG   = CT["white"]
MENU_DISABLED_FG = CT["zinc500"]

# Inter を最優先。未インストール時は OS 既定の sans へフォールバック（main で解決）
FONT_FAMILY = "Segoe UI" if IS_WIN else ("Helvetica Neue" if IS_MAC else "DejaVu Sans")
_FONT_PREFS = ["Inter", "Segoe UI", "Helvetica Neue", "SF Pro Text", "DejaVu Sans", "Arial"]

# ============================================================
# 設定（ここを変えるだけで見た目を調整できます）
# ============================================================
WINDOW_SIZE      = 204
SIZE_PRESETS     = [
    ("XS (50%)", 120), ("S (60%)", 144), ("M (70%)", 168),
    ("L (85%)", 204), ("XL (100%)", 240),
]
ALPHA            = 0.96
TRANSPARENT_COLOR = "#FF00FF"   # Windows: この色を透明化して角を丸く見せる
FONT_SIZE        = 16
UPDATE_MS        = 200

SHOW_DIGITAL      = True
DIGITAL_FONT_SIZE = 18
DIGITAL_SECONDS   = True

POMO_WORK_MIN    = 25
POMO_BREAK_MIN   = 5
POMO_WORK_COLOR  = CT["red500"]
POMO_BREAK_COLOR = CT["green500"]
POMO_ARC_W       = 6
POMO_FONT_SIZE   = 20
POMO_SOUND       = True
POMO_AUTO_LOOP   = True
SHOW_COUNT       = True
COUNT_FONT_SIZE  = 13

HOUR_LEN, HOUR_W = 0.50, 6
MIN_LEN,  MIN_W  = 0.72, 4
SEC_LEN,  SEC_W  = 0.80, 2

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

POMO = {"active": False, "phase": "work", "running": False,
        "remaining": 0.0, "total": 0.0, "last": None}


def _phase_len(phase):
    return (POMO_WORK_MIN if phase == "work" else POMO_BREAK_MIN) * 60


def pomo_start():
    POMO.update(active=True, running=True, phase="work",
                total=_phase_len("work"), remaining=_phase_len("work"),
                last=datetime.now())


def pomo_toggle():
    if POMO["active"]:
        POMO["running"] = not POMO["running"]


def pomo_reset():
    POMO.update(active=False, running=False)


def pomo_switch():
    if POMO["phase"] == "work":
        count_increment()
    POMO["phase"] = "break" if POMO["phase"] == "work" else "work"
    POMO["total"] = _phase_len(POMO["phase"])
    POMO["remaining"] = POMO["total"]
    if POMO_SOUND:
        try:
            if IS_WIN:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            else:
                print("\a", end="", flush=True)   # macOS/Linux: ベル
        except Exception:
            pass
    if not POMO_AUTO_LOOP:
        POMO["running"] = False


try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
COUNT_FILE = os.path.join(_HERE, "pomo_count.json")
POS_FILE = os.path.join(_HERE, "window_pos.json")
POMO_COUNT = {"date": "", "count": 0}


def _today():
    return datetime.now().strftime("%Y-%m-%d")


def count_load():
    POMO_COUNT["date"] = _today()
    POMO_COUNT["count"] = 0
    try:
        with open(COUNT_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("date") == _today():
            POMO_COUNT["count"] = int(data.get("count", 0))
    except Exception:
        pass


def count_save():
    try:
        with open(COUNT_FILE, "w", encoding="utf-8") as f:
            json.dump({"date": POMO_COUNT["date"], "count": POMO_COUNT["count"]}, f)
    except Exception:
        pass


def count_increment():
    if POMO_COUNT["date"] != _today():
        POMO_COUNT["date"] = _today()
        POMO_COUNT["count"] = 0
    POMO_COUNT["count"] += 1
    count_save()


# ============================================================
# 描画ロジック
# ============================================================
BASE = 240.0
SIZE = WINDOW_SIZE
SCALE = SIZE / BASE
CX = CY = SIZE / 2
R = SIZE / 2 - 8 * SCALE


def hand_coords(angle_deg, length):
    rad = math.radians(angle_deg)
    return CX + length * math.sin(rad), CY - length * math.cos(rad)


def draw_clock(canvas, now):
    canvas.delete("all")

    canvas.create_oval(CX - R, CY - R, CX + R, CY + R,
                       fill=FACE_COLOR, outline=RING_COLOR, width=2)

    for i in range(60):
        ang = math.radians(i * 6)
        major = (i % 5 == 0)
        outer = R - 4 * SCALE
        inner = R - (14 if major else 7) * SCALE
        w = max(1, round((3 if major else 1) * SCALE))
        x1 = CX + inner * math.sin(ang); y1 = CY - inner * math.cos(ang)
        x2 = CX + outer * math.sin(ang); y2 = CY - outer * math.cos(ang)
        canvas.create_line(x1, y1, x2, y2,
                           fill=(TICK_MAJOR if major else TICK_COLOR), width=w)

    h = now.hour % 12; m = now.minute; s = now.second; us = now.microsecond
    sec_ang  = (s + us / 1_000_000) * 6
    min_ang  = (m + s / 60) * 6
    hour_ang = (h + m / 60) * 30

    hx, hy = hand_coords(hour_ang, R * HOUR_LEN)
    canvas.create_line(CX, CY, hx, hy, fill=HOUR_COLOR, width=max(1, HOUR_W * SCALE), capstyle="round")
    mx, my = hand_coords(min_ang, R * MIN_LEN)
    canvas.create_line(CX, CY, mx, my, fill=MIN_COLOR, width=max(1, MIN_W * SCALE), capstyle="round")
    sx, sy = hand_coords(sec_ang, R * SEC_LEN)
    canvas.create_line(CX, CY, sx, sy, fill=SEC_COLOR, width=max(1, SEC_W * SCALE), capstyle="round")

    cr = max(2, 5 * SCALE)
    canvas.create_oval(CX - cr, CY - cr, CX + cr, CY + cr, fill=CENTER_COLOR, outline="")

    if SHOW_DIGITAL:
        fmt = "%H:%M:%S" if DIGITAL_SECONDS else "%H:%M"
        dsize = max(6, round(DIGITAL_FONT_SIZE * SCALE))
        canvas.create_text(CX, CY - R * 0.42, text=now.strftime(fmt),
                           fill=DIGITAL_COLOR, font=(FONT_FAMILY, dsize, "bold"))

    wd = WEEKDAYS[now.weekday()]
    label = f"{wd} {now.day} {MONTHS[now.month - 1]} {now.year}"
    fsize = max(6, round(FONT_SIZE * SCALE))
    canvas.create_text(CX, CY + R * 0.45, text=label,
                       fill=TEXT_COLOR, font=(FONT_FAMILY, fsize, "bold"))

    if SHOW_COUNT:
        csize = max(6, round(COUNT_FONT_SIZE * SCALE))
        canvas.create_text(CX, CY - R * 0.63, text=f"Today: {POMO_COUNT['count']}",
                           fill=COUNT_COLOR, font=(FONT_FAMILY, csize, "bold"))

    if POMO["active"]:
        pcolor = POMO_WORK_COLOR if POMO["phase"] == "work" else POMO_BREAK_COLOR
        frac = 0.0 if POMO["total"] <= 0 else max(0.0, min(1.0, 1 - POMO["remaining"] / POMO["total"]))
        if frac > 0:
            aw = max(2, round(POMO_ARC_W * SCALE))
            ext = -359.9 if frac >= 1.0 else -360 * frac
            canvas.create_arc(CX - R + aw, CY - R + aw, CX + R - aw, CY + R - aw,
                              start=90, extent=ext, style="arc", outline=pcolor, width=aw)
        rem = max(0, int(POMO["remaining"] + 0.999))
        mm, ss = divmod(rem, 60)
        ptxt = ("Focus" if POMO["phase"] == "work" else "Break") + f" {mm:02d}:{ss:02d}"
        if not POMO["running"]:
            ptxt += " ||"
        psize = max(6, round(POMO_FONT_SIZE * SCALE))
        canvas.create_text(CX, CY + R * 0.13, text=ptxt,
                           fill=pcolor, font=(FONT_FAMILY, psize, "bold"))


def tick(root, canvas):
    now = datetime.now()
    if POMO_COUNT["date"] and POMO_COUNT["date"] != now.strftime("%Y-%m-%d"):
        POMO_COUNT["date"] = now.strftime("%Y-%m-%d")
        POMO_COUNT["count"] = 0
        count_save()
    if POMO["active"] and POMO["running"] and POMO["last"] is not None:
        POMO["remaining"] -= (now - POMO["last"]).total_seconds()
        if POMO["remaining"] <= 0:
            pomo_switch()
    POMO["last"] = now
    draw_clock(canvas, now)
    root.after(UPDATE_MS, tick, root, canvas)


# ============================================================
# 単一起動チェック（Windows=named mutex / 他=PIDロックファイル）
# ============================================================
def already_running():
    if IS_WIN:
        try:
            import ctypes
            ctypes.windll.kernel32.CreateMutexW(None, False, "AnalogClockSingleton_niki")
            return ctypes.windll.kernel32.GetLastError() == 183  # ERROR_ALREADY_EXISTS
        except Exception:
            return False
    # macOS / Linux: PID ロックファイル
    lock = os.path.join(_HERE, ".clock.lock")
    try:
        if os.path.exists(lock):
            with open(lock, encoding="utf-8") as f:
                pid = int((f.read() or "0").strip() or 0)
            if pid > 0:
                try:
                    os.kill(pid, 0)   # 生存確認（例外なし=動作中）
                    return True
                except OSError:
                    pass               # 死んでいる → 続行して奪取
        with open(lock, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass
    return False


# ============================================================
# ウィンドウ
# ============================================================
def main():
    if already_running():
        return

    root = tk.Tk()
    root.title("AnalogClock")

    # Inter 優先でフォント解決
    global FONT_FAMILY
    try:
        fams = set(tkfont.families(root))
        for cand in _FONT_PREFS:
            if cand in fams:
                FONT_FAMILY = cand
                break
    except Exception:
        pass

    root.overrideredirect(True)
    try:
        root.wm_attributes("-topmost", True)
    except tk.TclError:
        pass
    try:
        root.wm_attributes("-alpha", ALPHA)
    except tk.TclError:
        pass

    # 背景透過（角を丸く見せる）。プラットフォーム別。
    win_bg = FACE_COLOR
    if IS_WIN:
        win_bg = TRANSPARENT_COLOR
        root.config(bg=win_bg)
        try:
            root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
        except tk.TclError:
            win_bg = FACE_COLOR
            root.config(bg=win_bg)
    elif IS_MAC:
        try:
            root.wm_attributes("-transparent", True)
            win_bg = "systemTransparent"
            root.config(bg=win_bg)
        except tk.TclError:
            win_bg = FACE_COLOR
            root.config(bg=win_bg)
    else:
        root.config(bg=win_bg)

    # 初期位置：保存済みなら復元、なければ画面右上
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x, y = sw - SIZE - 40, 40
    try:
        with open(POS_FILE, encoding="utf-8") as f:
            _d = json.load(f)
        x, y = int(_d["x"]), int(_d["y"])
    except Exception:
        pass
    x = max(0, min(x, sw - SIZE))
    y = max(0, min(y, sh - SIZE))
    root.geometry(f"{SIZE}x{SIZE}+{x}+{y}")

    canvas = tk.Canvas(root, width=SIZE, height=SIZE, bg=win_bg, highlightthickness=0)
    canvas.pack()

    # --- ドラッグで移動 + 位置保存 ---
    drag = {"x": 0, "y": 0}

    def start_move(e):
        drag["x"], drag["y"] = e.x, e.y

    def do_move(e):
        nx = root.winfo_x() + e.x - drag["x"]
        ny = root.winfo_y() + e.y - drag["y"]
        root.geometry(f"+{nx}+{ny}")

    def end_move(_e):
        try:
            with open(POS_FILE, "w", encoding="utf-8") as f:
                json.dump({"x": root.winfo_x(), "y": root.winfo_y()}, f)
        except Exception:
            pass

    canvas.bind("<Button-1>", start_move)
    canvas.bind("<B1-Motion>", do_move)
    canvas.bind("<ButtonRelease-1>", end_move)

    # --- サイズ変更（中心を保ったまま） ---
    def apply_size(new_size):
        global SIZE, SCALE, CX, CY, R
        old = SIZE
        cxs = root.winfo_x() + old / 2
        cys = root.winfo_y() + old / 2
        SIZE = new_size
        SCALE = SIZE / BASE
        CX = CY = SIZE / 2
        R = SIZE / 2 - 8 * SCALE
        nx = round(cxs - SIZE / 2); ny = round(cys - SIZE / 2)
        canvas.config(width=SIZE, height=SIZE)
        root.geometry(f"{SIZE}x{SIZE}+{nx}+{ny}")
        draw_clock(canvas, datetime.now())

    def step_size(delta):
        apply_size(max(80, min(400, SIZE + delta)))

    # --- 右クリックメニュー（Catalyst Dropdown 配色） ---
    menu_opts = dict(tearoff=0, bg=MENU_BG, fg=MENU_FG,
                     activebackground=MENU_ACTIVE_BG, activeforeground=MENU_ACTIVE_FG,
                     activeborderwidth=0, bd=0, relief="flat",
                     disabledforeground=MENU_DISABLED_FG, font=(FONT_FAMILY, 10))
    menu = tk.Menu(root, **menu_opts)
    menu.add_command(label="Start Pomodoro", accelerator="P", command=pomo_start)
    menu.add_command(label="Pause / Resume", accelerator="Space", command=pomo_toggle)
    menu.add_command(label="Reset", accelerator="R", command=pomo_reset)
    menu.add_separator()
    size_menu = tk.Menu(menu, **menu_opts)
    for _label, _sz in SIZE_PRESETS:
        size_menu.add_command(label=_label, command=lambda s=_sz: apply_size(s))
    menu.add_cascade(label="Size", menu=size_menu)
    menu.add_separator()
    menu.add_command(label="Quit", accelerator="Esc", command=root.destroy)

    # メニュー表示中だけ最前面の再主張を止める。閉じたかは winfo_ismapped で実監視し、
    # イベント取りこぼしでフラグが固着して「ずっと最前面でなくなる」事故を防ぐ。
    menu_open = {"v": False}

    def _resume_topmost():
        menu_open["v"] = False
        try:
            root.attributes("-topmost", True)
            root.lift()
        except tk.TclError:
            pass

    def _watch_menu():
        try:
            still = bool(menu.winfo_ismapped())
        except tk.TclError:
            still = False
        if still:
            root.after(120, _watch_menu)
        else:
            _resume_topmost()

    def popup(e):
        menu_open["v"] = True
        try:
            root.attributes("-topmost", False)
        except tk.TclError:
            pass
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()
        root.after(200, _watch_menu)

    canvas.bind("<Button-3>", popup)
    if IS_MAC:
        canvas.bind("<Button-2>", popup)            # macOS の副ボタン
        canvas.bind("<Control-Button-1>", popup)    # macOS の Ctrl+クリック
    root.bind("<Escape>", lambda e: root.destroy())
    root.bind("<space>", lambda e: pomo_toggle())
    root.bind("p", lambda e: pomo_start())
    root.bind("r", lambda e: pomo_reset())
    root.bind("<plus>", lambda e: step_size(24))
    root.bind("<KP_Add>", lambda e: step_size(24))
    root.bind("<minus>", lambda e: step_size(-24))
    root.bind("<KP_Subtract>", lambda e: step_size(-24))

    count_load()

    def keep_top():
        if not menu_open["v"]:
            try:
                root.attributes("-topmost", False)
                root.attributes("-topmost", True)
                root.lift()
            except tk.TclError:
                pass
        root.after(1000, keep_top)

    keep_top()
    tick(root, canvas)
    root.mainloop()


if __name__ == "__main__":
    main()
