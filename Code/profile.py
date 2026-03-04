# profile.py

import microcontroller
import board
import usb_hid
import analogio
import digitalio
import asyncio
import time
from time import sleep
import busio

#Libraries for communicating as a Keyboard device
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from gamepad import Gamepad
from led import led

# Import your corresponding ADDIN libraries
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15 import ads1x15
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_pcf8574 as PCF

class Profile:
    """
        * from profile import Profile.
        * profile = Profile().
        * profile.init_HOME(GPIO.PIN).
        * profile.init_LED(up = board.GP0, right = board.GP1, down = board.GP2, left = board.GP3).
    """
    
    def init_VAR(self):
        """The variables that should be assigned after initializing Profile"""
        print(" VAR Initializing...")
        self.HOME = None
        self.led = None
        self.dpad = []
        self.triggers = []
        self._buttons = []
        self.gamepad_buttons = []
        self.gamepad_buttons_hz = []
        self._deadband = 4  # You may adjust this value based on your desired deadband width
        self.pcf0 = None
        self.pcf1 = None
        self.pcf2 = None
        self.pcf3 = None
        self.pcf4 = None
        self.pcf5 = None
        self.pcf6 = None
        self.pcf7 = None
        self.Lx = None
        self.Ly = None
        self.Rx = None
        self.Ry = None
        
        # Axis Range Map Variables
        self.RM_in_min = 10
        self.RM_in_max = 26362
        self.RM_out_min = self.gp.axis_MIN
        self.RM_out_max = self.gp.axis_MAX
        self.Axis_Idle = self.gp.axis_IDLE
        
        # List of defind mode names
        self.mode_names = {
            1 : 'Gamepad w/ POV HAT',
            2 : 'Gamepad',
            3 : 'Desktop',
            4 : 'FPS_WASD',
            5 : 'FPS_Fusion',
        }
        
        # Desktop Profile keys
        self.desktop_buttons = {
            0 : Keycode.ENTER, 
            1 : Keycode.ESCAPE, 
            2 : Keycode.BACKSPACE, 
            3 : Keycode.SPACE,
            4 : Keycode.WINDOWS, 
            5 : Keycode.LEFT_ALT, 
            6 : None, 
            7 : None, 
            8 : None, 
            9 : None, 
            10 : None, 
            11 : None, 
            12 : Keycode.UP_ARROW, 
            13 : Keycode.DOWN_ARROW, 
            14 : Keycode.LEFT_ARROW, 
            15 : Keycode.RIGHT_ARROW,
            16 : Keycode.LEFT_CONTROL,
            17 : Keycode.LEFT_SHIFT,
            18 : None,
            19 : None
        }
        
        self.fps_wasd_buttons = {
            0 : Keycode.F, 
            1 : Keycode.V, 
            2 : Keycode.R, 
            3 : Keycode.T,
            4 : Keycode.Q, 
            5 : Keycode.E, 
            6 : None, 
            7 : None, 
            8 : Keycode.TAB,  
            9 : Keycode.ESCAPE,
            10 : Keycode.LEFT_SHIFT, 
            11 : Keycode.ENTER, 
            12 : Keycode.UP_ARROW,  
            13 : Keycode.DOWN_ARROW, 
            14 : Keycode.LEFT_ARROW, 
            15 : Keycode.RIGHT_ARROW,
            16 : Keycode.M, 
            17 : Keycode.N,
            18 : Keycode.SPACE, 
            19 : Keycode.LEFT_CONTROL,
        }
        
        # calculate raw input midpoint and scaled deadband range
        self._raw_midpoint = self.RM_in_min + ((self.RM_in_max - self.RM_in_min) // 2)
        self._db_range = self.RM_in_max - self.RM_in_min - (self._deadband * 2) + 1
        
        self._held_keys = set() # To keep track of currently held keys in desktop mode
        
        print(" VAR Initialized.")
    
    def __init__(self) -> None:
        print(" PROFILE Initializing...")
        # Creating Objects for necessary classes
        self.mouse = Mouse(usb_hid.devices)
        self.keyboard = Keyboard(usb_hid.devices)
        self.layout = KeyboardLayoutUS(self.keyboard)
        self.gp = Gamepad(usb_hid.devices)
        
        # Initializing I2C Buses
        self.i2c0 = busio.I2C(scl=board.GP17, sda=board.GP16, frequency=400000)
        self.i2c1 = busio.I2C(scl=board.GP3, sda=board.GP2, frequency=400000)
        self.ads = ADS.ADS1115(self.i2c1, address=0x48, data_rate=860)
        self.pcf = PCF.PCF8574(self.i2c0, address=0x20)
        
        # Default Proflie
        self.Mode = 1
        
        # The variable the should be assigned after initializing Profile
        self.init_VAR()
        
        # Initializing ADS and PCF
        self.init_ADS()
        self.init_PCF()
        
        print(" PROFILE Initialized.")
        
    async def _update(self):
        await self.Home_pressed()
        
    def init_ADS(self) -> None:
        print(" ADS Initializing...")
        self.Ry = AnalogIn(self.ads, ads1x15.Pin.A2)
        self.Rx = AnalogIn(self.ads, ads1x15.Pin.A3)
        self.Ly = AnalogIn(self.ads, ads1x15.Pin.A0)
        self.Lx = AnalogIn(self.ads, ads1x15.Pin.A1)
        print(" ADS Initialized.")
    
    def init_PCF(self) -> None:
        """ initialized PCF GPIO individually for easy assigning. """
        print(" PCF Initializing...")
        self.pcf0 = self.pcf.get_pin(0)
        self.pcf0.switch_to_input(pull=digitalio.Pull.UP)
        self.pcf1 = self.pcf.get_pin(1)
        self.pcf1.switch_to_input(pull=digitalio.Pull.UP)
        self.pcf2 = self.pcf.get_pin(2)
        self.pcf2.switch_to_input(pull=digitalio.Pull.UP)
        self.pcf3 = self.pcf.get_pin(3)
        self.pcf3.switch_to_input(pull=digitalio.Pull.UP)
        self.pcf4 = self.pcf.get_pin(4)
        self.pcf4.switch_to_input(pull=digitalio.Pull.UP)
        self.pcf5 = self.pcf.get_pin(5)
        self.pcf5.switch_to_input(pull=digitalio.Pull.UP)
        self.pcf6 = self.pcf.get_pin(6)
        self.pcf6.switch_to_input(pull=digitalio.Pull.UP)
        self.pcf7 = self.pcf.get_pin(7)
        self.pcf7.switch_to_input(pull=digitalio.Pull.UP)
        print(" PCF Initialized.")
        
    def pcf_0(self):
        return self.pcf0
    
    def pcf_1(self):
        return self.pcf1
    
    def pcf_2(self):
        return self.pcf2
    
    def pcf_3(self):
        return self.pcf3
        
    def pcf_4(self):
        return self.pcf4
    
    def pcf_5(self):
        return self.pcf5
    
    def pcf_6(self):
        return self.pcf6
    
    def pcf_7(self):
        return self.pcf7
    
    def apply_deadzone(self, value):
        """ This handles the deadzone of the analog joystick, and pass it to range_map(). """
        
        # # calculate raw input midpoint and scaled deadband range
        # _raw_midpoint = self.RM_in_min + ((self.RM_in_max - self.RM_in_min) // 2)
        # _db_range = self.RM_in_max - self.RM_in_min - (self._deadband * 2) + 1
        
        # Clamp raw input value to specified min/max
        new_value = min(max(value, self.RM_in_min), self.RM_in_max)

        # Account for deadband
        if new_value < (self._raw_midpoint - self._deadband):
            new_value -= self.RM_in_min
        elif new_value > (self._raw_midpoint + self._deadband):
            new_value = new_value - self.RM_in_min - (self._deadband * 2)
        else:
            new_value = self._db_range // 2

        # Calculate scaled joystick-compatible value and clamp to 0-255
        return self.range_map(new_value, self.RM_in_min, self._db_range, self.RM_out_min, self.RM_out_max)
    
    def init_LED(
        self,
        up: [microcontroller.Pin],
        right: [microcontroller.Pin],
        down: [microcontroller.Pin],
        left: [microcontroller.Pin]
        ) -> None:
        self.led = led(up, right, down, left)
        print("LED PINs SET.")
        
    def init_HOME(self, source: [microcontroller.Pin]) -> None:
        """ Initializes the pin that is connected to the HOME button. """
        print("HOME BUTTON initializing...")
        source_gpio = digitalio.DigitalInOut(source)
        source_gpio.direction = digitalio.Direction.INPUT
        source_gpio.pull = digitalio.Pull.UP
        self.HOME =  source_gpio
        print("HOME BUTTON initialized")
    
    def _hat(self, dpad_buttons) -> None:
        U = not dpad_buttons[0].value
        D = not dpad_buttons[1].value
        L = not dpad_buttons[2].value
        R = not dpad_buttons[3].value
        if U and R:
            self.gp.update_hat(1)
        elif U and L:
            self.gp.update_hat(7)
        elif U:
            self.gp.update_hat(0)
        elif D and R:
            self.gp.update_hat(3)
        elif D and L:
            self.gp.update_hat(5)
        elif D:
            self.gp.update_hat(4)
        elif L:
            self.gp.update_hat(6)
        elif R:
            self.gp.update_hat(2)
        else:
            self.gp.update_hat()
    
    @staticmethod
    def invert_axis(value):
        midpoint = 128
        #return midpoint - (value - midpoint)
        return min(max((midpoint - (value - midpoint)), 0), 255)
    
    @staticmethod
    def axis(value):
        midpoint = 128
        return min(max(value, 0),255)
        
    
    @staticmethod
    def range_map(_input, in_min, in_max, out_min, out_max):
        """ Adjusts the raw input to the specific Output Range. """
        return (_input - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
    
    @staticmethod
    def transform_range(value):
        return int((value - 128) * (127 / 128))
    
    def set_buttons(self, buttons) -> None:
        self._buttons = buttons
        self._buttons_cache = [True] * len(buttons)
        print("BUTTON PINs SET.")
        
    def set_dpad(self, dpad_buttons) -> None:
        self.dpad = dpad_buttons
        print("D-PAD PINs SET.")
            
    def set_triggers(self, trigger_btns) -> None:
        self.triggers = trigger_btns
        print("TRIGGER PINs SET.")
        
    def set_buttons_ghz(self, buttons_ghz) -> None:
        self.gamepad_buttons_hz = buttons_ghz
        print("Gamepad_HZ PINs SET.")
            
    def _analogJS(self, x=None, y=None, r_x=None, r_y=None):
        x_value =x.value
        y_value =y.value
        r_x_value = r_x.value
        r_y_value = r_y.value
        self.gp.update_joysticks(
                x=self.axis(self.apply_deadzone(x_value)),
                y=self.axis(self.apply_deadzone(y_value)),
                z=self.axis(self.apply_deadzone(r_x_value)),
                r_x=self.axis(self.apply_deadzone(r_y_value)),
            )
        
        
    def _analogJS_z(self, x=None, y=None, r_x=None, r_y=None, trigger_btns=None):
        x_value =x.value
        y_value =y.value
        r_x_value = r_x.value
        r_y_value = r_y.value
        self.gp.update_joysticks(
                x=self.axis(self.apply_deadzone(x_value)),
                y=self.axis(self.apply_deadzone(y_value)),
                z=self._trigger_axis(self.triggers),
                r_x=self.axis(self.apply_deadzone(r_x_value)),
                r_y=self.axis(self.apply_deadzone(r_y_value)),
            )
        
    def _analog_JS_fps(self, r_x=None, r_y=None):
        r_x_value = r_x.value
        r_y_value = r_y.value
        self.gp.update_joysticks(
                r_x=self.axis(self.apply_deadzone(r_x_value)),
                r_y=self.axis(self.apply_deadzone(r_y_value)),
            )
        
    def _trigger_axis(self, trigger_btns):
        buttons = trigger_btns
        axis_value = (self.RM_out_min, self.RM_out_max)
        if not buttons[0].value and not buttons[1].value:
            return self.Axis_Idle
        elif not buttons[0].value:
            return axis_value[0]
        elif not buttons[1].value:
            return axis_value[1]
        else:
            return self.Axis_Idle
    
            
    async def _mouseJS(self, x, y):
        MOVE_SPEED = 20     # Max speed of mouse movement
        THRESHOLD = 250
        x_val = x.value
        y_val = y.value
        x_move = 0
        y_move = 0

        if abs(x_val - self._raw_midpoint) > THRESHOLD:
            #x_move = self.range_map(x_val, self.RM_in_min, self.RM_in_max, -MOVE_SPEED, MOVE_SPEED)
            x_move = (x_val - self.RM_in_min) * (MOVE_SPEED - (- MOVE_SPEED)) // (self.RM_in_max - (-MOVE_SPEED)) + (- MOVE_SPEED)
        if abs(y_val - self._raw_midpoint) > THRESHOLD:
            #y_move = self.range_map(y_val, self.RM_in_min, self.RM_in_max, -MOVE_SPEED, MOVE_SPEED)
            y_move = (y_val - self.RM_in_min) * (MOVE_SPEED - (- MOVE_SPEED)) // (self.RM_in_max - (-MOVE_SPEED)) + (- MOVE_SPEED)

        if x_move != 0 or y_move != 0:
            self.mouse.move(x=x_move, y=y_move)
            
        # await asyncio.sleep(0.01)  # Small delay to control update rate

    async def _mouseJS_Accelerated(self, x, y):
        # --- Configuration ---
        MAX_SPEED = 40        # Max pixels per update at full tilt
        ACCEL_POWER = 2.2     # 1.0 is linear, 2.0 is heavy acceleration
        CURVE_THRESHOLD = 0.15 # Ignore tiny jitters
        
        # 1. Get current values (0-255 range from your apply_deadzone)
        x_val = self.apply_deadzone(x.value)
        y_val = self.apply_deadzone(y.value)

        # 2. Convert to -1.0 to 1.0 range (0.0 is center)
        # Center is 128, max deflection is 127
        nx = (x_val - 128) / 127
        ny = (y_val - 128) / 127

        # 3. Calculate acceleration
        def calculate_accel(normalized_val):
            mag = abs(normalized_val)
            if mag < CURVE_THRESHOLD:
                return 0
            # The magic: Raise the magnitude to the power of ACCEL_POWER
            accel_mag = pow(mag, ACCEL_POWER) * MAX_SPEED
            # Restore the direction (positive or negative)
            return int(accel_mag if normalized_val > 0 else -accel_mag)

        x_move = calculate_accel(nx)
        y_move = calculate_accel(ny)

        # 4. Move the mouse
        if x_move != 0 or y_move != 0:
            self.mouse.move(x=x_move, y=y_move)

        # 5. Yield to other tasks (Buttons, LEDs, etc)
        # 0.008s = ~125Hz update rate, feels very smooth
        await asyncio.sleep(0.008)

    async def _scrollJS(self, y) -> None:
        yJS = self.axis(self.apply_deadzone(y.value))
        # print(yJS)
                
        if yJS < 120:
            amount = 2 if yJS < 40 else 1
            self.mouse.move(wheel=amount)
        elif yJS > 135:
            amount = -2 if yJS > 210 else -1
            self.mouse.move(wheel=amount)
        await asyncio.sleep(0.02)
            
    def _wasdJS(self, x, y) -> None:
        xJS = self.axis(self.apply_deadzone(x.value))
        yJS = self.axis(self.apply_deadzone(y.value))
        
        check_map = [
            (Keycode.W, yJS <= 121),
            (Keycode.S, yJS >= 135),
            (Keycode.A, xJS <= 121),
            (Keycode.D, xJS >= 135),
        ]
        
        for key, is_triggered in check_map:
            if is_triggered:
                if key not in self._held_keys:
                    self.keyboard.press(key)
                    self._held_keys.add(key)
            else:
                if key in self._held_keys:
                    self.keyboard.release(key)
                    self._held_keys.remove(key)
            
    async def _mouseJS_FPS(self, x, y):
        x = x.value
        y = y.value
        xJS = self.axis(self.apply_deadzone(x))
        # print("x",xJS)
        yJS = self.axis(self.apply_deadzone(y))
        # print("y",yJS)
        if (121 >= yJS >= self.RM_out_min) and (135 <= xJS <= self.RM_out_max): # U R
            self.mouse.move(x=self.transform_range(xJS),y=self.transform_range(yJS))
        elif (121 >= yJS >= self.RM_out_min) and (121 >= xJS >= self.RM_out_min): # U L
            self.mouse.move(x=self.transform_range(xJS),y=self.transform_range(yJS))
        elif (121 >= yJS >= self.RM_out_min): # U
            self.mouse.move(y=self.transform_range(yJS))
        elif (135 <= yJS <= self.RM_out_max) and (135 <= xJS <= self.RM_out_max): # D R
            self.mouse.move(x=self.transform_range(xJS),y=self.transform_range(yJS))
        elif (135 <= yJS <= self.RM_out_max) and (121 >= xJS >= self.RM_out_min): # U L
            self.mouse.move(x=self.transform_range(xJS),y=self.transform_range(yJS))
        elif (135 <= yJS <= self.RM_out_max): # D
            self.mouse.move(y=self.transform_range(yJS))
        elif (121 >= xJS >= self.RM_out_min): # L
            self.mouse.move(x=self.transform_range(xJS))
        elif (135 <= xJS <= self.RM_out_max): # R
            self.mouse.move(x=self.transform_range(xJS))
        else:
            self.mouse._send_no_move()
    
    def _gamepad_buttons(self, buttons) -> None:
        changes = []
        for i,button in enumerate(buttons):
            current_state = button.value
            if current_state != self._buttons_cache[i]:
                self._buttons_cache[i] = current_state
                changes.append((i, not current_state))
                
        if changes:
            self.gp.update_button(*changes)
        
    def _gamepad_buttons_hz(self, buttons) -> None:
        changes = []
        for i,button in enumerate(buttons):
            current_state = button.value
            if current_state != self._buttons_cache[i]:
                self._buttons_cache[i] = current_state
                changes.append((i, not current_state))
        if changes:
            self.gp.update_button(*changes)
    
    def _desktop_buttons(self, buttons):
        # iterate through buttons
        for i, button in enumerate(buttons):
            current_state = button.value
            
            # CHECK: Only process if the state has changed
            if current_state != self._buttons_cache[i]:
                # Update the cache immediately
                self._buttons_cache[i] = current_state
                # --- LOGIC START ---
                
                # 1. Handle Standard Keys (mapped in self.desktop_buttons)
                key = self.desktop_buttons.get(i)
                if key is not None:
                    if not current_state: # Button Pressed
                        self.keyboard.press(key)
                    else:               # Button Released
                        self.keyboard.release(key)
                        
                # 2. Handle Special Keys (None mapped in self.desktop_buttons)
                else:
                    # Mouse Right Click (Left Trigger - Index 6)
                    if i == 6:
                        if not current_state:
                            self.mouse.press(Mouse.RIGHT_BUTTON)
                        else:
                            self.mouse.release(Mouse.RIGHT_BUTTON)

                    # Mouse Left Click (Right Trigger - Index 7)
                    elif i == 7:
                        if not current_state:
                            self.mouse.press(Mouse.LEFT_BUTTON)
                        else:
                            self.mouse.release(Mouse.LEFT_BUTTON)

                    # Mouse Middle Click (Right Stick Button - Index 11)
                    elif i == 11:
                        if not current_state:
                            self.mouse.press(Mouse.MIDDLE_BUTTON)
                        else:
                            self.mouse.release(Mouse.MIDDLE_BUTTON)
                            
                    # Macros: Copy, Paste, Undo, Redo
                    # We only trigger these on the PRESS (not on release)
                    elif not current_state: 
                        if i == 8:   # Select 1 -> Ctrl+C
                            self.keyboard.send(Keycode.CONTROL, Keycode.C)
                        elif i == 9: # Option 1 -> Ctrl+V
                            self.keyboard.send(Keycode.CONTROL, Keycode.V)
                        elif i == 18: # Select 2 -> Ctrl+Z
                            self.keyboard.send(Keycode.CONTROL, Keycode.Z)
                        elif i == 19: # Option 2 -> Ctrl+Y
                            self.keyboard.send(Keycode.CONTROL, Keycode.Y)
                
    def _fpswasd_buttons(self, buttons) -> None:
        for i, button in enumerate(buttons):
            current_state = button.value
            if current_state != self._buttons_cache[i]:
                self._buttons_cache[i] = current_state
                key = self.fps_wasd_buttons.get(i)
                if key is not None:
                    if not current_state: # Button Pressed
                        self.keyboard.press(key)
                    else:               # Button Released
                        self.keyboard.release(key)
                else:
                    if i == 6:
                        if not current_state:
                            self.mouse.press(Mouse.RIGHT_BUTTON)
                        else:
                            self.mouse.release(Mouse.RIGHT_BUTTON)
                    elif i == 7:
                        if not current_state:
                            self.mouse.press(Mouse.LEFT_BUTTON)
                        else:
                            self.mouse.release(Mouse.LEFT_BUTTON)
            
    async def _profile_1(self) -> None: # Profile: 'Gamepad w/ POV HAT'
        # print("Profile 1")
        self.led.array('1000')
        self._gamepad_buttons_hz(self.gamepad_buttons_hz)
        self._hat(self.dpad)
        self._analogJS_z(x=self.Lx, y=self.Ly, r_x=self.Rx, r_y=self.Ry)
        
    async def _profile_2(self) -> None: # Profile: 'Gamepad'
        # print("Profile 2")
        self.led.array('0100')
        self._gamepad_buttons(self._buttons)
        self._analogJS(x=self.Lx, y=self.Ly, r_x=self.Rx, r_y=self.Ry)
        
    async def _profile_3(self) -> None: # Profile: 'Desktop'
        # print("Profile 3")
        self.led.array('0010')
        self._desktop_buttons(self._buttons)
        #await self.mouseJS(x=self.Lx, y=self.Ly)
        await self._mouseJS_Accelerated(x=self.Lx, y=self.Ly)
        await self._scrollJS(y=self.Ry)
        
    async def _profile_4(self) -> None:
        # print("Profile 4")
        self.led.array('0001')
        self._fpswasd_buttons(self._buttons)
        await self._mouseJS_Accelerated(x=self.Rx, y=self.Ry)
        self._wasdJS(x=self.Lx, y=self.Ly)
        
    async def _profile_5(self) -> None:
        # print("Profile 5")
        self.led.array('0111')
        self._analog_JS_fps(r_x=self.Rx, r_y=self.Ry,)
        self._wasdJS(x=self.Lx, y=self.Ly)
        self._fpswasd_buttons(self._buttons)
               
    async def _wait_double_press(self, pin):
        """Return True if double pressed"""
        DOUBLE_PRESS_TIME = 0.275  # seconds
        await asyncio.sleep(DOUBLE_PRESS_TIME)
        return not pin.value
    
        
    async def Home_pressed(self) -> None:
            
        DEBOUNCE = 0.02
                
        if not self.HOME.value:
            old_mode = self.Mode
            if not self.pcf1.value:
                await asyncio.sleep(DEBOUNCE)
                if await self._wait_double_press(self.pcf1):
                    self.Mode = 5
                else:
                    self.Mode = 1
                await asyncio.sleep(DEBOUNCE)

            elif not self.pcf0.value:
                await asyncio.sleep(DEBOUNCE)
                if await self._wait_double_press(self.pcf0):
                    #self.Mode = 6
                    pass
                else:
                    self.Mode = 2
                await asyncio.sleep(DEBOUNCE)

            elif not self.pcf6.value:
                await asyncio.sleep(DEBOUNCE)
                if await self._wait_double_press(self.pcf6):
                    # self.Mode = 7
                    pass
                else:
                    self.Mode = 3
                await asyncio.sleep(DEBOUNCE)

            elif not self.pcf2.value:
                await asyncio.sleep(DEBOUNCE)
                if await self._wait_double_press(self.pcf2):
                    # self.Mode = 8
                    pass
                else:
                    self.Mode = 4
                await asyncio.sleep(DEBOUNCE)
                
            if self.Mode != old_mode:
                self.clear_all_hid()
                await asyncio.sleep(0.01)

        await self._set_profile(self.Mode)
                    
    def clear_all_hid(self) -> None:
        """ Releases all pressed keys/buttons/hats """
        self.keyboard.release_all()
        self.mouse.release_all()
        self.gp.reset_all()
        
    async def _set_profile(self, mode: int) -> None:
        if self.Mode == 1: await self._profile_1()
        elif self.Mode == 2: await self._profile_2()
        elif self.Mode == 3: await self._profile_3()            
        elif self.Mode == 4: await self._profile_4()            
        elif self.Mode == 5: await self._profile_5()
