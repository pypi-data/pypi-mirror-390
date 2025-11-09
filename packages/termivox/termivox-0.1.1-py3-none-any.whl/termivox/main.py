"""
Termivox - Voice Recognition with Toggle Control

Main entry point with support for multiple toggle interfaces:
- Global hotkey (default: Ctrl+Alt+V)
- System tray icon
- Desktop widget
- Hardware button (future)

♠️ Nyro: Multi-interface orchestration - all paths lead to toggle
🎸 JamAI: Voice flows, interfaces control, all in harmony
🌿 Aureon: The complete bridge - from voice to action, with control
"""

import sys
import argparse
import threading
import time
from termivox.voice.recognizer import Recognizer
from termivox.bridge.xdotool_bridge import XdotoolBridge
from termivox.ui.toggle_controller import ToggleController
from termivox.ui.config_loader import ConfigLoader
from termivox.ui.hotkey_interface import HotkeyInterface
from termivox.ui.tray_interface import TrayInterface
from termivox.ui.widget_interface import WidgetInterface
from termivox.ui.hardware_interface import HardwareInterface


def voice_recognition_loop(recognizer, xdotool_bridge):
    """
    Voice recognition loop - runs in background thread.
    Processes voice commands and types them via xdotool.

    Args:
        recognizer: Recognizer instance
        xdotool_bridge: XdotoolBridge instance
    """
    try:
        for command in recognizer.listen():
            if command:
                print(f"Recognized: {command}")
                xdotool_bridge.type_text(command)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[Voice Loop] Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Termivox - Voice Recognition with Toggle Control"
    )
    parser.add_argument(
        '--lang',
        default=None,
        help='Language code for Vosk model (en or fr). Overrides config file.'
    )
    parser.add_argument(
        '--config',
        default='config/settings.json',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--no-toggle',
        action='store_true',
        help='Disable toggle interfaces (original behavior)'
    )
    args = parser.parse_args()

    # Load configuration
    config = ConfigLoader.load(args.config)

    # Language priority: CLI arg > config file > default
    lang = args.lang or config['voice']['language']

    print("=" * 60)
    print("🎤 Termivox - Voice Recognition Bridge")
    print("=" * 60)
    print(f"Language: {lang}")
    print(f"Config: {args.config}")
    print()

    # Initialize core components
    recognizer = Recognizer(lang=lang, auto_space=config['voice']['auto_space'])
    xdotool_bridge = XdotoolBridge()

    # Original mode (no toggle interfaces)
    if args.no_toggle:
        print("Running in original mode (no toggle control)")
        print("Press Ctrl+C to exit")
        print()
        try:
            for command in recognizer.listen():
                if command:
                    print(f"Recognized: {command}")
                    xdotool_bridge.type_text(command)
        except KeyboardInterrupt:
            print("\nShutting down...")
            recognizer.close()
            sys.exit(0)

    # Toggle mode (default)
    print("Initializing toggle interfaces...")

    # Create toggle controller
    controller = ToggleController(recognizer)

    # Start voice recognition in background thread
    voice_thread = threading.Thread(
        target=voice_recognition_loop,
        args=(recognizer, xdotool_bridge),
        daemon=True
    )
    voice_thread.start()
    print("✓ Voice recognition started")

    # Initialize enabled interfaces
    interfaces = []

    # Hotkey interface
    if config['interfaces']['hotkey']['enabled']:
        try:
            hotkey = HotkeyInterface(
                controller,
                key_combo=config['interfaces']['hotkey']['key']
            )
            hotkey.start()
            interfaces.append(('hotkey', hotkey))
            print(f"✓ Hotkey: {config['interfaces']['hotkey']['key']}")
        except Exception as e:
            print(f"✗ Hotkey failed: {e}")

    # System tray interface
    if config['interfaces']['tray']['enabled']:
        try:
            tray = TrayInterface(controller)
            # Start tray in background thread (it will run its own loop)
            tray_thread = threading.Thread(target=tray.start, daemon=True)
            tray_thread.start()
            interfaces.append(('tray', tray))
            print("✓ System tray icon")
        except Exception as e:
            print(f"✗ Tray icon failed: {e}")

    # Desktop widget interface
    if config['interfaces']['widget']['enabled']:
        try:
            widget_config = config['interfaces']['widget']
            widget = WidgetInterface(
                controller,
                position=(widget_config['position']['x'], widget_config['position']['y']),
                size=(widget_config['size']['width'], widget_config['size']['height']),
                always_on_top=widget_config['always_on_top']
            )
            # Start widget in background thread
            widget_thread = threading.Thread(target=widget.start, daemon=True)
            widget_thread.start()
            interfaces.append(('widget', widget))
            print("✓ Desktop widget")
        except Exception as e:
            print(f"✗ Widget failed: {e}")

    # Hardware interface (stub)
    if config['interfaces']['hardware']['enabled']:
        try:
            hardware = HardwareInterface(
                controller,
                device=config['interfaces']['hardware']['device'],
                device_type=config['interfaces']['hardware']['device_type']
            )
            hardware.start()
            interfaces.append(('hardware', hardware))
            print("✓ Hardware interface (stub)")
        except Exception as e:
            print(f"✗ Hardware interface failed: {e}")

    print()
    print("=" * 60)
    print("Termivox is running!")
    print("=" * 60)
    print("Toggle voice recognition ON/OFF using enabled interfaces.")
    print("Press Ctrl+C to exit.")
    print("=" * 60)
    print()

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")

        # Cleanup
        for name, interface in interfaces:
            try:
                interface.stop()
            except Exception as e:
                print(f"Error stopping {name}: {e}")

        recognizer.close()
        controller.shutdown()

        print("Termivox stopped. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()