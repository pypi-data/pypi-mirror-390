"""
System tray icon interface for Termivox toggle control.

Displays an icon in the system tray that changes color based on
voice recognition state (green=ON, red=OFF). Right-click menu
provides toggle and exit options.

♠️ Nyro: Visual state indicator - always visible, always informed
🎸 JamAI: Green glow for active, red for silent - the visual rhythm
🌿 Aureon: A gentle reminder of the voice bridge's presence
"""

import pystray
from PIL import Image, ImageDraw
from typing import Optional
import threading
from .toggle_controller import ToggleState


class TrayInterface:
    """
    System tray icon for toggle control.

    Shows current state visually and provides menu for toggle/exit.

    Example:
        controller = ToggleController(recognizer)
        tray = TrayInterface(controller)
        tray.start()  # Runs in background, blocks until exit
    """

    def __init__(self, controller):
        """
        Initialize tray icon interface.

        Args:
            controller: ToggleController instance
        """
        self.controller = controller
        self._icon: Optional[pystray.Icon] = None
        self._running = False

        # Register for state change notifications
        self.controller.register_interface(self._on_state_change)

    def _create_icon(self, color: str) -> Image.Image:
        """
        Create a simple colored circle icon.

        Args:
            color: Color name ('green' or 'red')

        Returns:
            PIL Image for tray icon
        """
        # Create 64x64 image with transparency
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw colored circle
        color_map = {
            'green': (76, 175, 80, 255),  # Material green
            'red': (244, 67, 54, 255)      # Material red
        }
        fill_color = color_map.get(color, color_map['green'])

        # Draw circle with padding
        padding = 8
        draw.ellipse(
            [padding, padding, size - padding, size - padding],
            fill=fill_color,
            outline=(255, 255, 255, 200),
            width=2
        )

        return image

    def _on_state_change(self, state: ToggleState):
        """
        Called when controller state changes.
        Updates tray icon color.

        Args:
            state: New ToggleState
        """
        if not self._icon:
            return

        if state == ToggleState.ACTIVE:
            self._icon.icon = self._create_icon('green')
            self._icon.title = "Termivox - ACTIVE (listening)"
        else:
            self._icon.icon = self._create_icon('red')
            self._icon.title = "Termivox - PAUSED (muted)"

    def _toggle_action(self, icon, item):
        """
        Menu action: Toggle voice recognition.
        """
        self.controller.toggle()

    def _exit_action(self, icon, item):
        """
        Menu action: Exit application.
        """
        print("[Tray] Exit requested")
        self.stop()

    def start(self):
        """
        Start tray icon.
        Blocks until stop() is called or user exits via menu.
        """
        if self._running:
            print("[Tray] Already running")
            return

        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem(
                "Toggle Voice Recognition",
                self._toggle_action,
                default=True
            ),
            pystray.MenuItem("Exit", self._exit_action)
        )

        # Get initial state
        initial_state = self.controller.get_state()
        if initial_state == ToggleState.ACTIVE:
            icon_image = self._create_icon('green')
            title = "Termivox - ACTIVE (listening)"
        else:
            icon_image = self._create_icon('red')
            title = "Termivox - PAUSED (muted)"

        # Create icon
        self._icon = pystray.Icon(
            "termivox",
            icon_image,
            title,
            menu
        )

        self._running = True
        print("[Tray] Starting icon...")

        # Run (blocks until stop())
        self._icon.run()

    def start_async(self):
        """
        Start tray icon in background thread.
        Returns immediately.
        """
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()

    def stop(self):
        """
        Stop tray icon and exit.
        """
        if not self._running:
            return

        if self._icon:
            self._icon.stop()
            self._icon = None

        self._running = False
        print("[Tray] Stopped")

    def is_running(self) -> bool:
        """
        Check if tray icon is active.

        Returns:
            True if running, False otherwise
        """
        return self._running
