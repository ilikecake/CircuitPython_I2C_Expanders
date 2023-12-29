# SPDX-FileCopyrightText: 2023 Pat Satyshur
# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Carter Nelson
#
# SPDX-License-Identifier: MIT

# pylint: disable=too-many-public-methods


# TODO: mostly a copy/paste from the PCA9555, make sure this stuff is still true here.
"""
`PCA9554`
====================================================

CircuitPython module for the PCA9554 and compatible expanders.
The PCA9554 is a basic 8 pin I2C expander.

* Configurable pins as input or output
* Per pin polarity inversion. This inverts the value that is returned when an input port
  is read. Does not affect the pins set as outputs.
* Pin change interrupts. An interrupt is generated on any pin change for a pin configured
  as an input. The interrupt signal is cleared by a change back to the original value of
  the input pin or a read to the GPIO register.This will have to be detected and tracked in
  user code. There is no way to tell from the device what pin caused the interrupt.

Use this class if you are using a PCA9554 or compatible expander. This class is also used
as the base class for the PCAL9554 expander.

Required library files (.py or their .mpy equivalent):

* PCA9554.py
* i2c_expander.py
* digital_inout.py
* helpers.py

Compatible Devices

* PCA9554
* PCA9538

These are devices I have specifically tested and know work. There appear to be a lot more devices
with similar naming schemes that use the same register map. These should also be compatible, but
make sure you check the i2c address and default register state.

Heavily based on the code written by Tony DiCola for the MCP230xx library.

* Author(s): Pat Satyshur
"""

# TODO: Fix these imports.
from micropython import const
from i2c_expanders.i2c_expander import I2c_Expander
from i2c_expanders.helpers import _enable_bit, Capability

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/ilikecake/CircuitPython_I2C_Expanders.git"

# This is the default address for the PCA9554 with all addr pins grounded.
_PCA9554_DEFAULT_ADDRESS = const(0x20)

_PCA9554_INPUT = const(0x00)  # Input register
_PCA9554_OUTPUT = const(0x01)  # Output register
_PCA9554_IPOL = const(0x02)  # Polarity inversion register
_PCA9554_IODIR = const(0x03)  # Configuration (direction) register


class PCA9554(I2c_Expander):
    """The class for the PCA9554 expander. Instantiate one of these for each expander on the bus.
    Make sure you get the address right.
    """

    def __init__(self, i2c, address=_PCA9554_DEFAULT_ADDRESS, reset=True):
        super().__init__(i2c, address)
        self._maxpins = 7
        self._capability = _enable_bit(0x00, Capability.INVERT_POL)
        if reset:
            self.reset_to_defaults()

    def reset_to_defaults(self):
        """Reset all registers to their default state. This is also
        done with a power cycle, but it can be called by software here.

        :return:        Nothing.
        """
        # Input port register is read only.
        self.gpio = 0xFF
        self.ipol = 0x00
        self.iodir = 0xFF

    @property
    def gpio(self):
        """The raw GPIO port registers.  Each bit represents the value of the associated pin
        (0 = low, 1 = high). Read this register to get the value of all pins. Write to this
        register to set the value of any pins configured as outputs.
        Read and written as a 8 bit number.

        Register address (read):  0x00

        Register address (write): 0x01
        """
        return self._read_u8(_PCA9554_INPUT)

    @gpio.setter
    def gpio(self, val):
        self._write_u8(_PCA9554_OUTPUT, val)

    @property
    def ipol(self):
        """The raw 'polarity inversion' register. Each bit represents the polarity value of the
        associated pin (0 = normal, 1 = inverted). This only applies to pins configured as inputs.
        Read and written as a 8 bit number.

        Register address: 0x02
        """
        return self._read_u8(_PCA9554_IPOL)

    @ipol.setter
    def ipol(self, val):
        self._write_u8(_PCA9554_IPOL, val)

    @property
    def iodir(self):
        """The raw pin configuration register. Each bit represents direction of a pin, either 1
        for an input or 0 for an output. Read and written as a 8 bit number.

        Register address: 0x03
        """
        return self._read_u8(_PCA9554_IODIR)

    @iodir.setter
    def iodir(self, val):
        self._write_u8(_PCA9554_IODIR, val)
