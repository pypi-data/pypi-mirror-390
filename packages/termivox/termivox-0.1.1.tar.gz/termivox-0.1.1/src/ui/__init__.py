"""
UI module for Termivox toggle controls.

Provides multiple interfaces for controlling voice recognition ON/OFF:
- Hotkey (global keyboard shortcut)
- System tray icon
- Desktop widget
- Hardware button support (future)

All interfaces connect to a central ToggleController.
"""

from .toggle_controller import ToggleController, ToggleState

__all__ = ['ToggleController', 'ToggleState']
