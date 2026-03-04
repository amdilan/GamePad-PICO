# gamepad.py
"""
`Gamepad`
====================================================

* Modifier : Madushanka Dilan
"""

import struct
import time

from adafruit_hid import find_device


class Gamepad:
    """Emulate a generic gamepad controller with 16 buttons,
    numbered 1-16, and two joysticks, one controlling
    ``x` and ``y`` values, and the other controlling ``z`` and
    ``r_x`` (x rotation or ``Rx``) values.

    The joystick values could be interpreted
    differently by the receiving program: those are just the names used here.
    The joystick values are in the range 0 to 255."""

    def __init__(self, devices) -> None:
        """Create a Gamepad object that will send USB gamepad HID reports.

        Devices can be a list of devices that includes a gamepad device or a gamepad device
        itself. A device is any object that implements ``send_report()``, ``usage_page`` and
        ``usage``.
        """
        self._gamepad_device = find_device(devices, usage_page=0x1, usage=0x05)

        # Reuse this bytearray to send mouse reports.
        # Typically controllers start numbering buttons at 1 rather than 0.
        # report[0] joystick 0 x: 0 to 255
        # report[1] joystick 0 y: 0 to 255
        # report[2] joystick 1 x: 0 to 255
        # report[3] joystick 1 y: 0 to 255
        # report[4] joystick z: 0 to 255
        # report[5] joystick z: 0 to 255
        # report[6] POV Hat Switch
        # report[7] buttons 1-8 (LSB is button 1)
        # report[8] buttons 9-16
        # report[9] buttons 17-24
        _report_length = 10
        self._report = bytearray(_report_length)

        # Remember the last report as well, so we can avoid sending
        # duplicate reports.
        self._last_report = bytearray(_report_length)

        # Store settings separately before putting into report. Saves code
        # especially for buttons.
        self.axis_IDLE = 128
        self.axis_MIN = 0
        self.axis_MAX = 255
        self.hat_IDLE = 8
        self._joy_x = self.axis_IDLE
        self._joy_y = self.axis_IDLE
        self._joy_z = self.axis_IDLE
        self._joy_r_x = self.axis_IDLE
        self._joy_r_y = self.axis_IDLE
        self._joy_r_z = self.axis_IDLE
        self._hat = self.hat_IDLE
        self._buttons_state = [ 0, 0, 0]


        # Send an initial report to test if HID device is ready.
        # If not, wait a bit and try once more.
        try:
            self.reset_all()
        except OSError:
            time.sleep(1)
            self.reset_all()
            
    def _send(self, always=False) -> None:
        """Send a report with all the existing settings.
        If ``always`` is ``False`` (the default), send only if there have been changes.
        """
        #self._report[0] = 0x04  # Report ID
        struct.pack_into(
            "<BBBBBBBBBB",
            self._report,
            0,
            self._joy_x,
            self._joy_y,
            self._joy_z,
            self._joy_r_x,
            self._joy_r_y,
            self._joy_r_z,
            self._hat,
            self._buttons_state[0],
            self._buttons_state[1],
            self._buttons_state[2]
        )

        if always or self._last_report != self._report:
            self._gamepad_device.send_report(self._report)
            # Remember what we sent, without allocating new storage.
            self._last_report[:] = self._report

    def reset_all(self) -> None:
        """Release all buttons and set joysticks to zero."""
        self._buttons_state = [ 0, 0, 0 ]
        self._joy_x = self.axis_IDLE
        self._joy_y = self.axis_IDLE
        self._joy_z = self.axis_IDLE
        self._joy_r_x = self.axis_IDLE
        self._joy_r_y = self.axis_IDLE
        self._joy_r_z = self.axis_IDLE
        self._hat = self.hat_IDLE
        self._send(always=True)
        
    def update_joysticks(self, x=None, y=None, z=None, r_x=None, r_y=None, r_z=None) -> None:
        """Set and send the given joystick values.
        The joysticks will remain set with the given values until changed

        One joystick provides ``x`` and ``y`` values,
        and the other provides ``z`` and ``r_x`` (z rotation).
        Any values left as ``None`` will not be changed.

        All values must be in the range -127 to 127 inclusive.

        Examples::

            # Change x and y values only.
            gp.update_joysticks(x=100, y=-50)

            # Reset all joystick values to center position.
            gp.update_joysticks(0, 0, 0, 0)
        """
        if x is not None:
            self._joy_x = self._validate_joystick_value(x)
        if y is not None:
            self._joy_y = self._validate_joystick_value(y)
        if z is not None:
            self._joy_z = self._validate_joystick_value(z)
        if r_x is not None:
            self._joy_r_x = self._validate_joystick_value(r_x)
        if r_y is not None:
            self._joy_r_y = self._validate_joystick_value(r_y)
        if r_z is not None:
            self._joy_r_z = self._validate_joystick_value(r_z)
        self._send()
        
    def update_button(self, *button: Tuple[int, bool],):
        for b, value in button:
            if self._validate_button_number(b):
                _bank = b // 8
                _bit = b % 8
                if value:
                    self._buttons_state[_bank] |= 1 << _bit
                else:
                    self._buttons_state[_bank] &= ~(1 << _bit)
        self._send()
                    
    '''def press_buttons(self, *buttons) -> None:
        """Press and hold the given buttons."""
        for button in buttons:
            _bank = button // 8
            _bit = button % 8
            self._buttons_state[_bank] |= 1 << _bit
        self._send()

    def release_buttons(self, *buttons) -> None:
        """Release the given buttons."""
        for button in buttons:
            _bank = button // 8
            _bit = button % 8
            self._buttons_state[_bank] &= ~(1 << _bit)
        self._send()

    def release_all_buttons(self) -> None:
        """Release all the buttons."""

        self._buttons_state = [ 0, 0, 0]
        self._send()

    def click_buttons(self, *buttons) -> None:
        """Press and release the given buttons."""
        self.press_buttons(*buttons)
        self.release_buttons(*buttons)'''

    
    def update_hat(self, position=None) -> None:
        """Set and send the given POV HAT angle.
        The POV HAT will remain set with the given angle until changed.

        The angle should be one of the following values:
        * ``0`` = UP
        * ``1`` = UP + RIGHT
        * ``2`` = RIGHT
        * ``3`` = DOWN + RIGHT
        * ``4`` = DOWN
        * ``5`` = DOWN + LEFT
        * ``6`` = LEFT
        * ``7`` = UP + LEFT
        * ``8`` = IDLE

        Examples::

            # Set POV HAT to Up-Right.
            gp.update_hat(1)

            # Reset POV HAT to center position.
            gp.update_hat()
        """
        if position is None:
            self._hat = 8  # Center position
        else:
            self._hat = self._validate_hat_angle(position)
        self._send()
                    
    @staticmethod
    def _validate_button_number(button) -> int:
        if not 0 <= button <= 23:
            raise ValueError("Button number must in range 1 to 24")
        #return button
        return True
    
    @staticmethod
    def _validate_joystick_value(value) -> int:
        if not 0 <= value <= 255:
            raise ValueError("Joystick value must be in range 0 to 255")
        return value
    
    @staticmethod
    def _validate_hat_angle(position) -> int:
        valid_angles = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        if position not in valid_angles:
            raise ValueError("Invalid POV HAT position. Must be one of: 0, 1, 2, 3, 4, 5, 6, 7, 8.")
        return position