# SPDX-FileCopyrightText: 2023 Pat Satyshur
# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Carter Nelson
#
# SPDX-License-Identifier: MIT

"""
`digital_inout`
====================================================

An implementation of the digitalio interface that works with the I2C expanders.

Heavily based on the version written by Tony DiCola for the MCP230xx library.

* Author(s): Pat Satyshur
"""

import digitalio
from i2c_expanders.helpers import Capability, _get_bit, _enable_bit, _clear_bit

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/ilikecake/CircuitPython_I2C_Expanders.git"


class DigitalInOut:
    """The interface is exactly the same as the digitalio.DigitalInOut
       class. However Some devices do not support pull up/down resistors
       or setting the pin to open drain.

    Exceptions will be thrown when attempting to set unsupported configurations.
    """

    def __init__(self, pin_number, ioexpander_class):
        """Specify the pin number of the expander and pass the class object.
        Pin numbers start a 0.
        """
        self._pin = pin_number
        self._ioexp = ioexpander_class

    # kwargs in switch functions below are _necessary_ for compatibility
    # with DigitalInout class (which allows specifying pull, etc. which
    # is unused by this class).  Do not remove them, instead turn off pylint
    # in this case.
    # pylint: disable=unused-argument
    def switch_to_output(self, value=False, **kwargs):
        """Switch the pin state to a digital output with the provided starting
        value (True/False for high or low, default is False/low).
        """
        self.direction = digitalio.Direction.OUTPUT
        self.value = value

    def switch_to_input(self, pull=None, invert_polarity=False, **kwargs):
        """Switch the pin state to a digital input with the provided starting
        pull up/down resistor state (optional, none by default) and input polarity.
        Attempting to set a pull up/down resistor here for an expander that does not
        support it will throw an error.
        """
        self.direction = digitalio.Direction.INPUT
        self.pull = pull
        self.invert_polarity = invert_polarity

    # pylint: enable=unused-argument

    @property
    def value(self):
        """The value of the pin, either True for high or False for
        low.  Note you must configure as an output or input appropriately
        before reading and writing this value.
        """
        return _get_bit(self._ioexp.gpio, self._pin)

    @value.setter
    def value(self, val):
        if val:
            self._ioexp.gpio = _enable_bit(self._ioexp.gpio, self._pin)
        else:
            self._ioexp.gpio = _clear_bit(self._ioexp.gpio, self._pin)

    @property
    def direction(self):
        """The direction of the pin, either True for an input or
        False for an output.
        """
        if _get_bit(self._ioexp.iodir, self._pin):
            return digitalio.Direction.INPUT
        return digitalio.Direction.OUTPUT

    @direction.setter
    def direction(self, val):
        if val == digitalio.Direction.INPUT:
            self._ioexp.iodir = _enable_bit(self._ioexp.iodir, self._pin)
        elif val == digitalio.Direction.OUTPUT:
            self._ioexp.iodir = _clear_bit(self._ioexp.iodir, self._pin)
        else:
            raise ValueError(
                "Expected 'digitalio.Direction.INPUT' or 'digitalio.Direction.OUTPUT'."
            )

    @property
    def pull(self):
        """Returns the setup of internal pull up/down resistors. If pull up/down resistors
        are not supported, this function will raise an error.
        """
        if (not _get_bit(self._ioexp.capability, Capability.PULL_DOWN)) and (
            not _get_bit(self._ioexp.capability, Capability.PULL_UP)
        ):
            raise ValueError("Pull up/down resistors are not supported.")

        return self._ioexp.get_pupd(self._pin)

    @pull.setter
    def pull(self, val):
        # User requests pull up, pull up resistors are not supported.
        if (val == digitalio.Pull.UP) and (
            not _get_bit(self._ioexp.capability, Capability.PULL_UP)
        ):
            raise ValueError("Pull-up resistors are not supported.")

        # User requests pull down, pull down resistors are not supported.
        if (val == digitalio.Pull.DOWN) and (
            not _get_bit(self._ioexp.capability, Capability.PULL_DOWN)
        ):
            raise ValueError("Pull-down resistors are not supported.")

        # User requests no pull up/down. Pull up/down is not supported. There is nothing to do
        # in this case, but we have to catch it here or it will cause an error when the function
        # tries to set non-exsistent registers for no pull up/down.
        if (
            (val is None)
            and (not _get_bit(self._ioexp.capability, Capability.PULL_DOWN))
            and (not _get_bit(self._ioexp.capability, Capability.PULL_UP))
        ):
            return

        self._ioexp.set_pupd(self._pin, val)

    # TODO: Check capability on these
    @property
    def invert_polarity(self):
        """The polarity of the pin, either True for an Inverted or False for an normal."""
        if not _get_bit(self._ioexp.capability, Capability.INVERT_POL):
            raise ValueError("Polarity inversion not supported.")

        if _get_bit(self._ioexp.ipol, self._pin):
            return True
        return False

    @invert_polarity.setter
    def invert_polarity(self, val):
        if not _get_bit(self._ioexp.capability, Capability.INVERT_POL):
            raise ValueError("Polarity inversion not supported.")
        if val:
            self._ioexp.ipol = _enable_bit(self._ioexp.ipol, self._pin)
        else:
            self._ioexp.ipol = _clear_bit(self._ioexp.ipol, self._pin)

    # TODO: Not implemented. The expanders I am using do not support this.
    @property
    def drive_mode(self):
        """Set the drive mode on expanders that support it. Will raise an error if setting
        drive mode is not supported.

        Not implemented, will raise an error if set/read.
        """
        raise NotImplementedError("Drive mode setting is not implemented.")

    @drive_mode.setter
    def drive_mode(self, val):
        raise NotImplementedError("Drive mode setting is not implemented.")
