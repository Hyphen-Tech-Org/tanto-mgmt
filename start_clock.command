#!/bin/bash
# AnalogClock launcher for macOS — double-click to run.
# First time only, make it executable:  chmod +x start_clock.command
# (clock.pyw uses only the Python standard library; no pip install needed.)
cd "$(dirname "$0")"
# Launch detached so no Terminal window stays attached.
nohup python3 clock.pyw >/dev/null 2>&1 &
