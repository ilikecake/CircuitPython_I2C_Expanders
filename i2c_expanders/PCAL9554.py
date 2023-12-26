# SPDX-FileCopyrightText: 2023 Pat Satyshur
# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Carter Nelson
#
# SPDX-License-Identifier: MIT

# pylint: disable=too-many-public-methods, duplicate-code
# Note: there is a bit of duplicated code between this and the PCAL9555. This code is duplicated
#       for these two expanders, but may not be if other expanders are added to this library. I
#       therefore  want to keep is separate in these two classes. The line above disables the
#       pylint check for this.

"""
`PCAL9554`
====================================================

CircuitPython module for the PCAL9554 I2C I/O extenders.
The PCAL9554 is a 8 pin IO Expander. It is software compatible with the PCA9554, but has a
bunch of added functions.

Added features of these expanders include:

* Built in pull up and pull down resistors.
* Per pin selectable drive strength.
* Maskable interrupt pins
* Latching interrupt option
* Per bank push-pull/open drain pin setup.

There are likely other devices that use this same command set and can be used with this class.
Where I find them, I will probably make a separate class name to make it obvious what devices are
supported. A list of other devices that should be compatible is below.

Compatible Devices

* PCAL9554
* PCAL9538
* TODO

Heavily based on the code written by Tony DiCola for the MCP230xx library.

* Author(s): Pat Satyshur
"""

# TODO: Disable unused imports here. After I finish this code, turn that off and see if they
# are still unused.
# pylint: disable=unused-import
from micropython import const
import digitalio  # import DigitalInOut	#TODO: Do i need this??

from i2c_expanders.PCA9554 import PCA9554
from i2c_expanders.helpers import (
    Capability,
    _get_bit,
    _enable_bit,
    _clear_bit,
)

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/ilikecake/CircuitPython_I2C_Expanders.git"

# TODO: Probably don't want this here.
_PCAL9554_ADDRESS = const(0x27)

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
        super().__init__(
            i2c, address, False
        )  # This initializes the PCA9554 compatible registers.
        self.capability = (
            _enable_bit(0x00, Capability.PULL_UP)
            | _enable_bit(0x00, Capability.PULL_DOWN)
            | _enable_bit(0x00, Capability.INVERT_POL)
        )  # TODO: This device does not really have a capability to set drive mode the way
        # digitalio is expecting. I should probably not set this here.
        if reset:
            self.reset_to_defaults()

    def set_int_pin(self, pin, latch=False):
        """Enable interrupt on a pin. Interrupts are generally triggered by any state change
        of the pin. There is an exception to this, see info below on latching for details.

        :param pin:     Pin number to modify.
        :param latch:   Set to True to enable latching on this interrupt. Defaults to False.
        :return:        Nothing.
        """
        # Validate inputs
        self._validate_pin(pin)
        if not isinstance(latch, (bool)):
            raise ValueError("latch must be True or False")

        self.irq_mask = _clear_bit(self.irq_mask, pin)

        if latch:
            self.input_latch = _enable_bit(self.input_latch, pin)
        else:
            self.input_latch = _clear_bit(self.input_latch, pin)

    def clear_int_pin(self, pin):
        """Disable interrupts on a pin.

        :param pin:     Pin number to modify.
        :return:        Nothing.
        """
        self._validate_pin(pin)
        self.irq_mask = _enable_bit(self.irq_mask, pin)

    def get_int_pins(self):
        """Returns a list of pins causing an interrupt. It is possible for multiple pins
        to be causing an interrupt. Calling this function will not clear the interrupt state.

        :return:        Returns a list of pin numbers.
        """
        output = []
        reg = self.irq_status
        for i in range(self.maxpins):
            if ((reg >> i) & 1) == 1:
                output.append(i)
        return output

    def set_int_latch(self, pin):
        """Set the interrupt on 'pin' to latching operation. Note this does not enable
        or disable the interrupt or clear the interrupt state.

        :param pin:     Pin number to modify.
        :return:        Nothing.
        """
        self._validate_pin(pin)
        self.input_latch = _enable_bit(self.input_latch, pin)

    def clear_int_latch(self, pin):
        """Set the interrupt on 'pin' to non-latching operation. Note this does not enable
        or disable the interrupt. This does not clear the interrupt state.

        :param pin:     Pin number to modify.
        :return:        Nothing.
        """
        self._validate_pin(pin)
        self.input_latch = _clear_bit(self.input_latch, pin)

    """Interrupt latch behavior
        By default (non-latched) if an interrupt enabled pin changes state, but changes back before the GPIO state register is read, the interrupt state
        will be cleared. Setting the interrupt latch will cause the device to latch on a state change of the input pin. With latching enabled, on a state
        change to the pin, the interrupt pin will be asserted and will not deassert until the input register is read. The value read from the input register
        will be the value that caused the interrupt, not nessecarially the current value of the pin. If the pin changed state, but changed back before the
        input register was read, the changed state will be what is returned in the register. The state change back to the original state will not trigger
        another interrupt as long as it happens before the input register is read. If the input register is read before the pin state changes back to the
        original value, both state changes will cause an interrupt.
    """

    def get_pupd(self, pin):
        """Checks the state of a pin to see if pull up/down is enabled.

        :param pin:     Pin number to check.
        :return:        Returns 'digitalio.Pull.UP', 'digitalio.Pull.DOWN' or 'None'
                        to indicate the state of the pin.
        """
        self._validate_pin(pin)
        # The else statements here are extaneous, but without them, it is harder to tell
        # what the code is doing. Disable pylint for that error here only.
        if _get_bit(self.pupd_en, pin):
            if _get_bit(self.pupd_sel, pin):  # pylint: disable=no-else-return
                return digitalio.Pull.UP
            else:
                return digitalio.Pull.DOWN
        else:
            return None

    def set_pupd(self, pin, status):
        """Sets the state of the pull up/down resistors on a pin.

        :param pin:     Pin number to modify.
        :param status:  The new state of the pull up/down resistors. Should be one of
                        'digitalio.Pull.UP', 'digitalio.Pull.DOWN' or 'None'.
        :return:        Nothing.
        """
        self._validate_pin(pin)

        if status is None:
            self.pupd_en = _clear_bit(self.pupd_en, pin)
            return

        self.pupd_en = _enable_bit(self.pupd_en, pin)

        if status == digitalio.Pull.UP:
            self.pupd_sel = _enable_bit(self.pupd_sel, pin)
        elif status == digitalio.Pull.DOWN:
            self.pupd_sel = _clear_bit(self.pupd_sel, pin)
        else:
            raise ValueError("Expected UP, DOWN, or None for pull state.")

    def set_output_drive(self, pin, drive):
        """Sets the output drive strength of a pin.

        :param pin:     Pin number to modify.
        :param drive:   The drive strength value to set. See the class 'Drive_strength'
                        for valid values to set.
        :return:        Nothing.
        """
        self._validate_pin(pin)
        # Check inputs to make sure they are valid
        if (drive > 3) or (drive < 0):
            raise ValueError("Invalid drive strength value.")

        loc = pin * 2  # Bit location in the register
        val = drive << loc  # Value to set shifted to the proper location
        mask = ~(3 << loc) & 0xFFFF  # Mask to clear the two bits we need to set.

        self.out_drive = ((self.out_drive) & (mask)) | val

    def get_output_drive(self, pin):
        """Reads the drive strength value of the given pin.

        :param pin:     Pin number to check.
        :return:        The current drive strength. Return values are shown in the
                        'Drive_strength' class
        """
        self._validate_pin(pin)

        val = self.out_drive
        loc = pin * 2  # Bit location in the register
        return (val >> loc) & 0x03

    def set_drive_mode(self, mode):
        """Configures the output drive of the entire output bank. Sets the outputs to either
        open drain or push-pull. Note that this is not a per-pin setting. All pins are set to the
        same mode.

        :param mode:    The mode to set. Should be one of either 'digitalio.DriveMode.PUSH_PULL'
                        or 'digitalio.DriveMode.OPEN_DRAIN'.

        :return:        Nothing.
        """

        if mode == digitalio.DriveMode.PUSH_PULL:
            self.out_port_config = _clear_bit(self.out_port_config, 0)
        elif mode == digitalio.DriveMode.OPEN_DRAIN:
            self.out_port_config = _enable_bit(self.out_port_config, 0)
        else:
            raise ValueError(
                "Invalid drive mode. It should be either 'digitalio.DriveMode.PUSH_PULL' "
                "or 'digitalio.DriveMode.OPEN_DRAIN'."
            )

    def get_drive_mode(self):
        """Returns the drive mode of the output bank. This is the drive mode of all pins.

        :return:        The drive mode. Either 'digitalio.DriveMode.PUSH_PULL'
                        or 'digitalio.DriveMode.OPEN_DRAIN'.
        """
        if _get_bit(self.out_port_config, 0) == 0x01:
            return digitalio.DriveMode.OPEN_DRAIN
        return digitalio.DriveMode.PUSH_PULL

    def reset_to_defaults(self):
        """Reset all registers to their default state. This is also
        done with a power cycle, but it can be called by software here.

        :return:        Nothing.
        """
        # TODO: Should I make some sort of 'register' class to handle
        #  memory addresses and default states?
        # Input port and interrupt status registers are read only.
        self.gpio = 0xFF
        self.ipol = 0x00
        self.iodir = 0xFF

        self.out_drive = 0xFFFF
        self.input_latch = 0x00
        self.pupd_en = 0x00  # TODO: 0xFF for PCAL9554, 0x00 for PCAL9538
        self.pupd_sel = 0xFF
        self.irq_mask = 0xFF
        self.out_port_config = 0x00

    """ Low level register access. These functions directly set or read the values of the
        registers on the device. In general, you should not need to call these
        functions directly.
    """

    @property
    def out_drive(self):
        """Output drive strength of pins 0-7."""
        return self._read_u16le(_PCAL9554_OUTPUT_DRIVE_1)

    @out_drive.setter
    def out_drive(self, val):
        self._write_u16le(_PCAL9554_OUTPUT_DRIVE_1, val)

    @property
    def input_latch(self):
        """Sets latching or non-latching interrupts per pin."""
        return self._read_u8(_PCAL9554_INPUT_LATCH)

    @input_latch.setter
    def input_latch(self, val):
        self._write_u8(_PCAL9554_INPUT_LATCH, val)

    @property
    def pupd_en(self):
        """reads the pull up/down status"""
        return self._read_u8(_PCAL9554_PUPD_EN)

    @pupd_en.setter
    def pupd_en(self, val):
        self._write_u8(_PCAL9554_PUPD_EN, val)

    @property
    def pupd_sel(self):
        """reads the pull up/down status"""
        return self._read_u8(_PCAL9554_PUPD_SEL)

    @pupd_sel.setter
    def pupd_sel(self, val):
        self._write_u8(_PCAL9554_PUPD_SEL, val)

    @property
    def irq_mask(self):
        """Masks or unmasks pins for generating interrupts."""
        return self._read_u8(_PCAL9554_IRQ_MASK)

    @irq_mask.setter
    def irq_mask(self, val):
        self._write_u8(_PCAL9554_IRQ_MASK, val)

    @property
    def irq_status(self):
        """Indicates which pin caused an interrupt."""
        return self._read_u8(_PCAL9554_IRQ_STATUS)

    @irq_status.setter
    def irq_status(self, val):
        # Regsiter is read only
        pass

    @property
    def out_port_config(self):
        """Sets output banks to open drain or push-pull operation."""
        return self._read_u8(_PCAL9554_OUTPUT_PORT_CONFIG)

    @out_port_config.setter
    def out_port_config(self, val):
        self._write_u8(_PCAL9554_OUTPUT_PORT_CONFIG, val)
