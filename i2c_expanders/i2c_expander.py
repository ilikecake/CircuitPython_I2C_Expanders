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

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/ilikecake/CircuitPython_I2C_Expanders.git"


# pylint: disable=too-few-public-methods
class I2c_Expander:
    """Base class for I2C GPIO expander devices. This class has basic read and write functions that
    are common to all i2c expanders. This class should never be used directly.
    """

    def __init__(self, bus_device, address):
        self._device = i2c_device.I2CDevice(bus_device, address)
        # Initialize capabiltiy and max pins to zero. These should be set in the upper level class.
        self._maxpins = 0
        self._capability = 0x00
        # This used to be a global to save memory. However, I don't think the tradeoff of saving 3
        # bytes per expander instance is worth the wierdness of using a global for this.
        self._buffer = bytearray(3)

    @property
    def maxpins(self):
        """Number of pins in the expander. Starts at 0. Read only from user code."""
        return self._maxpins

    @maxpins.setter
    def maxpins(self, val):
        # Read only
        pass

    @property
    def capability(self):
        """Indicates the device capability. Used by digital_inout when setting pull up/down
        resistors and stuff.

         * Bit 0: Pull up resistors.
         * Bit 1: Pull down resisors.
         * Bit 2: Invert polarity of inputs.
         * Bit 3: Set drive mode of pins.

        Note that this bit is only set if the part has capabilty on a per-pin basis. Some parts
        can only set banks of pins, so they do not advertise the capability here.

        Read only from user code.
        """
        return self._capability

    @capability.setter
    def capability(self, val):
        # Read only
        pass

    def _read_u16le(self, register):
        # Read an unsigned 16 bit little endian value from the specified 8-bit
        # register.
        with self._device as bus_device:
            self._buffer[0] = register & 0xFF

            bus_device.write_then_readinto(
                self._buffer, self._buffer, out_end=1, in_start=1, in_end=3
            )
            return (self._buffer[2] << 8) | self._buffer[1]

    def _write_u16le(self, register, val):
        # Write an unsigned 16 bit little endian value to the specified 8-bit
        # register.
        with self._device as bus_device:
            self._buffer[0] = register & 0xFF
            self._buffer[1] = val & 0xFF
            self._buffer[2] = (val >> 8) & 0xFF
            bus_device.write(self._buffer, end=3)

    def _read_u8(self, register):
        # Read an unsigned 8 bit value from the specified 8-bit register.
        with self._device as bus_device:
            self._buffer[0] = register & 0xFF

            bus_device.write_then_readinto(
                self._buffer, self._buffer, out_end=1, in_start=1, in_end=2
            )
            return self._buffer[1]

    def _write_u8(self, register, val):
        # Write an 8 bit value to the specified 8-bit register.
        with self._device as bus_device:
            self._buffer[0] = register & 0xFF
            self._buffer[1] = val & 0xFF
            bus_device.write(self._buffer, end=2)

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
