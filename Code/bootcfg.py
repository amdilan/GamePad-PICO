# bootcfg.py

try:
    from typing import Optional
except ImportError:
    pass

import microcontroller
import board, digitalio
import usb_hid
import usb_midi
import usb_cdc
import supervisor
from hid import hid_gamepad



def bootcfg(
    pin: [microcontroller.Pin],
    storage: Optional[bool] = True,
    cdc: Optional[bool] = True,
    **kwargs,
):
    if len(kwargs):
        print('unknown option', kwargs)
        
    # Default disable MIDI
    usb_midi.disable()
    
    # If not pressed, the key will be at +V (due to the pull-up).
    sbtn = digitalio.DigitalInOut(pin)
    sbtn.pull = digitalio.Pull.UP

    # Disable storage only if button is not pressed.
    if not storage:
        if sbtn.value:
            import storage
            storage.disable_usb_drive()
       
    # Entries for cdc (REPL) and storage are intentionally evaluated last to
    # ensure the board is debuggable, mountable and rescueable, in case any of
    # the previous code throws an exception.
    if not cdc:
        import usb_cdc
        usb_cdc.disable()
       
    # supervisor usb identification changing
    manufacturer = "Adafruit Industries LLC"
    product = "CircuitPy Pico Gamepad"
    supervisor.set_usb_identification(manufacturer,product,)
    
    # Enabling HID Devices
    # !NOTE : DO NOT CHANGE THE ORDER
    usb_hid.enable(
        (usb_hid.Device.KEYBOARD,
         usb_hid.Device.MOUSE,
         hid_gamepad(),)
    )