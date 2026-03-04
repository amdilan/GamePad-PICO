# boot.py

import board
from bootcfg import bootcfg

bootcfg(
   pin = board.GP19, # the button to off the bootcfg
    storage=False,
    cdc=True
)