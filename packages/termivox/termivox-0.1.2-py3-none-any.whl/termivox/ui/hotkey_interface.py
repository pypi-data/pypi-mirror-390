"""
Global hotkey interface for Termivox toggle control.

Registers a keyboard shortcut (default: Ctrl+Alt+V) that toggles
voice recognition ON/OFF from anywhere.

♠️ Nyro: Keyboard listener - the invisible trigger
🎸 JamAI: Press the key, flip the state - instant rhythm change
🌿 Aureon: Like a guitar pedal - one tap, instant response
"""

from pynput import keyboard
from typing import Optional
import threading


class HotkeyInterface:
    """
    Global hotkey listener for toggle control.

    Registers a configurable keyboard combination and calls
    controller.toggle() when pressed.

    Example:
        controller = ToggleController(recognizer)
        hotkey = HotkeyInterface(controller, key_combo="ctrl+alt+v")
        hotkey.start()  # Begins listening in background
    """

    def __init__(self, controller, key_combo="ctrl+alt+v"):
        """
        Initialize hotkey interface.

        Args:
            controller: ToggleController instance
            key_combo: Keyboard shortcut (e.g., "ctrl+alt+v", "ctrl+shift+t")
        """
        self.controller = controller
        self.key_combo = key_combo
        self._listener: Optional[keyboard.GlobalHotKeys] = None
        self._running = False

        # Parse key combination
        self._hotkey_config = self._parse_hotkey(key_combo)

    def _parse_hotkey(self, key_combo: str) -> dict:
        """
        Parse hotkey string into pynput format.

        Args:
            key_combo: String like "ctrl+alt+v"

        Returns:
            Dictionary mapping hotkey to callback
        """
        # Convert common names to pynput format
        # Modifier keys (ctrl, alt, shift, cmd) need angle brackets
        # Regular keys (letters, numbers) do NOT use angle brackets
        modifiers = {'ctrl', 'alt', 'shift', 'cmd', 'win', 'super'}

        keys = key_combo.lower().replace(" ", "").split('+')
        formatted_keys = []
        for key in keys:
            if key in modifiers:
                formatted_keys.append(f'<{key}>')
            else:
                formatted_keys.append(key)

        formatted = '+'.join(formatted_keys)
        return {formatted: self._on_hotkey_press}

    def _on_hotkey_press(self):
        """
        Called when hotkey is pressed.
        Toggles the controller state.
        """
        try:
            new_state = self.controller.toggle()
            print(f"[Hotkey] Toggled to: {new_state.value}")
        except Exception as e:
            print(f"[Hotkey] Error toggling: {e}")

    def start(self):
        """
        Start listening for hotkey presses.
        Runs in background thread.
        """
        if self._running:
            print("[Hotkey] Already running")
            return

        try:
            self._listener = keyboard.GlobalHotKeys(self._hotkey_config)
            self._listener.start()
            self._running = True
            print(f"[Hotkey] Listening for: {self.key_combo}")
        except Exception as e:
            print(f"[Hotkey] Failed to start: {e}")
            raise

    def stop(self):
        """
        Stop listening for hotkey presses.
        """
        if not self._running:
            return

        try:
            if self._listener:
                self._listener.stop()
                self._listener = None
            self._running = False
            print("[Hotkey] Stopped")
        except Exception as e:
            print(f"[Hotkey] Error stopping: {e}")

    def is_running(self) -> bool:
        """
        Check if hotkey listener is active.

        Returns:
            True if listening, False otherwise
        """
        return self._running
