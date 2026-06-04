# -*- coding: utf-8 -*-
"""
AnalogClock — PySide6 / Qt 版（今風 & 軽量）
- アンチエイリアス描画で滑らか／角丸・ソフト影／滑らか秒針
- デザインは Tailwind "Catalyst": Inter / zinc / blue-500 / ライト既定・ダーク切替
- 枠なし・透過・常に最前面・ドラッグ移動・右クリックメニュー・単一起動・位置記憶
- 依存: pip install PySide6-Essentials
"""

import sys
import os
import json
from datetime import datetime

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import (QPainter, QColor, QPen, QFont, QGuiApplication,
                           QAction, QActionGroup, QRadialGradient)

IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"
HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(HERE, "settings.json")
POS_FILE = os.path.join(HERE, "window_pos.json")

# ===== Catalyst tokens =====
C = {
    "zinc950": "#09090b", "zinc900": "#18181b", "zinc800": "#27272a", "zinc700": "#3f3f46",
    "zinc600": "#52525b", "zinc500": "#71717a", "zinc400": "#a1a1aa", "zinc300": "#d4d4d8",
    "zinc200": "#e4e4e7", "white": "#ffffff", "blue500": "#3b82f6", "red500": "#ef4444",
    "green500": "#22c55e",
}
THEMES = {
    "light": dict(face="#ffffff", ring="#d4d4d8", tick="#d4d4d8", tickMajor="#18181b",
                  hand="#09090b", sec="#3b82f6", center="#09090b", digital="#09090b",
                  date="#71717a", count="#a1a1aa", shadow=70,
                  menuBg="#ffffff", menuRing="#e4e4e7", menuFg="#09090b",
                  menuMuted="#a1a1aa", menuDivider="#e4e4e7"),
    "dark": dict(face="#18181b", ring="#3f3f46", tick="#52525b", tickMajor="#d4d4d8",
                 hand="#ffffff", sec="#3b82f6", center="#ffffff", digital="#ffffff",
                 date="#a1a1aa", count="#71717a", shadow=150,
                 menuBg="#27272a", menuRing="#3f3f46", menuFg="#ffffff",
                 menuMuted="#a1a1aa", menuDivider="#3f3f46"),
}
SIZE_PRESETS = [("XS", 120), ("S", 144), ("M", 168), ("L", 204), ("XL", 240)]
PAD = 18           # 影のための余白
UPDATE_MS = 33     # 約30fps（小さな部品なのでCPUはごく僅か。1000で「秒刻み・CPUほぼ0」も可）
WORK_MIN, BREAK_MIN = 25, 5


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, obj):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f)
    except Exception:
        pass


def today():
    return datetime.now().strftime("%Y-%m-%d")


class Clock(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        s = load_json(SETTINGS_FILE, {})
        self.theme = "dark" if s.get("theme") == "dark" else "light"
        self.face_size = int(s.get("size", 204))
        self.count = int(s.get("count", 0))
        self.count_date = s.get("countDate", "")
        if self.count_date != today():
            self.count, self.count_date = 0, today()
        self.pomo = {"active": False, "phase": "work", "running": False,
                     "remaining": 0.0, "total": 0.0, "last": None}
        self._drag = None
        self.font_family = self._resolve_font()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self._apply_window_size()
        self._restore_position()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(UPDATE_MS)

        # 最前面の再主張（他の最前面アプリより上に居続ける。メニュー表示中は除外）
        self._menu_open = False
        self.top_timer = QTimer(self)
        self.top_timer.timeout.connect(self._reassert_top)
        self.top_timer.start(1500)

    # ---- helpers ----
    def _resolve_font(self):
        fams = set(QtGui.QFontDatabase.families())
        for cand in ("Inter", "Segoe UI", "Helvetica Neue", "SF Pro Text", "Arial"):
            if cand in fams:
                return cand
        return self.font().family()

    def _win_size(self):
        return self.face_size + PAD * 2

    def _apply_window_size(self):
        self.setFixedSize(self._win_size(), self._win_size())

    def _restore_position(self):
        pos = load_json(POS_FILE, None)
        if isinstance(pos, dict):
            x, y = int(pos.get("x", 0)), int(pos.get("y", 0))
            if not (x == 0 and y == 0):
                self.move(x, y)
                return
        geo = QGuiApplication.primaryScreen().availableGeometry()
        self.move(geo.right() - self._win_size() - 20, geo.top() + 20)

    def _save_settings(self):
        save_json(SETTINGS_FILE, {"theme": self.theme, "size": self.face_size,
                                  "count": self.count, "countDate": self.count_date})

    # ---- pomodoro ----
    def pomo_start(self):
        self.pomo.update(active=True, running=True, phase="work",
                         total=WORK_MIN * 60, remaining=WORK_MIN * 60, last=datetime.now())

    def pomo_toggle(self):
        if self.pomo["active"]:
            self.pomo["running"] = not self.pomo["running"]

    def pomo_reset(self):
        self.pomo.update(active=False, running=False)

    def _pomo_switch(self):
        if self.pomo["phase"] == "work":
            if self.count_date != today():
                self.count, self.count_date = 0, today()
            self.count += 1
            self._save_settings()
        self.pomo["phase"] = "break" if self.pomo["phase"] == "work" else "work"
        self.pomo["total"] = (WORK_MIN if self.pomo["phase"] == "work" else BREAK_MIN) * 60
        self.pomo["remaining"] = self.pomo["total"]
        QtWidgets.QApplication.beep()

    # ---- loop ----
    def _tick(self):
        now = datetime.now()
        if self.count_date and self.count_date != today():
            self.count, self.count_date = 0, today()
            self._save_settings()
        P = self.pomo
        if P["active"] and P["running"] and P["last"] is not None:
            P["remaining"] -= (now - P["last"]).total_seconds()
            if P["remaining"] <= 0:
                self._pomo_switch()
        P["last"] = now
        self.update()

    def _reassert_top(self):
        # メニュー表示中は何もしない（メニューを時計の裏に回さない）
        if self._menu_open:
            return
        try:
            if IS_WIN:
                import ctypes
                HWND_TOPMOST = -1
                SWP = 0x0001 | 0x0002 | 0x0010  # NOSIZE | NOMOVE | NOACTIVATE
                ctypes.windll.user32.SetWindowPos(int(self.winId()), HWND_TOPMOST, 0, 0, 0, 0, SWP)
            else:
                self.raise_()
        except Exception:
            pass

    # ---- painting ----
    def paintEvent(self, _e):
        t = THEMES[self.theme]
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)
        W = self._win_size()
        cx = cy = W / 2.0
        R = self.face_size / 2.0
        scale = self.face_size / 240.0
        now = datetime.now()

        # soft drop shadow
        grad = QRadialGradient(cx, cy + 4 * scale, R + PAD)
        sh = QColor(0, 0, 0, t["shadow"])
        grad.setColorAt(max(0.0, (R - 2) / (R + PAD)), sh)
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(grad)
        p.drawEllipse(QPointF(cx, cy + 4 * scale), R + PAD - 2, R + PAD - 2)

        # face + ring
        p.setBrush(QColor(t["face"]))
        p.setPen(QPen(QColor(t["ring"]), 1.5))
        p.drawEllipse(QPointF(cx, cy), R, R)

        # ticks
        for i in range(60):
            major = (i % 5 == 0)
            ang = i * 6.0
            outer = R - 4 * scale
            inner = R - (14 if major else 7) * scale
            p.save()
            p.translate(cx, cy)
            p.rotate(ang)
            pen = QPen(QColor(t["tickMajor"] if major else t["tick"]),
                       max(1.0, (3 if major else 1) * scale))
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawLine(QPointF(0, -inner), QPointF(0, -outer))
            p.restore()

        # hands
        h = now.hour % 12
        m = now.minute
        s = now.second + now.microsecond / 1_000_000
        self._hand(p, cx, cy, (h + m / 60) * 30, R * 0.50, 6 * scale, t["hand"])
        self._hand(p, cx, cy, (m + s / 60) * 6, R * 0.72, 4 * scale, t["hand"])
        self._hand(p, cx, cy, s * 6, R * 0.80, 2 * scale, t["sec"])

        # center
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(t["center"]))
        p.drawEllipse(QPointF(cx, cy), max(2.0, 5 * scale), max(2.0, 5 * scale))

        # texts
        self._text(p, cx, cy - R * 0.63, f"Today: {self.count}", 13 * scale, t["count"])
        self._text(p, cx, cy - R * 0.40, now.strftime("%H:%M:%S"), 18 * scale, t["digital"])
        wd = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][now.weekday()]
        mo = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][now.month - 1]
        self._text(p, cx, cy + R * 0.46, f"{wd} {now.day} {mo} {now.year}", 15 * scale, t["date"])

        # pomodoro
        P = self.pomo
        if P["active"]:
            col = QColor(C["red500"] if P["phase"] == "work" else C["green500"])
            frac = 0.0 if P["total"] <= 0 else max(0.0, min(1.0, 1 - P["remaining"] / P["total"]))
            if frac > 0:
                aw = max(2.0, 6 * scale)
                pen = QPen(col, aw)
                pen.setCapStyle(Qt.RoundCap)
                p.setPen(pen)
                p.setBrush(Qt.NoBrush)
                rr = R - aw
                rect = QRectF(cx - rr, cy - rr, rr * 2, rr * 2)
                p.drawArc(rect, 90 * 16, -int(360 * frac * 16))
            rem = max(0, int(P["remaining"] + 0.999))
            txt = ("Focus " if P["phase"] == "work" else "Break ") + f"{rem // 60:02d}:{rem % 60:02d}" + ("" if P["running"] else " ||")
            self._text(p, cx, cy + R * 0.14, txt, 18 * scale, col.name(), bold=True)
        p.end()

    def _hand(self, p, cx, cy, ang, length, width, color):
        p.save()
        p.translate(cx, cy)
        p.rotate(ang)
        pen = QPen(QColor(color), max(1.0, width))
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawLine(QPointF(0, 0), QPointF(0, -length))
        p.restore()

    def _text(self, p, x, y, s, size, color, bold=True):
        f = QFont(self.font_family, max(6, int(round(size))))
        f.setBold(bold)
        p.setFont(f)
        p.setPen(QColor(color))
        fm = QtGui.QFontMetricsF(f)
        p.drawText(QPointF(x - fm.horizontalAdvance(s) / 2.0, y + fm.ascent() / 2.0 - fm.descent() / 2.0), s)

    # ---- size / theme ----
    def set_size(self, px):
        center = self.geometry().center()
        self.face_size = px
        self._apply_window_size()
        g = self.frameGeometry()
        g.moveCenter(center)
        self.move(g.topLeft())
        self._save_settings()
        self.update()

    def set_theme(self, name):
        self.theme = "dark" if name == "dark" else "light"
        self._save_settings()
        self.update()

    # ---- interaction ----
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e):
        if self._drag is not None and (e.buttons() & Qt.LeftButton):
            self.move(e.globalPosition().toPoint() - self._drag)
            e.accept()

    def mouseReleaseEvent(self, e):
        if self._drag is not None:
            self._drag = None
            save_json(POS_FILE, {"x": self.x(), "y": self.y()})

    def keyPressEvent(self, e):
        k = e.key()
        if k == Qt.Key_Escape:
            self.close()
        elif k == Qt.Key_Space:
            self.pomo_toggle()
        elif k == Qt.Key_P:
            self.pomo_start()
        elif k == Qt.Key_R:
            self.pomo_reset()
        elif k in (Qt.Key_Plus, Qt.Key_Equal):
            self.set_size(min(400, self.face_size + 24))
        elif k == Qt.Key_Minus:
            self.set_size(max(80, self.face_size - 24))

    def contextMenuEvent(self, e):
        t = THEMES[self.theme]
        menu = QtWidgets.QMenu(self)
        menu.setAttribute(Qt.WA_TranslucentBackground, True)
        menu.setWindowFlags(menu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        menu.setStyleSheet(f"""
            QMenu {{ background:{t['menuBg']}; border:1px solid {t['menuRing']};
                     border-radius:12px; padding:4px; color:{t['menuFg']};
                     font-family:'{self.font_family}'; font-size:13px; }}
            QMenu::item {{ padding:6px 28px 6px 14px; border-radius:8px; }}
            QMenu::item:selected {{ background:{C['blue500']}; color:#ffffff; }}
            QMenu::separator {{ height:1px; background:{t['menuDivider']}; margin:4px 10px; }}
            QMenu::indicator {{ width:14px; height:14px; left:6px; }}
        """)

        def act(label, fn, shortcut=None):
            a = QAction(label, menu)
            if shortcut:
                a.setShortcut(shortcut)
            a.triggered.connect(fn)
            menu.addAction(a)
            return a

        act("Start Pomodoro", self.pomo_start, "P")
        act("Pause / Resume", self.pomo_toggle, "Space")
        act("Reset", self.pomo_reset, "R")
        menu.addSeparator()

        theme_menu = menu.addMenu("Theme")
        theme_menu.setStyleSheet(menu.styleSheet())
        grp = QActionGroup(theme_menu)
        for name in ("light", "dark"):
            a = QAction(name.capitalize(), theme_menu)
            a.setCheckable(True)
            a.setChecked(self.theme == name)
            a.triggered.connect(lambda _c=False, n=name: self.set_theme(n))
            grp.addAction(a)
            theme_menu.addAction(a)

        size_menu = menu.addMenu("Size")
        size_menu.setStyleSheet(menu.styleSheet())
        for lb, px in SIZE_PRESETS:
            a = QAction(f"{lb}", size_menu)
            a.setCheckable(True)
            a.setChecked(self.face_size == px)
            a.triggered.connect(lambda _c=False, p=px: self.set_size(p))
            size_menu.addAction(a)

        menu.addSeparator()
        act("Quit", self.close, "Esc")
        self._menu_open = True       # 表示中は最前面の再主張を止め、メニューを最上位に
        try:
            menu.exec(e.globalPos())
        finally:
            self._menu_open = False
            self.raise_()


def single_instance():
    shm = QtCore.QSharedMemory("AnalogClockSingleton_niki_qt")
    if shm.attach():
        return None
    if not shm.create(1):
        return None
    return shm  # 参照を保持して常駐


def main():
    QApplication = QtWidgets.QApplication
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    guard = single_instance()
    if guard is None:
        return
    w = Clock()
    w._guard = guard
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
