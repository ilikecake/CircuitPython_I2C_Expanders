# SPDX-FileCopyrightText: 2023 Pat Satyshur
# SPDX-FileCopyrightText: 2021 Red_M
#
# SPDX-License-Identifier: MIT

"""
`i2c_expander`
====================================================

The base class for the I2C expanders.
This class should not be included directly in user code. It provides base functions that are used by
all of the I2C expander drivers.

Based heavily on the code from Red_M for the MCP230xx library.

* Author(s): Pat Satyshur
"""

from adafruit_bus_device import i2c_device
from i2c_expanders.digital_inout import DigitalInOut

# from i2c_expanders.helpers import Capability

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/ilikecake/CircuitPython_I2C_Expanders.git"

# Global buffer for reading and writing registers with the devices.  This is
# shared between both the MCP23008 and MCP23017 class to reduce memory allocations.
# However this is explicitly not thread safe or re-entrant by design!
# TODO: DO I want this? Why is this not inside the class?
_BUFFER = bytearray(3)

# Figure out how to doccument the maxpins with this:
# how many pins does the IO expander have starts at 0
# and goes up to this value. An 8 pin expander would
# set maxpins to 7 (0-7).


# pylint: disable=too-few-public-methods
class I2c_Expander:
    """Base class for I2C GPIO expander devices."""

    def __init__(self, bus_device, address):
        self._device = i2c_device.I2CDevice(bus_device, address)
        self.maxpins = 0
        self.capability = 0x00  # Pull up, pull down, open drain, etc...

    def _read_u16le(self, register):
        # Read an unsigned 16 bit little endian value from the specified 8-bit
        # register.
        with self._device as bus_device:
            _BUFFER[0] = register & 0xFF

            bus_device.write_then_readinto(
                _BUFFER, _BUFFER, out_end=1, in_start=1, in_end=3
            )
            return (_BUFFER[2] << 8) | _BUFFER[1]

    def _write_u16le(self, register, val):
        # Write an unsigned 16 bit little endian value to the specified 8-bit
        # register.
        with self._device as bus_device:
            _BUFFER[0] = register & 0xFF
            _BUFFER[1] = val & 0xFF
            _BUFFER[2] = (val >> 8) & 0xFF
            bus_device.write(_BUFFER, end=3)

    def _read_u8(self, register):
        # Read an unsigned 8 bit value from the specified 8-bit register.
        with self._device as bus_device:
            _BUFFER[0] = register & 0xFF

            bus_device.write_then_readinto(
                _BUFFER, _BUFFER, out_end=1, in_start=1, in_end=2
            )
            return _BUFFER[1]

    def _write_u8(self, register, val):
        # Write an 8 bit value to the specified 8-bit register.
        with self._device as bus_device:
            _BUFFER[0] = register & 0xFF
            _BUFFER[1] = val & 0xFF
            bus_device.write(_BUFFER, end=2)

    def get_pin(self, pin):
        """Convenience function to create an instance of the DigitalInOut class
        pointing at the specified pin on the IO expander. This function should
        never be called directly from the I2c_expander class. It is included
        here so that all subclasses have this function by default.
        """
        self._validate_pin(pin)
        return DigitalInOut(pin, self)

    def _validate_pin(self, pin):
        """Internal helper function to make sure the pin that is passed to the function is valid.
        Will raise a value error if an invalid pin number is given.
        """
        if (pin > self.maxpins) or (pin < 0):
            raise ValueError(
                f"Invalid pin number {pin}. Pin should be 0-{self.maxpins}."
            )
