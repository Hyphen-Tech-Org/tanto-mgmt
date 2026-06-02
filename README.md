![Analog Clock](assets/hero.svg)

# 🕒 Analog Clock

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-0078D6.svg)](#requirements--動作環境)
[![Python: 3.x](https://img.shields.io/badge/python-3.x-3776AB.svg)](https://www.python.org/)
[![Dependencies: none](https://img.shields.io/badge/dependencies-none-success.svg)](#requirements--動作環境)

> **インストール不要・管理者権限不要・設定不要。** ダブルクリックするだけで動く、いつも最前面に浮かぶ Windows 向けのアナログ時計ウィジェット。
> *A portable, always-on-top desktop analog clock for Windows. Pure Python (tkinter) — just run it.*

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
| `*_COLOR`（各色） | 各パーツの色（針・文字盤・背景・文字など） |
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

---

## 🔧 How it works / 仕組み

- **tkinter Canvas** に針・目盛り・デジタル時刻・日付を毎フレーム描画します（更新間隔は `UPDATE_MS`）。
- **常に最前面** は `-topmost` 属性、**透明・角丸の見た目** はウィンドウの透過設定で実現しています。
- **ポモドーロの完了回数** は `pomo_count.json` に「日付ごと」で保存します（`Today: N`）。
- **多重起動の防止** は Windows の **ミューテックス (mutex)** を使い、すでに起動中なら新しいプロセスはすぐ終了します。
- **コンソール非表示** は、拡張子 `.pyw`（＝ `pythonw.exe` で実行）と `start_clock.vbs` ランチャーによるものです。

---

## 💻 Requirements / 動作環境

- **OS:** Windows
- **Python:** 3.x（標準ライブラリの `tkinter` を使用）
- **依存パッケージ:** **なし** — `pip install` 不要 / 管理者権限不要 / 追加セットアップ不要。

---

## 📄 License / ライセンス

**MIT License** — 自由に使って・改変して・配布できます。
Author: **niki-nakamura** ／ 詳細は [LICENSE](LICENSE) をご覧ください。

---

<p align="center"><sub>Made with 🕒 + 🍅 by <a href="https://github.com/niki-nakamura">niki-nakamura</a></sub></p>
