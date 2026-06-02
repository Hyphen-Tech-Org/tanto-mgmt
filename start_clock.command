#!/bin/bash
# AnalogClock launcher for macOS — double-click to run.
# First time only, make it executable:  chmod +x start_clock.command
# Requires PySide6:  pip3 install PySide6-Essentials
cd "$(dirname "$0")"
# Launch detached so no Terminal window stays attached.
nohup python3 clock_qt.py >/dev/null 2>&1 &
