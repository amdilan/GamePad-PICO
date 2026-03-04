# code.py

import board
import digitalio
import asyncio
from profile import Profile
from CircuitPy_Gamepad import CircuitPy_Gamepad

async def main():
    profile = Profile()
    CPGP = CircuitPy_Gamepad()

    profile.init_HOME(board.GP19)
    profile.init_LED(up = board.GP20, right = board.GP13, down = board.GP21, left = board.GP26)

    RPbtn_pins=(
        board.GP9, # A
        board.GP8, # B	
        board.GP7, # x
        board.GP4, # Y
        board.GP0, # RB
        board.GP11, # RT
        board.GP28, # Select 1
        board.GP1, # Option 1
        board.GP22, # LSB
        board.GP10, # RSB
        board.GP27, # Select 2
        board.GP6, # Option 2
        board.GP12, # RT 3
    )

    RPbtns = [digitalio.DigitalInOut(pin) for pin in RPbtn_pins]
    for RPbtn in RPbtns:
        RPbtn.direction = digitalio.Direction.INPUT
        RPbtn.pull = digitalio.Pull.UP

    pcf0 = profile.pcf_0()
    pcf1 = profile.pcf_1()
    pcf2 = profile.pcf_2()
    pcf3 = profile.pcf_3()
    pcf4 = profile.pcf_4()
    pcf5 = profile.pcf_5()
    pcf6 = profile.pcf_6()
    pcf7 = profile.pcf_7()

    # All buttons
    btns = [
        RPbtns[0], # B1     A
        RPbtns[1], # B2     B
        RPbtns[2], # B3     Y
        RPbtns[3], # B4     X
        pcf3, # B5          LB
        RPbtns[4], # B6     RB
        pcf5, # B7          RT  
        RPbtns[5], # B8     LT
        RPbtns[6], # B9     SELECT 1
        RPbtns[7], # B10    2OPTION 1
        RPbtns[8], # B11    LSB
        RPbtns[9], # B12    RSB
        pcf1, # B13         D-UP
        pcf6, # B14         D-DOWN
        pcf2, # B15         D-LEFT
        pcf0, # B16         D-RIGHT
        RPbtns[10], # B17   SELECT 2
        RPbtns[11], # B18   OPTION 2
        pcf4, # B19         R2
        RPbtns[12], # B20   R3
    ]

    # Hat buttons
    hat_btns = [
        pcf1, # B13 = UP
        pcf6, # B14 = Down
        pcf2, # B15 = Left
        pcf0, # B16 = Right
    ]

    # Trigger buttons
    tgr_btns = [
        pcf5, # B7
        RPbtns[5], # B8
    ]

    # GamePad w/ POV Hat & Z-axis
    ghz_btns = [
        RPbtns[0], # B1
        RPbtns[1], # B2
        RPbtns[2], # B3
        RPbtns[3], # B4
        pcf3, # B5
        RPbtns[4], # B6
        RPbtns[6], # B9
        RPbtns[7], # B10
        RPbtns[8], # B11
        RPbtns[9], # B12
        RPbtns[10], # B17
        RPbtns[11], # B18
        pcf4, # B19
        RPbtns[12], # B20
    ]

    wasd_btns = [
        RPbtns[0], # B1
        RPbtns[1], # B2
        RPbtns[2], # B3
        RPbtns[3], # B4
        pcf5, # B5
        RPbtns[4], # B6
        RPbtns[6], # B9
        RPbtns[7], # B10
        RPbtns[8], # B11
        RPbtns[9], # B12
        pcf1, # B13
        pcf6, # B14
        pcf2, # B15
        pcf0, # B16
        RPbtns[10], # B17
        RPbtns[11], # B18
        pcf4, # B19
        RPbtns[12], # B20
    ]

    profile.set_buttons(btns)
    profile.set_triggers(tgr_btns)
    profile.set_dpad(hat_btns)
    profile.set_buttons_ghz(ghz_btns)

    await CPGP.update(profile)
    
asyncio.run(main())

