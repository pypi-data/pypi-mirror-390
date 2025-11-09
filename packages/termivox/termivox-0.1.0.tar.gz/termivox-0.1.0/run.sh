#!/bin/bash
# Termivox launcher script
# Activates the virtual environment and starts voice recognition with toggle control

cd "$(dirname "$0")"

source termivox-env/bin/activate

echo "🎤 Termivox Voice Recognition Bridge"
echo "======================================"
echo ""
echo "Starting voice recognition with toggle control..."
echo "Speak commands and they will be typed in your active window."
echo ""
echo "🎛️  TOGGLE CONTROL:"
echo "  - Hotkey: Ctrl+Alt+V (toggle ON/OFF from anywhere)"
echo "  - Tray Icon: Click icon in system tray"
echo "  - Configure interfaces in config/settings.json"
echo ""
echo "🎤 VOICE COMMANDS:"
echo "  - Say punctuation names: 'comma', 'period', 'question mark', etc."
echo "  - 'new line', 'new paragraph', 'tab'"
echo "  - 'copy', 'paste', 'click', 'scroll up/down'"
echo ""
echo "Press Ctrl+C to stop."
echo ""

python src/main.py --lang en
