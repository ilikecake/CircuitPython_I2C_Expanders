# SPDX-FileCopyrightText: 2023 Pat Satyshur
# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Carter Nelson
#
# SPDX-License-Identifier: MIT

# pylint: disable=too-many-public-methods

"""
`pca9555`
====================================================

CircuitPython module for the PCA9555 and compatible expanders.
The PCA9555 is a basic 16 pin I2C expander.
    *Configurable pins as input or output
    *Per pin polarity inversion. This inverts the value that is returned when an input port
     is read. Does not affect the pins set as outputs.
    *Pin change interrupts. An interrupt is generated on any pin change for a pin configured
     as an input. The interrupt signal is cleared by a change back to the original value of
     the input pin or a read to the GPIO register.This will have to be detected and tracked in
     user code. There is no way to tell from the device what pin caused the interrupt.

Use this class if you are using a PCA9555 or compatible expander. This class is also used
as the base class for the PCAL9555 expander.

There are likely other devices that use this same command set and can be used with this class.
Where I find them, I will probably make a separate class name to make it obvious what devices are
supported. A list of other devices that should be compatible is below.

Compatible Devices
    *PCA9555
    *TODO

Heavily based on the code written by Tony DiCola for the MCP230xx library.

* Author(s): Pat Satyshur
"""

# DriveMode: PUSH_PULL vs OPEN_DRAIN
# Pull: Pull.Up vs Pull.DOWN vs None
# TODO: Handle interrupts in here somewhere

from micropython import (
    const,
)  # TODO: What does const get me in this situation? Can I remove it?
from i2c_expanders.i2c_expander import I2c_Expander
from i2c_expanders.helpers import _enable_bit, Capability

# from i2c_expanders.digital_inout import _enable_bit

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/ilikecake/CircuitPython_I2C_Expanders.git"

# TODO: this will probably change based on the device used.
# Not sure how to deal with this. Maybe remove the default and
# force the user to specify the address?

_PCA9555_ADDRESS = const(0x20)
_PCA9555_INPUT0 = const(0x00)  # Input register 0
_PCA9555_INPUT1 = const(0x01)  # Input register 1
_PCA9555_OUTPUT0 = const(0x02)  # Output register 0
_PCA9555_OUTPUT1 = const(0x03)  # Output register 1
_PCA9555_IPOL0 = const(0x04)  # Polarity inversion register 0
_PCA9555_IPOL1 = const(0x05)  # Polarity inversion register 1
_PCA9555_IODIR0 = const(0x06)  # Configuration (direction) register 0
_PCA9555_IODIR1 = const(0x07)  # Configuration (direction) register 1


class PCA9555(I2c_Expander):
    """Supports PCA9555 instance on specified I2C bus and optionally
    at the specified I2C address.
    """

    def __init__(self, i2c, address=_PCA9555_ADDRESS, reset=True):
        super().__init__(i2c, address)
        self.maxpins = 15
        self.capability = _enable_bit(0x00, Capability.INVERT_POL)
        if reset:
            self.reset_to_defaults()

    @property
    def gpio(self):
        """The raw GPIO output register.  Each bit represents the
        output value of the associated pin (0 = low, 1 = high), assuming that
        pin has been configured as an output previously.
        """
        return self._read_u16le(_PCA9555_INPUT0)

    @gpio.setter
    def gpio(self, val):
        self._write_u16le(_PCA9555_OUTPUT0, val)

    @property
    def iodir(self):
        """The raw IODIR direction register.  Each bit represents
        direction of a pin, either 1 for an input or 0 for an output mode.
        """
        return self._read_u16le(_PCA9555_IODIR0)

    @iodir.setter
    def iodir(self, val):
        self._write_u16le(_PCA9555_IODIR0, val)

    def reset_to_defaults(self):
        """Reset all registers to their default state. This is also
        done with a power cycle, but it can be called by software here.

        :return:        Nothing.
        """
        # TODO: Should I make some sort of 'register' class to
        # handle memory addresses and default states?
        # Input port register is read only.
        self.gpio = 0xFFFF
        self.ipol = 0x0000
        self.iodir = 0xFFFF

    @property
    def ipol(self):
        """The raw IPOL output register.  Each bit represents the
        polarity value of the associated pin (0 = normal, 1 = inverted), assuming that
        pin has been configured as an input previously.
        """
        return self._read_u16le(_PCA9555_IPOL0)

    @ipol.setter
    def ipol(self, val):
        self._write_u16le(_PCA9555_IPOL0, val)
