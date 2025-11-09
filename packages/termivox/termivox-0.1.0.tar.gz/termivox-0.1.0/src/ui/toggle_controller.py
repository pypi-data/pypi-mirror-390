"""
Core toggle controller for Termivox voice recognition.

Manages ON/OFF state and coordinates multiple control interfaces.
Thread-safe state management with event broadcasting to all registered interfaces.

♠️ Nyro: Central state machine - the anchor for all toggle interfaces
🎸 JamAI: Event-driven rhythm - state changes ripple through all listeners
🌿 Aureon: The bridge between intention and action
"""

import threading
from enum import Enum
from typing import Callable, List, Optional


class ToggleState(Enum):
    """Voice recognition state."""
    ACTIVE = "active"    # Voice recognition running
    PAUSED = "paused"    # Voice recognition muted


class ToggleController:
    """
    Central controller for voice recognition toggle functionality.

    Manages state transitions and notifies all registered interfaces
    when the state changes. Thread-safe for use with multiple interfaces.

    Example:
        recognizer = Recognizer()
        controller = ToggleController(recognizer)

        # Register interface callback
        controller.register_interface(my_interface_callback)

        # Toggle state
        controller.toggle()  # ACTIVE -> PAUSED or PAUSED -> ACTIVE
    """

    def __init__(self, recognizer):
        """
        Initialize toggle controller.

        Args:
            recognizer: Voice recognizer instance with pause()/resume() methods
        """
        self.recognizer = recognizer
        self._state = ToggleState.ACTIVE  # Start active
        self._lock = threading.Lock()
        self._interfaces: List[Callable[[ToggleState], None]] = []

    def register_interface(self, callback: Callable[[ToggleState], None]) -> None:
        """
        Register an interface to receive state change notifications.

        Args:
            callback: Function called with new state when state changes
                     Signature: callback(state: ToggleState) -> None
        """
        with self._lock:
            if callback not in self._interfaces:
                self._interfaces.append(callback)
                # Immediately notify new interface of current state
                callback(self._state)

    def unregister_interface(self, callback: Callable[[ToggleState], None]) -> None:
        """
        Unregister an interface from state change notifications.

        Args:
            callback: Previously registered callback function
        """
        with self._lock:
            if callback in self._interfaces:
                self._interfaces.remove(callback)

    def get_state(self) -> ToggleState:
        """
        Get current toggle state.

        Returns:
            Current ToggleState (ACTIVE or PAUSED)
        """
        with self._lock:
            return self._state

    def is_active(self) -> bool:
        """
        Check if voice recognition is currently active.

        Returns:
            True if ACTIVE, False if PAUSED
        """
        return self.get_state() == ToggleState.ACTIVE

    def toggle(self) -> ToggleState:
        """
        Toggle between ACTIVE and PAUSED states.

        Returns:
            New state after toggle
        """
        with self._lock:
            if self._state == ToggleState.ACTIVE:
                return self._pause()
            else:
                return self._resume()

    def pause(self) -> ToggleState:
        """
        Explicitly pause voice recognition.

        Returns:
            New state (PAUSED)
        """
        with self._lock:
            return self._pause()

    def resume(self) -> ToggleState:
        """
        Explicitly resume voice recognition.

        Returns:
            New state (ACTIVE)
        """
        with self._lock:
            return self._resume()

    def _pause(self) -> ToggleState:
        """
        Internal pause implementation (must be called with lock held).

        Returns:
            New state (PAUSED)
        """
        if self._state == ToggleState.PAUSED:
            return self._state  # Already paused, no-op

        self._state = ToggleState.PAUSED
        self.recognizer.pause()
        self._broadcast_state_change()
        return self._state

    def _resume(self) -> ToggleState:
        """
        Internal resume implementation (must be called with lock held).

        Returns:
            New state (ACTIVE)
        """
        if self._state == ToggleState.ACTIVE:
            return self._state  # Already active, no-op

        self._state = ToggleState.ACTIVE
        self.recognizer.resume()
        self._broadcast_state_change()
        return self._state

    def _broadcast_state_change(self) -> None:
        """
        Notify all registered interfaces of state change.
        Called with lock held.
        """
        for callback in self._interfaces:
            try:
                callback(self._state)
            except Exception as e:
                # Don't let one interface's error break others
                print(f"[ToggleController] Interface callback error: {e}")

    def shutdown(self) -> None:
        """
        Clean shutdown - unregister all interfaces.
        """
        with self._lock:
            self._interfaces.clear()
