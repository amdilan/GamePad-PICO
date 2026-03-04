# led.py

import microcontroller
import board
import digitalio
import time

class led:
    """
        initialize by for example:
            led=led(up = board.GP0, right = board.GP1, down = board.GP2, left = board.GP3)
    """
    def __init__(
        self,
        up: [microcontroller.Pin],
        right: [microcontroller.Pin],
        down: [microcontroller.Pin],
        left: [microcontroller.Pin]
    ) -> None:
        print(" LED Initializing...")
        self.led_up = digitalio.DigitalInOut(up)
        self.led_up.direction = digitalio.Direction.OUTPUT
        self.led_right = digitalio.DigitalInOut(right)
        self.led_right.direction = digitalio.Direction.OUTPUT
        self.led_down = digitalio.DigitalInOut(down)
        self.led_down.direction = digitalio.Direction.OUTPUT
        self.led_left = digitalio.DigitalInOut(left)
        self.led_left.direction = digitalio.Direction.OUTPUT
        self.led_list = [self.led_up,self.led_right,self.led_down,self.led_left]
        self.led_value = []
        led.blink(self)
        print(" LED Initialized.")
        
    def blink(self) -> None:
        for i,led in enumerate(self.led_list):
            self.led_list[i].value = True
        time.sleep(0.5)
        for i,led in enumerate(self.led_list):
            self.led_list[i].value = False
        time.sleep(0.5)
        for i,led in enumerate(self.led_list):
            self.led_list[i].value = True
        time.sleep(0.5)
        
    def array(self, arr) -> None:
        if arr == "1000":
            self.led_list[0].value = True
            self.led_list[1].value = False
            self.led_list[2].value = False
            self.led_list[3].value = False
            # print(" LED Changed 1000.")
        if arr == "0100":
            self.led_list[0].value = False
            self.led_list[1].value = True
            self.led_list[2].value = False
            self.led_list[3].value = False
            # print(" LED Changed 0100.")
        if arr == "0010":
            self.led_list[0].value = False
            self.led_list[1].value = False
            self.led_list[2].value = True
            self.led_list[3].value = False
            # print(" LED Changed 0010.")
        if arr == "0001":
            self.led_list[0].value = False
            self.led_list[1].value = False
            self.led_list[2].value = False
            self.led_list[3].value = True
            # print(" LED Changed 0001.")
        if arr == "0111":
            self.led_list[0].value = False
            self.led_list[1].value = True
            self.led_list[2].value = True
            self.led_list[3].value = True
            # print(" LED Changed 0111.")
        if arr == "1011":
            self.led_list[0].value = True
            self.led_list[1].value = False
            self.led_list[2].value = True
            self.led_list[3].value = True
            # print(" LED Changed 1011.")
        if arr == "1101":
            self.led_list[0].value = True
            self.led_list[1].value = True
            self.led_list[2].value = False
            self.led_list[3].value = True
            # print(" LED Changed 1101.")
        if arr == "1110":
            self.led_list[0].value = True
            self.led_list[1].value = True
            self.led_list[2].value = True
            self.led_list[3].value = False
            # print(" LED Changed 1110.")
        if arr == "0000":
            self.led_list[0].value = False
            self.led_list[1].value = False
            self.led_list[2].value = False
            self.led_list[3].value = False
            # print(" LED Changed 0000.")
            
    def home(self, source: [microcontroller.Pin], changed: [bool]):
        self.led_value = self.led_list
        if not source.value:
            for i,led in enumerate(self.led_list):
                self.led_list[i].value = True
        if not changed:
            for i,led in enumerate(self.led_list):
                self.led_list[i] = self.led_value[i]
            