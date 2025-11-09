"""
Hardware button interface for Termivox toggle control.

FUTURE IMPLEMENTATION: Support for physical buttons, foot pedals,
MIDI controllers, and other USB/hardware devices.

♠️ Nyro: Physical toggle - the ultimate pedal experience
🎸 JamAI: Press the pedal, feel the click, change the rhythm
🌿 Aureon: True tactile connection - foot, hand, or custom trigger
"""

from typing import Optional
import threading


class HardwareInterface:
    """
    Hardware button interface (STUB - Future Implementation).

    Will support:
    - USB foot pedals
    - MIDI controllers
    - Custom button devices
    - GPIO pins (Raspberry Pi)

    Example (planned):
        controller = ToggleController(recognizer)
        hardware = HardwareInterface(controller, device="/dev/input/event0")
        hardware.start()

    IMPLEMENTATION NOTES:
    =====================

    For USB Devices (evdev):
    ------------------------
    import evdev
    from evdev import InputDevice, categorize, ecodes

    device = InputDevice('/dev/input/event0')
    for event in device.read_loop():
        if event.type == ecodes.EV_KEY:
            if event.value == 1:  # Key press
                controller.toggle()

    For MIDI Controllers:
    ---------------------
    import rtmidi

    midiin = rtmidi.MidiIn()
    ports = midiin.get_ports()
    midiin.open_port(0)

    def midi_callback(message, data):
        if message[0] == 144:  # Note on
            controller.toggle()

    midiin.set_callback(midi_callback)

    For GPIO (Raspberry Pi):
    ------------------------
    import RPi.GPIO as GPIO

    BUTTON_PIN = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def button_callback(channel):
        controller.toggle()

    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING,
                          callback=button_callback, bouncetime=300)

    Required Dependencies:
    ----------------------
    - evdev (USB devices): pip install evdev
    - python-rtmidi (MIDI): pip install python-rtmidi
    - RPi.GPIO (Raspberry Pi): pip install RPi.GPIO

    """

    def __init__(self, controller, device=None, device_type="usb"):
        """
        Initialize hardware interface (STUB).

        Args:
            controller: ToggleController instance
            device: Device path or identifier
            device_type: Type of device ("usb", "midi", "gpio")
        """
        self.controller = controller
        self.device = device
        self.device_type = device_type
        self._running = False

        print("[Hardware] Interface is a stub - not yet implemented")
        print(f"[Hardware] Configured for: {device_type} device at {device}")

    def start(self):
        """
        Start hardware button listener (STUB).

        FUTURE: Will initialize device and start listening for button presses.
        """
        if self._running:
            print("[Hardware] Already running (stub)")
            return

        print("[Hardware] STUB - Hardware interface not yet implemented")
        print("[Hardware] To implement:")
        print("  1. Install device library (evdev, rtmidi, or RPi.GPIO)")
        print("  2. Implement device detection and connection")
        print("  3. Add event loop for button press detection")
        print("  4. Call controller.toggle() on button press")

        self._running = True

    def stop(self):
        """
        Stop hardware button listener (STUB).
        """
        if not self._running:
            return

        print("[Hardware] Stopped (stub)")
        self._running = False

    def is_running(self) -> bool:
        """
        Check if hardware listener is active (STUB).

        Returns:
            True if running, False otherwise
        """
        return self._running

    @staticmethod
    def detect_devices(device_type="usb"):
        """
        Detect available hardware devices (STUB).

        Args:
            device_type: Type of device to detect

        Returns:
            List of detected devices (empty in stub)
        """
        print(f"[Hardware] Device detection not implemented for: {device_type}")
        print("[Hardware] Possible implementations:")
        print("  USB: Use evdev.list_devices()")
        print("  MIDI: Use rtmidi.MidiIn().get_ports()")
        print("  GPIO: Check /sys/class/gpio/")
        return []
