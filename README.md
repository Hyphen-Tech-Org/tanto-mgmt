![Analog Clock](assets/hero.svg)

# 🕒 Analog Clock

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform: Windows & macOS](https://img.shields.io/badge/platform-Windows%20%26%20macOS-3b82f6.svg)](#requirements--動作環境)
[![Python: 3.x](https://img.shields.io/badge/python-3.x-3776AB.svg)](https://www.python.org/)
[![Dependencies: none](https://img.shields.io/badge/dependencies-none-success.svg)](#requirements--動作環境)

> **インストール不要・管理者権限不要・設定不要。** ダブルクリックするだけで動く、いつも最前面に浮かぶ Windows & macOS 向けのアナログ時計ウィジェット。
> *A portable, always-on-top desktop analog clock for Windows & macOS. Pure Python (tkinter) — just run it.*

---

## 📸 Screenshot

![screenshot](assets/clock.svg)

文字盤のアナログ時計＋デジタル時刻＋日付（例: `Mon 1 Jun 2026`）、そして内蔵ポモドーロタイマー。すべてが小さな1つのウィンドウに収まっています。

---

## ✨ Features / 特徴

- **アナログ＋デジタル表示** — 針の時計と数字の時刻を同時に表示。
- **日付表示** — `Mon 1 Jun 2026` のように曜日・日・月・年をひと目で。
- **🍅 内蔵ポモドーロタイマー** — 25分集中 / 5分休憩。`Today: N` でその日に完了した回数を自動カウント（日付ごとに保存）。
- **ドラッグで移動** — 時計をつかんで好きな場所へ。
- **サイズ変更** — 右クリックメニューから XS〜XL のプリセットで拡大・縮小。
- **常に最前面（always-on-top）** — 他のウィンドウに隠れません。
- **透明背景・角丸の見た目** — デスクトップに自然になじむデザイン。
- **コンソール無しで起動** — `start_clock.vbs` をダブルクリックすれば黒い画面は出ません。
- **多重起動を防止（single-instance）** — Windows のミューテックスで、二重に開かない安心設計。

---

## 🎨 Design System / デザインシステム

このウィジェットの UI は、Tailwind の **Catalyst** UI キットのデザイン言語で統一されています。
*The UI follows Tailwind's **Catalyst** design system — applied consistently across the clock face, digital readout, and the right-click menu.*

- **フォント (Font):** Inter（`Inter, ui-sans-serif, system-ui, sans-serif`）
- **ニュートラル (Neutrals):** Tailwind `zinc` パレット（`zinc-950`〜`zinc-300` + white）でダークなサーフェスを構成。
- **アクセント (Accent):** `blue-500` (#3b82f6) — フォーカス・ホバー・秒針・アクセントチップに使用。
- **サーフェス (Surface):** Catalyst 流のダーク基調。角丸（rounded-xl）+ 1px の subtle ring（white 10%）+ `shadow-lg`。
- **メニュー (Menu):** 右クリックメニューは Catalyst の **Dropdown** に合わせてテーマ化（`zinc-800` 背景、項目ホバーで `blue-500`）。

| 要素 (Element) | トークン (Token) | 色 |
|----------------|------------------|----|
| 文字盤 (Face) | `zinc-900` | #18181b |
| 文字盤の縁 (Ring) | `zinc-700` | #3f3f46 |
| 目盛り (Ticks) | `zinc-300` | #d4d4d8 |
| 時針・分針 (Hour/Minute hands) | `white` | #ffffff |
| 秒針・アクセント (Second / Accent) | `blue-500` | #3b82f6 |
| メニュー背景 (Menu) | `zinc-800` | #27272a |
| メニュー hover | `blue-500` | #3b82f6 |
| 日付の文字 (Date text) | `zinc-400` | #a1a1aa |
| 補助テキスト (Muted text) | `zinc-500` | #71717a |
| ポモドーロ（作業 / 休憩） | `red-500` / `green-500` | #ef4444 / #22c55e |

> 🖱️ 右クリックメニューは Catalyst の **Dropdown** コンポーネントに合わせ、`zinc-800` の暗いサーフェスと `blue-500` ホバーでテーマ化されています。

---

## 🚀 Quick Start / すぐ使う

1. このリポジトリをダウンロード（または `git clone`）します。
2. Python 3.x がインストールされていれば、追加のインストールは **一切不要** です。
3. 次のどちらかで起動します。
   - `clock.pyw` を **ダブルクリック**
   - もしくは `start_clock.vbs` を **ダブルクリック**（コンソール画面が一切出ません ✨）

```text
AnalogClock-oss/
├── clock.pyw        ← 本体（これを実行）
└── start_clock.vbs  ← コンソール無しで起動するランチャー
```

> 💡 `pip install` も管理者権限も要りません。標準ライブラリ（tkinter）だけで動きます。

---

## 🍎 macOS

macOS でも追加インストール不要で動きます（標準の Python 3 + tkinter）。
*Works on macOS too — no extra install (system Python 3 + tkinter).*

1. **起動 (Run)**
   `start_clock.command` を **ダブルクリック** します。
   初回のみ実行権限を付与してください:
   ```sh
   chmod +x start_clock.command
   ```

2. **ログイン時の自動起動 + 自動復活 (Auto-start on login + auto-revive)**
   `launchd` の LaunchAgent を使うと、ログイン時に自動起動し、万一終了しても `KeepAlive` が再起動します。
   ```sh
   # 1) LaunchAgent をコピー
   cp com.analogclock.plist ~/Library/LaunchAgents/

   # 2) plist 内の clock.pyw のパスを自分の環境に合わせて編集
   #    （<string>...clock.pyw</string> を実際のフルパスへ）

   # 3) 読み込み（以後ログイン時に自動起動 / 終了時は自動復活）
   launchctl load ~/Library/LaunchAgents/com.analogclock.plist
   ```
   > `KeepAlive` が有効なので、時計がクラッシュ・終了しても `launchd` が自動で起動し直します。

> 🪟 **Windows ユーザーは従来どおり** `start_clock.vbs` + タスク スケジューラ（Task Scheduler）で自動起動・自動復旧します（下記「Auto-start」参照）。

---

## 🎮 Controls / 操作方法

### ⌨️ キーボード

| キー | 動作 |
|------|------|
| `Esc` | 終了 (Quit) |
| `Space` | ポモドーロの一時停止 / 再開 (Pause / Resume) |
| `p` | ポモドーロ開始 (Start) |
| `r` | リセット (Reset) |
| `+` / `-` | サイズ拡大 / 縮小 (Resize) |

### 🖱️ 右クリックメニュー

右クリックメニューは Catalyst の **Dropdown**（`zinc-800` 背景・`blue-500` ホバー）でテーマ化されています。

- **Start Pomodoro** — ポモドーロを開始
- **Pause / Resume** — 一時停止・再開
- **Reset** — リセット
- **Size** — サイズ変更（XS / S / M / L / XL）
- **Quit** — 終了

> 🖱️ 時計を **ドラッグ** すると、画面の好きな位置に移動できます。

---

## 🎨 Customization / カスタマイズ

`clock.pyw` の先頭にある定数を書き換えるだけで、見た目や動作を自由に調整できます。
*Edit the constants at the top of `clock.pyw` — no other changes needed.*

| 定数 (Constant) | 意味 (What it does) |
|-----------------|---------------------|
| `WINDOW_SIZE` | ウィンドウの大きさ（ピクセル） |
| `ALPHA` | 透明度（0.0=透明 〜 1.0=不透明） |
| `FONT_SIZE` | デジタル時刻・日付の文字サイズ |
| `UPDATE_MS` | 画面の更新間隔（ミリ秒） |
| `*_COLOR`（各色） | 各パーツの色（針・文字盤・背景・文字など。既定は Catalyst の zinc / blue-500） |
| `POMO_WORK_MIN` | ポモドーロの作業時間（分・既定25） |
| `POMO_BREAK_MIN` | ポモドーロの休憩時間（分・既定5） |
| `POMO_SOUND` | 完了時の音を鳴らすか (True / False) |
| `POMO_AUTO_LOOP` | 作業→休憩→作業…を自動で繰り返すか (True / False) |

---

## 🔁 Auto-start / 自動起動

PC を再起動しても、スリープから復帰しても、万一クラッシュしても、時計が **自動で復活** するように二重で仕込みます。
どちらも `pythonw.exe clock.pyw` を **直接** 呼び出すため、VBScript に依存せず、VBScript のエラーポップアップが出ることもありません。

1. **スタートアップ フォルダのショートカット**
   ログイン時に自動で起動します。
2. **タスク スケジューラのタスク**
   数分おきにチェックして、時計が動いていなければ起動し直します。
   → クラッシュ・スリープ・再起動のあとでも **自動復旧** します。

> ✅ どちらも `pythonw.exe clock.pyw` を直接実行（VBScript 非依存）なので、エラーダイアログが絶対に出ません。
> 🍎 macOS では上記「macOS」セクションの `launchd` LaunchAgent（`KeepAlive`）が同じ役割を果たします。

---

## 🔧 How it works / 仕組み

- **tkinter Canvas** に針・目盛り・デジタル時刻・日付を毎フレーム描画します（更新間隔は `UPDATE_MS`）。
- **常に最前面** は `-topmost` 属性、**透明・角丸の見た目** はウィンドウの透過設定で実現しています。
- **ポモドーロの完了回数** は `pomo_count.json` に「日付ごと」で保存します（`Today: N`）。
- **多重起動の防止** は Windows の **ミューテックス (mutex)** を使い、すでに起動中なら新しいプロセスはすぐ終了します。
- **コンソール非表示** は、拡張子 `.pyw`（＝ `pythonw.exe` で実行）と `start_clock.vbs` ランチャーによるものです。

---

## 💻 Requirements / 動作環境

- **OS:** Windows & macOS
- **Python:** 3.x（標準ライブラリの `tkinter` を使用）
- **依存パッケージ:** **なし** — `pip install` 不要 / 管理者権限不要 / 追加セットアップ不要。

---

## 📄 License / ライセンス

**MIT License** — 自由に使って・改変して・配布できます。
Author: **niki-nakamura** ／ 詳細は [LICENSE](LICENSE) をご覧ください。

---

<p align="center"><sub>Made with 🕒 + 🍅 by <a href="https://github.com/niki-nakamura">niki-nakamura</a></sub></p>
