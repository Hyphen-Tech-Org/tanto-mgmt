# -*- coding: utf-8 -*-
"""
デスクトップ常駐アナログ時計ウィジェット
- 標準ライブラリ tkinter のみ（追加インストール不要 / 管理者権限不要 / ポータブル）
- frameless / 背景透過 / 常に最前面 / ドラッグ移動 / タスクバー非表示 / 右クリックで終了
"""

import tkinter as tk
import math
import os
import json
from datetime import datetime

# ============================================================
# 設定（ここを変えるだけで見た目を調整できます）
# ============================================================
WINDOW_SIZE      = 204          # ウィンドウの一辺(px)。これ1つで時計全体が拡大縮小する（240の85%＝大）
SIZE_PRESETS     = [            # 右クリック Size に出る選択肢 (ラベル, px)
    ("XS (50%)", 120), ("S (60%)", 144), ("M (70%)", 168),
    ("L (85%)", 204), ("XL (100%)", 240),
]
ALPHA            = 0.95         # 全体の不透明度 (0.0=透明 〜 1.0=不透明)
TRANSPARENT_COLOR = "#FF00FF"   # この色が透明になる（画面で使われない色を指定）。角を透明にして丸く見せる
FONT_FAMILY      = "Yu Gothic UI"  # 日付・デジタル時刻のフォント
FONT_SIZE        = 16           # 日付・曜日の文字サイズ（240px基準。WINDOW_SIZEに連動して自動縮小）
UPDATE_MS        = 200          # 再描画間隔(ms)。小さいほど秒針が滑らか

# デジタル時刻表示
SHOW_DIGITAL      = True        # 文字盤上部にデジタル時刻を出すか
DIGITAL_FONT_SIZE = 18          # デジタル時刻の文字サイズ（240px基準）
DIGITAL_SECONDS   = True        # 秒(:SS)まで表示するか
DIGITAL_COLOR     = "#000000"   # デジタル時刻の色

# ポモドーロタイマー（25分作業 / 5分休憩のみ）
POMO_WORK_MIN    = 25           # 作業フェーズの長さ(分)
POMO_BREAK_MIN   = 5            # 休憩フェーズの長さ(分)
POMO_WORK_COLOR  = "#D00000"    # 作業中のアーク・文字色（赤）
POMO_BREAK_COLOR = "#0A8F3C"    # 休憩中のアーク・文字色（緑）
POMO_ARC_W       = 6            # 進捗アークの太さ（240px基準）
POMO_FONT_SIZE   = 20           # ポモドーロ残り時間の文字サイズ（240px基準）
POMO_SOUND       = True         # フェーズ切替時にビープを鳴らすか
POMO_AUTO_LOOP   = True         # 作業→休憩→作業…と自動で繰り返すか
SHOW_COUNT       = True         # 今日の完了ポモドーロ数（周回数）を表示するか
COUNT_FONT_SIZE  = 13           # 完了数の文字サイズ（240px基準）
COUNT_COLOR      = "#666666"    # 完了数の文字色

# 色
FACE_COLOR   = "#FFFFFF"   # 文字盤の背景（白）
RING_COLOR   = "#000000"   # 文字盤の外枠
TICK_COLOR   = "#222222"   # 目盛り
HOUR_COLOR   = "#000000"   # 時針
MIN_COLOR    = "#000000"   # 分針
SEC_COLOR    = "#D00000"   # 秒針
TEXT_COLOR   = "#000000"   # 日付テキスト
CENTER_COLOR = "#000000"   # 中心の軸

# 針の太さ・長さ（半径に対する割合）
HOUR_LEN, HOUR_W = 0.50, 6
MIN_LEN,  MIN_W  = 0.72, 4
SEC_LEN,  SEC_W  = 0.80, 2

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]  # datetime.weekday(): 0=Mon
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# ポモドーロ実行状態（メニュー操作で書き換わる）
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
    if POMO["phase"] == "work":      # 作業フェーズ完了 → 本日カウント +1
        count_increment()
    POMO["phase"] = "break" if POMO["phase"] == "work" else "work"
    POMO["total"] = _phase_len(POMO["phase"])
    POMO["remaining"] = POMO["total"]
    if POMO_SOUND:
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass
    if not POMO_AUTO_LOOP:
        POMO["running"] = False


# 本日の完了ポモドーロ数（日付ごとにファイル保存。日付が変われば0に戻る）
try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
COUNT_FILE = os.path.join(_HERE, "pomo_count.json")
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
BASE = 240.0                # 各種寸法の基準サイズ
SIZE = WINDOW_SIZE
SCALE = SIZE / BASE         # 線の太さ・目盛り・フォントに掛ける拡大率
CX = CY = SIZE / 2
R = SIZE / 2 - 8 * SCALE    # 外枠のマージン


def hand_coords(angle_deg, length):
    """12時方向を0度、時計回りに角度を取り、針の先端座標を返す。"""
    rad = math.radians(angle_deg)
    return CX + length * math.sin(rad), CY - length * math.cos(rad)


def draw_clock(canvas, now):
    canvas.delete("all")

    # 文字盤（円）
    canvas.create_oval(CX - R, CY - R, CX + R, CY + R,
                       fill=FACE_COLOR, outline=RING_COLOR, width=3)

    # 目盛り（60本。5本ごとに太く長く）
    for i in range(60):
        ang = math.radians(i * 6)
        outer = R - 4 * SCALE
        inner = R - (14 if i % 5 == 0 else 7) * SCALE
        w = max(1, round((3 if i % 5 == 0 else 1) * SCALE))
        x1 = CX + inner * math.sin(ang)
        y1 = CY - inner * math.cos(ang)
        x2 = CX + outer * math.sin(ang)
        y2 = CY - outer * math.cos(ang)
        canvas.create_line(x1, y1, x2, y2, fill=TICK_COLOR, width=w)

    h = now.hour % 12
    m = now.minute
    s = now.second
    us = now.microsecond

    # 角度
    sec_ang  = (s + us / 1_000_000) * 6
    min_ang  = (m + s / 60) * 6
    hour_ang = (h + m / 60) * 30

    # 時針・分針・秒針
    hx, hy = hand_coords(hour_ang, R * HOUR_LEN)
    canvas.create_line(CX, CY, hx, hy, fill=HOUR_COLOR, width=max(1, HOUR_W * SCALE), capstyle="round")

    mx, my = hand_coords(min_ang, R * MIN_LEN)
    canvas.create_line(CX, CY, mx, my, fill=MIN_COLOR, width=max(1, MIN_W * SCALE), capstyle="round")

    sx, sy = hand_coords(sec_ang, R * SEC_LEN)
    canvas.create_line(CX, CY, sx, sy, fill=SEC_COLOR, width=max(1, SEC_W * SCALE), capstyle="round")

    # 中心の軸
    cr = max(2, 5 * SCALE)
    canvas.create_oval(CX - cr, CY - cr, CX + cr, CY + cr, fill=CENTER_COLOR, outline="")

    # デジタル時刻（中央上）
    if SHOW_DIGITAL:
        fmt = "%H:%M:%S" if DIGITAL_SECONDS else "%H:%M"
        dsize = max(6, round(DIGITAL_FONT_SIZE * SCALE))
        canvas.create_text(CX, CY - R * 0.42, text=now.strftime(fmt),
                           fill=DIGITAL_COLOR, font=(FONT_FAMILY, dsize, "bold"))

    # 日付（中央下・英国式 例: Mon 1 Jun 2026）
    wd = WEEKDAYS[now.weekday()]
    label = f"{wd} {now.day} {MONTHS[now.month - 1]} {now.year}"
    fsize = max(6, round(FONT_SIZE * SCALE))
    canvas.create_text(CX, CY + R * 0.45, text=label,
                       fill=TEXT_COLOR, font=(FONT_FAMILY, fsize, "bold"))

    # 本日の完了ポモドーロ数（中央上）
    if SHOW_COUNT:
        csize = max(6, round(COUNT_FONT_SIZE * SCALE))
        canvas.create_text(CX, CY - R * 0.63, text=f"Today: {POMO_COUNT['count']}",
                           fill=COUNT_COLOR, font=(FONT_FAMILY, csize, "bold"))

    # ポモドーロ（リムに進捗アーク + 中央に残り時間）
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
            ptxt += " ⏸"
        psize = max(6, round(POMO_FONT_SIZE * SCALE))
        canvas.create_text(CX, CY + R * 0.13, text=ptxt,
                           fill=pcolor, font=(FONT_FAMILY, psize, "bold"))


def tick(root, canvas):
    now = datetime.now()
    if POMO_COUNT["date"] and POMO_COUNT["date"] != now.strftime("%Y-%m-%d"):
        POMO_COUNT["date"] = now.strftime("%Y-%m-%d")  # 日付が変わったらカウントを0に
        POMO_COUNT["count"] = 0
        count_save()
    if POMO["active"] and POMO["running"] and POMO["last"] is not None:
        POMO["remaining"] -= (now - POMO["last"]).total_seconds()
        if POMO["remaining"] <= 0:
            pomo_switch()        # フェーズ切替（残りは新フェーズの満タンにリセット）
    POMO["last"] = now           # 一時停止中も更新し、再開時に飛ばないようにする
    draw_clock(canvas, now)
    root.after(UPDATE_MS, tick, root, canvas)


# ============================================================
# ウィンドウ
# ============================================================
def main():
    # 二重起動防止：すでに起動済みなら静かに終了（ランチャ/タスクが何度呼んでも1つだけ動く）
    try:
        import ctypes
        ctypes.windll.kernel32.CreateMutexW(None, False, "AnalogClockSingleton_niki")
        if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            return
    except Exception:
        pass

    root = tk.Tk()
    root.title("AnalogClock")
    root.overrideredirect(True)          # 枠なし（タスクバーからも消える）
    root.wm_attributes("-topmost", True) # 常に最前面
    root.wm_attributes("-alpha", ALPHA)  # 全体の不透明度
    root.config(bg=TRANSPARENT_COLOR)
    try:
        # 指定色を透明化 → 角が透けて丸い時計だけが見える
        root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
    except tk.TclError:
        pass

    # 初期位置：保存済みなら復元、なければ画面右上あたり
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    POS_FILE = os.path.join(_HERE, "window_pos.json")
    x, y = sw - SIZE - 40, 40
    try:
        with open(POS_FILE, encoding="utf-8") as f:
            _d = json.load(f)
        x, y = int(_d["x"]), int(_d["y"])
    except Exception:
        pass
    x = max(0, min(x, sw - SIZE))   # 画面外に出ないようクランプ
    y = max(0, min(y, sh - SIZE))
    root.geometry(f"{SIZE}x{SIZE}+{x}+{y}")

    canvas = tk.Canvas(root, width=SIZE, height=SIZE,
                       bg=TRANSPARENT_COLOR, highlightthickness=0)
    canvas.pack()

    # --- ドラッグで移動 ---
    drag = {"x": 0, "y": 0}

    def start_move(e):
        drag["x"], drag["y"] = e.x, e.y

    def do_move(e):
        nx = root.winfo_x() + e.x - drag["x"]
        ny = root.winfo_y() + e.y - drag["y"]
        root.geometry(f"+{nx}+{ny}")

    def end_move(_e):
        # ドラッグ終了時に現在位置を保存（次回起動・自動復活でも同じ場所に出す）
        try:
            with open(POS_FILE, "w", encoding="utf-8") as f:
                json.dump({"x": root.winfo_x(), "y": root.winfo_y()}, f)
        except Exception:
            pass

    canvas.bind("<Button-1>", start_move)
    canvas.bind("<B1-Motion>", do_move)
    canvas.bind("<ButtonRelease-1>", end_move)

    # --- サイズ変更（中心を保ったまま拡大縮小） ---
    def apply_size(new_size):
        global SIZE, SCALE, CX, CY, R
        old = SIZE
        cxs = root.winfo_x() + old / 2
        cys = root.winfo_y() + old / 2
        SIZE = new_size
        SCALE = SIZE / BASE
        CX = CY = SIZE / 2
        R = SIZE / 2 - 8 * SCALE
        nx = round(cxs - SIZE / 2)
        ny = round(cys - SIZE / 2)
        canvas.config(width=SIZE, height=SIZE)
        root.geometry(f"{SIZE}x{SIZE}+{nx}+{ny}")
        draw_clock(canvas, datetime.now())

    def step_size(delta):
        apply_size(max(80, min(400, SIZE + delta)))

    # --- 右クリックメニュー（ポモドーロ操作 + サイズ + 終了） ---
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Start Pomodoro", command=pomo_start)
    menu.add_command(label="Pause / Resume", command=pomo_toggle)
    menu.add_command(label="Reset", command=pomo_reset)
    menu.add_separator()
    size_menu = tk.Menu(menu, tearoff=0)
    for _label, _sz in SIZE_PRESETS:
        size_menu.add_command(label=_label, command=lambda s=_sz: apply_size(s))
    menu.add_cascade(label="Size", menu=size_menu)
    menu.add_separator()
    menu.add_command(label="Quit", command=root.destroy)

    # メニュー表示中フラグ。表示中は最前面の再主張を止め、メニューが時計の裏に
    # 隠れないようにする（-topmost を周期的に付け直すと開いた瞬間に被るため）。
    menu_open = {"v": False}

    def _menu_closed(_e=None):
        menu_open["v"] = False
        try:
            root.attributes("-topmost", True)   # 閉じたら即座に最前面へ復帰
        except tk.TclError:
            pass

    menu.bind("<Unmap>", _menu_closed)

    def popup(e):
        menu_open["v"] = True
        try:
            root.attributes("-topmost", False)  # メニューが時計の上に出るよう一時的に解除
        except tk.TclError:
            pass
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    canvas.bind("<Button-3>", popup)
    root.bind("<Escape>", lambda e: root.destroy())   # Escで終了
    root.bind("<space>", lambda e: pomo_toggle())     # Spaceで一時停止/再開
    root.bind("p", lambda e: pomo_start())            # pで開始
    root.bind("r", lambda e: pomo_reset())            # rでリセット
    root.bind("<plus>", lambda e: step_size(24))      # +で拡大
    root.bind("<KP_Add>", lambda e: step_size(24))
    root.bind("<minus>", lambda e: step_size(-24))    # -で縮小
    root.bind("<KP_Subtract>", lambda e: step_size(-24))

    count_load()

    # 他の最前面アプリ（Docker等）の裏に隠れないよう、定期的に最前面を再主張する
    def keep_top():
        if not menu_open["v"]:        # メニュー表示中は再主張しない（裏に回るのを防ぐ）
            try:
                root.attributes("-topmost", False)
                root.attributes("-topmost", True)
            except tk.TclError:
                pass
        root.after(2000, keep_top)

    keep_top()
    tick(root, canvas)
    root.mainloop()


if __name__ == "__main__":
    main()
