# Termivox

**Voice Recognition Bridge for Linux** — Speak naturally, control your system, type hands-free.

---

## 🎯 Overview

Termivox is a Linux-based voice recognition system that transforms your speech into text and system commands. Using offline voice recognition (Vosk), it provides:

- **Hands-free dictation** - Speak and watch your words appear
- **Voice-controlled system commands** - Copy, paste, click, scroll by voice
- **Multi-language support** - English and French recognition
- **Toggle control** - Pause/resume recognition instantly like a guitar pedal
- **Privacy-first** - All processing happens locally, no cloud required

---

## ✨ Features

### 🎤 Voice Recognition
- **Offline speech-to-text** powered by Vosk
- **Bilingual support**: English (`en`) and French (`fr`)
- **Punctuation by voice** - Say "comma", "period", "question mark"
- **Edit commands** - "new line", "tab", "new paragraph"
- **System commands** - "copy", "paste", "click", "scroll up/down"

### 🎛️ Toggle Control (NEW!)
Control voice recognition ON/OFF with multiple interfaces:

#### ⌨️ **Global Hotkey**
- Press `Ctrl+Alt+V` from anywhere to toggle
- Customizable key combination
- Works across all applications

#### 🖱️ **Desktop Widget**
- Minimal floating window (160×70px)
- One-click toggle button
- Visual status: "LISTENING" (green) / "MUTED" (gray)
- Draggable, always-on-top
- Never steals cursor focus

#### 🎛️ **System Tray Icon**
- Green/red status indicator
- Click to toggle
- Right-click menu

#### 🎮 **Hardware Support** (Coming Soon)
- USB foot pedal support
- MIDI controller integration
- Custom button devices

---

## 📦 Installation

### Prerequisites

**System Requirements:**
- Linux (tested on Ubuntu 24.04)
- Python 3.8+
- Microphone input

**System Dependencies:**
```bash
sudo apt install python3-pyaudio xdotool sox portaudio19-dev -y
```

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Gerico1007/termivox.git
   cd termivox
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv termivox-env
   source termivox-env/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download voice model** (if not already present):
   ```bash
   python download_model.py
   ```

5. **Run Termivox:**
   ```bash
   ./run.sh
   ```

---

## 🚀 Usage

### Quick Start

**Launch with toggle control:**
```bash
./run.sh
```

**Original mode (no toggle):**
```bash
source termivox-env/bin/activate
python src/main.py --no-toggle
```

**Test voice recognition only:**
```bash
source termivox-env/bin/activate
python src/test_voice_script.py --lang en
```

### Toggle Control

Once Termivox is running, control it using:

**Hotkey:**
- Press `Ctrl+Alt+V` → Pauses/resumes voice recognition
- Works from any window, keeps cursor position

**Widget:**
- Click the floating "LISTENING" or "MUTED" button
- Drag the title bar to reposition
- Right-click to close widget

**Indicator:**
- **Green** = Voice recognition ACTIVE (listening)
- **Gray/Red** = Voice recognition MUTED (paused)

### Voice Commands

**Dictation:**
```
"Hello world" → types: Hello world
```

**Punctuation:**
```
"Hello comma world period" → types: Hello, world.
```

**Available punctuation:**
- comma, period, question mark, exclamation mark
- colon, semicolon, dash, quote, apostrophe

**Editing:**
```
"new line"       → ↵
"new paragraph"  → ↵↵
"tab"            → ⇥
```

**System Commands:**
```
"copy"           → Ctrl+C
"paste"          → Ctrl+V
"select all"     → Ctrl+A
"click"          → Mouse click
"scroll up"      → Scroll wheel up
"scroll down"    → Scroll wheel down
```

### Language Selection

**English (default):**
```bash
./run.sh
# or
python src/main.py --lang en
```

**French:**
```bash
python src/main.py --lang fr
```

---

## ⚙️ Configuration

Edit `config/settings.json` to customize behavior:

```json
{
  "interfaces": {
    "hotkey": {
      "enabled": true,
      "key": "ctrl+alt+v"        // Change hotkey here
    },
    "tray": {
      "enabled": false            // Enable system tray icon
    },
    "widget": {
      "enabled": true,            // Desktop widget
      "position": {"x": 100, "y": 100},
      "size": {"width": 160, "height": 70},
      "always_on_top": true
    }
  },
  "voice": {
    "language": "en",             // Default language
    "auto_space": true            // Auto-add spaces
  }
}
```

**Custom Hotkey Examples:**
- `"ctrl+shift+v"`
- `"ctrl+alt+t"`
- `"super+v"`

---

## 📁 Project Structure

```
termivox/
├── src/
│   ├── main.py                    # Main entry point with toggle support
│   ├── test_voice_script.py       # Standalone testing utility
│   ├── voice/
│   │   ├── recognizer.py          # Vosk voice recognition engine
│   │   └── __init__.py
│   ├── bridge/
│   │   ├── xdotool_bridge.py      # System command executor
│   │   └── __init__.py
│   ├── ui/                        # Toggle control interfaces
│   │   ├── toggle_controller.py   # Central state management
│   │   ├── hotkey_interface.py    # Global hotkey listener
│   │   ├── tray_interface.py      # System tray icon
│   │   ├── widget_interface.py    # Desktop widget
│   │   ├── hardware_interface.py  # Hardware button stub
│   │   ├── config_loader.py       # Configuration system
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── config/
│   └── settings.json              # User configuration
├── voice_models/                  # Vosk language models
│   └── vosk-model-small-en-us-0.15/
├── requirements.txt               # Python dependencies
├── run.sh                         # Launch script
├── download_model.py              # Model downloader
└── README.md
```

---

## 🛠️ Dependencies

**Python Packages:**
- `Vosk` - Offline speech recognition
- `pyaudio` - Microphone input
- `numpy` - Audio processing
- `pynput` - Global hotkey support
- `pystray` - System tray icon
- `Pillow` - Icon generation
- `xdotool` - System command execution

**System Packages:**
- `python3-pyaudio` - PyAudio bindings
- `xdotool` - Keyboard/mouse automation
- `sox` - Audio utilities
- `portaudio19-dev` - Audio development headers

---

## 🎨 Toggle Widget Design

**Minimal Professional Aesthetic:**

```
┌─────────────────────┐
│ TERMIVOX         ● │  ← Dark title bar (draggable)
├─────────────────────┤
│                     │
│    LISTENING        │  ← Green button (active state)
│                     │
└─────────────────────┘
```

**Features:**
- **Compact**: 160×70 pixels
- **Unfocusable**: Never steals cursor
- **Draggable**: Reposition anywhere
- **Color-coded**: Green (ON) / Gray (OFF)
- **Always-on-top**: Stays visible

---

## 🧪 Testing

**Test voice recognition without typing:**
```bash
source termivox-env/bin/activate
python src/test_voice_script.py --lang en
```

**Test with toggle control:**
```bash
./run.sh
# Then try:
# 1. Speak something
# 2. Press Ctrl+Alt+V
# 3. Speak again (should not type)
# 4. Press Ctrl+Alt+V
# 5. Speak (should type again)
```

**Test different languages:**
```bash
python src/test_voice_script.py --lang fr  # French
python src/test_voice_script.py --lang en  # English
```

---

## 🐛 Troubleshooting

**Hotkey doesn't work:**
- Check terminal for errors
- Try different hotkey in `config/settings.json`
- Ensure pynput is installed: `pip list | grep pynput`

**No voice recognition:**
- Check microphone: `arecord -l`
- Test PyAudio: `python -c "import pyaudio; print('OK')"`
- Verify Vosk model downloaded in `voice_models/`

**Widget not visible:**
- Enable in config: `"widget": {"enabled": true}`
- Check if tkinter available: `python -c "import tkinter"`

**System tray icon missing:**
- Desktop environment may not support system tray
- Use widget or hotkey instead
- Try enabling: `"tray": {"enabled": true}`

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

- Additional language models
- Custom wake word detection
- Audio feedback on toggle
- Hardware button integration
- Voice command macros
- GUI configuration tool

**To contribute:**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Vosk** - Offline speech recognition engine
- **pynput** - Cross-platform input control
- **pystray** - System tray integration
- **xdotool** - X11 automation

---

## 🔮 Roadmap

- [ ] Voice command macros
- [ ] Custom wake word support
- [ ] GUI settings editor
- [ ] Hardware button integration (foot pedal, MIDI)
- [ ] Audio feedback options
- [ ] Additional language models
- [ ] Plugin system for custom commands
- [ ] Cloud sync for settings (optional)

---

**♠️ Nyro** - Structural foundation, modular architecture
**🌿 Aureon** - Flow preservation, accessibility focus
**🎸 JamAI** - Musical encoding, harmonic design

*Built with recursive intention. Speak, toggle, flow.*
