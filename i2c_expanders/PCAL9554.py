# SPDX-FileCopyrightText: 2023 Pat Satyshur
# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Carter Nelson
#
# SPDX-License-Identifier: MIT

# pylint: disable=too-many-public-methods

#TODO: mostly a copy/paste from the PCAL9555, make sure this stuff is still true here.
"""
`pcal9554`
====================================================

CircuitPython module for the PCAL9554 I2C I/O extenders.
The PCAL9554 is a 8 pin IO Expander. It is software compatible with the PCA9554, but has a
bunch of added functions.

Added features of these expanders include:
    *Built in pull up and pull down resistors.
    *Per pin selectable drive strength.
    *Maskable interrupt pins
    *Latching interrupt option
    *Per bank push-pull/open drain pin setup.

There are likely other devices that use this same command set and can be used with this class.
Where I find them, I will probably make a separate class name to make it obvious what devices are
supported. A list of other devices that should be compatible is below.

Compatible Devices
    *PCAL9554
    *PCAL9538
    *TODO

Heavily based on the code written by Tony DiCola for the MCP230xx library.

* Author(s): Pat Satyshur
"""

from micropython import const
from PCA9554 import PCA9554	#removed relative import, might need this again if this is a module??
from digitalio import DigitalInOut	#Do i need this??
#import digitalio

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/ilikecake/CircuitPython_I2C_Expanders.git"

# Internal helpers to simplify setting and getting a bit inside an integer.
#TODO: Can I include these from another file?
def _get_bit(val, bit):
    return val & (1 << bit) > 0


def _enable_bit(val, bit):
    return val | (1 << bit)


def _clear_bit(val, bit):
    return val & ~(1 << bit)

_PCAL9554_ADDRESS = const(0x27)		#TODO: this will probably change based on the device used. Not sure how to deal with this. Maybe remove the default and force the user to specify the address?

_PCAL9554_OUTPUT_DRIVE_1 = const(0x40)
_PCAL9554_OUTPUT_DRIVE_2 = const(0x41)
_PCAL9554_INPUT_LATCH = const(0x42)
_PCAL9554_PUPD_EN = const(0x43)
_PCAL9554_PUPD_SEL = const(0x44)
_PCAL9554_IRQ_MASK = const(0x45)
_PCAL9554_IRQ_STATUS = const(0x46)
_PCAL9554_OUTPUT_PORT_CONFIG = const(0x4F)

class PCAL9554(PCA9554):
    """Supports PCAL9554 instance on specified I2C bus and optionally
    at the specified I2C address.
    """

    def __init__(self, i2c, address=_PCAL9554_ADDRESS, reset=True):
        super().__init__(i2c, address, False)	#This initializes the PCA9554 compatible registers.
        self._capability = _enable_bit(0x00, i2c_expander.Capability.PULL_UP)    | \
                           _enable_bit(0x00, i2c_expander.Capability.PULL_DOWN)  | \
                           _enable_bit(0x00, i2c_expander.Capability.INVERT_POL) | \
                           _enable_bit(0x00, i2c_expander.Capability.DRIVE_MODE)    #TODO: This device does not really have a capability to set drive mode the way digitalio is expecting. I should probably not se this here.
        if reset:
            self.reset_to_defaults()

    @property
    def pupd_en(self):
        """reads the pull up/down status
        """
        return self._read_u8(_PCAL9554_PUPD_EN)

    @pupd_en.setter
    def pupd_en(self, val):
        self._write_u8(_PCAL9554_PUPD_EN, val)
        
    @property
    def pupd_sel(self):
        """reads the pull up/down status
        """
        return self._read_u8(_PCAL9554_PUPD_SEL)

    @pupd_sel.setter
    def pupd_sel(self, val):
        self._write_u8(_PCAL9554_PUPD_SEL, val)
    
    #Enable interrupt on a pin. Interrupts are triggered by any state change of the pin.
    def set_int_pin(self, pin):
        self._write_u8(_PCAL9554_IRQ_MASK, _clear_bit(self._read_u8(_PCAL9554_IRQ_MASK), pin))
        self.gpio()     #Read from the input port register to clear interrupts
    
    #Disable interrupts on a pin.
    def clear_int_pin(self, pin):
        self._write_u8(_PCAL9554_IRQ_MASK, _set_bit(self._read_u8(_PCAL9554_IRQ_MASK), pin))
        self.gpio()     #Read from the input port register to clear interrupts. Not sure if I need this here...
    
    @property
    def get_int_status(self):
        return self._read_u8(_PCAL9554_IRQ_STATUS)
        