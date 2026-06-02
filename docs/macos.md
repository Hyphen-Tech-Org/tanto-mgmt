# 🍎 macOS セットアップガイド / macOS Setup Guide

Mac で **Analog Clock** を使うための、やさしい手順書です。順番にコピペしていくだけで動きます。
*A friendly, step-by-step guide for running Analog Clock on a Mac. Just copy-paste the commands in order.*

> ⬅️ Windows の方は [README.md](../README.md) に戻ってください。

---

## 1. 必要なもの / Requirements

- **Python 3**（`python3`）— macOS には標準で入っていることが多いです。確認するには:

  ```sh
  python3 --version
  ```

  もし入っていなければ [python.org](https://www.python.org/downloads/macos/) からインストールしてください。

- **PySide6**（推奨版 `clock_qt.py` 用）をインストールします:

  ```sh
  pip3 install PySide6-Essentials
  ```

> 🪶 メモリ使用量は約 60 MB と軽量です。
> 💡 `pip3 install` ができない / もっと軽くしたい場合は、依存ゼロの **`clock.pyw`**（tkinter）も Mac でそのまま動きます。下の「補足」を参照。

---

## 2. 起動する / Run

ターミナルを開き、プロジェクトのフォルダに移動してから、初回だけ実行権限を付けます。

```sh
# プロジェクトのフォルダへ移動（例）
cd ~/AnalogClock-oss

# 初回だけ：ランチャーに実行権限を付与
chmod +x start_clock.command
```

あとは **`start_clock.command` をダブルクリック** するだけで時計が起動します 🎉
*Then just double-click `start_clock.command`.*

コマンドで直接起動したい場合はこちら:

```sh
python3 clock_qt.py
```

---

## 3. ログイン時の自動起動 + 自動復活 / Auto-start + Auto-revive

Mac では **`launchd`** の **LaunchAgent** を使います。ログイン時に自動で起動し、万一終了してもすぐ再起動します（Windows の「スタートアップ + 監視タスク」に相当）。

### 手順 (Steps)

**① plist にパスを書き込む**

付属の `com.analogclock.plist` を開き、`clock_qt.py` の場所を **絶対パス（フルパス）** に書き換えます。

```xml
<key>ProgramArguments</key>
<array>
    <string>/usr/bin/python3</string>
    <string>/Users/あなたのユーザー名/AnalogClock-oss/clock_qt.py</string>   <!-- ここを実際のフルパスに -->
</array>
```

> 💡 フルパスがわからないときは、フォルダ内で次を実行するとコピーできます:
> ```sh
> echo "$(pwd)/clock_qt.py"
> ```

**② LaunchAgents フォルダにコピーする**

```sh
cp com.analogclock.plist ~/Library/LaunchAgents/
```

**③ 読み込む（これで有効化）**

```sh
launchctl load ~/Library/LaunchAgents/com.analogclock.plist
```

これで完了です。`RunAtLoad` によりログイン時に自動起動し、`KeepAlive` により終了しても自動で再起動します。
*`RunAtLoad` starts it at login; `KeepAlive` auto-restarts it if it ever quits.*

### 自動起動をやめる / Stop

```sh
launchctl unload ~/Library/LaunchAgents/com.analogclock.plist
```

---

## 4. 操作方法 / Controls

Windows 版とまったく同じです。*Same as Windows.*

### 🖱️ 右クリックメニュー

| 項目 | 動作 | ショートカット |
|------|------|------|
| **Start Pomodoro** | ポモドーロ開始 | `P` |
| **Pause / Resume** | 一時停止 / 再開 | `Space` |
| **Reset** | リセット | `R` |
| **Theme ▸ Light / Dark** | テーマ切り替え（既定 Light） | — |
| **Size ▸ XS〜XL** | サイズ変更 | — |
| **Quit** | 終了 | `Esc` |

- 時計を **ドラッグ** すると好きな位置へ移動できます（位置は記憶されます）。
- 設定（テーマ・サイズ・位置）は **`settings.json`** に保存され、次回も引き継がれます。

---

## 補足 / Notes

- 🪶 **軽量版 `clock.pyw` も Mac で動きます。** こちらは Python 標準ライブラリの **tkinter** だけを使うので `pip install` 不要です（見た目はシンプル版）。
  ```sh
  python3 clock.pyw
  ```
- `start_clock.command` は時計を **detached（バックグラウンド）** で起動するため、ターミナルのウィンドウは残りません。
- ダブルクリック時に「開けません」と出る場合は、`chmod +x start_clock.command` を実行したか確認してください。

---

<p align="center"><sub>Made with 🕒 + 🍅 by <a href="https://github.com/niki-nakamura">niki-nakamura</a> @ Hyphen Technologies</sub></p>
