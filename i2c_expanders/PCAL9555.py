# SPDX-FileCopyrightText: 2023 Pat Satyshur
# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Carter Nelson
#
# SPDX-License-Identifier: MIT

# pylint: disable=too-many-public-methods, duplicate-code

# Note: there is a bit of duplicated code between this and the PCAL9554. This code is duplicated
#       for these two expanders, but may not be if other expanders are added to this library. I
#       therefore  want to keep is separate in these two classes. The line above disables the
#       pylint check for this.


"""
`PCAL9555`
====================================================

CircuitPython module for the PCAL9555 I2C I/O extenders.
The PCAL9555 is a 16 pin IO Expander. It is software compatible with the PCA9555, but has a
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
* PCAL9555
* TODO

Heavily based on the code written by Tony DiCola for the MCP230xx library.

* Author(s): Pat Satyshur
"""

from micropython import const
import digitalio  # import DigitalInOut	#TODO: Do i need this??

from i2c_expanders.PCA9555 import (
    PCA9555,
)  # removed relative import, might need this again if this is a module??

# from i2c_expanders.i2c_expander import Capability
from i2c_expanders.helpers import Capability, _get_bit, _enable_bit, _clear_bit

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/ilikecake/CircuitPython_I2C_Expanders.git"

# TODO: this will probably change based on the device used. Not sure how to deal with this.
# Maybe remove the default and force the user to specify the address?
_PCAL9555_ADDRESS = const(0x27)

# Registers specific to the PCAL9555 devices. This device also inherits the registers
# from the PCA9555
_PCAL9555_OUTPUT_DRIVE_0_0 = const(0x40)
_PCAL9555_OUTPUT_DRIVE_0_1 = const(0x41)
_PCAL9555_OUTPUT_DRIVE_1_0 = const(0x42)
_PCAL9555_OUTPUT_DRIVE_1_1 = const(0x43)
_PCAL9555_INPUT_LATCH_0 = const(0x44)
_PCAL9555_INPUT_LATCH_1 = const(0x45)
_PCAL9555_PUPD_EN_0 = const(0x46)
_PCAL9555_PUPD_EN_1 = const(0x47)
_PCAL9555_PUPD_SEL_0 = const(0x48)
_PCAL9555_PUPD_SEL_1 = const(0x49)
_PCAL9555_IRQ_MASK_0 = const(0x4A)
_PCAL9555_IRQ_MASK_1 = const(0x4B)
_PCAL9555_IRQ_STATUS_0 = const(0x4C)
_PCAL9555_IRQ_STATUS_1 = const(0x4D)
_PCAL9555_OUTPUT_PORT_CONFIG = const(0x4F)


# TODO: is this a good way to use these variables?
class DriveStrength:  # pylint: disable=too-few-public-methods
    """IO Pins have a selectable drive strength. For the PCAL9555, the full drive strength is
    10mA source, 25mA sink. The drive strength can be decreased by setting the drive strength
    registers.

    Note: I have tested these functions to show that the software sets the correct bits to the
    correct values, but I have not tested the affect on the rise/fall time of the pins.
    """

    DS1_4 = 0x00  # Drive strength 1/4
    DS1_2 = 0x01  # Drive strength 1/2
    DS3_4 = 0x02  # Drive strength 3/4
    DS1 = 0x03  # Drive strength full


Drive_Strength = DriveStrength()


class PCAL9555(PCA9555):
    """PACL9555 is a compatible with all PCA9555 functions and definitions. All functions
    from the PCA9555 work without updates. The PCAL device added capability is defined below.
    """

    def __init__(self, i2c, address=_PCAL9555_ADDRESS, reset=True):
        super().__init__(
            i2c, address, False
        )  # This initializes the PCA9555 compatible registers.
        # TODO: This device does not really have a capability to set drive mode the way
        #  digitalio is expecting. I should probably not set this here.
        self.capability = (
            _enable_bit(0x00, Capability.PULL_UP)
            | _enable_bit(0x00, Capability.PULL_DOWN)
            | _enable_bit(0x00, Capability.INVERT_POL)
            | _enable_bit(0x00, Capability.DRIVE_MODE)
        )
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

        # There are two sets of drive strength registers so we need to determine
        # if the pin is in bank 1 or 2
        port = 0
        if pin > 7:
            port = 1
            pin = pin - 8

        loc = pin * 2  # Bit location in the register
        val = drive << loc  # Value to set shifted to the proper location
        mask = ~(3 << loc) & 0xFFFF  # Mask to clear the two bits we need to set.

        if port == 0:
            self.out0_drive = ((self.out0_drive) & (mask)) | val
        elif port == 1:
            self.out1_drive = ((self.out1_drive) & (mask)) | val

    def get_output_drive(self, pin):
        """Reads the drive strength value of the given pin.

        :param pin:     Pin number to check.
        :return:        The current drive strength. Return values are shown in the
                        'Drive_strength' class
        """
        self._validate_pin(pin)

        # There are two sets of drive strength registers so we need to determine
        # if the pin is in bank 0 or 1
        port = 0
        if pin > 7:
            port = 1
            pin = pin - 8

        if port == 0:
            val = self.out0_drive
        elif port == 1:
            val = self.out1_drive

        loc = pin * 2  # Bit location in the register
        return (val >> loc) & 0x03

    def set_drive_mode(self, bank, mode):
        """Configures the output drive of an output bank. Sets the outputs to either open drain
        or push-pull. Note that this is not a per-pin setting. All pins in bank 0 (pins 0-7) or
        1 (pins 8-15) are set to the same mode.

        :param bank:    The bank to set. Should be 0 or 1.
        :param mode:    The mode to set. Should be one of either 'digitalio.DriveMode.PUSH_PULL'
                        or 'digitalio.DriveMode.OPEN_DRAIN'.

        :return:        Nothing.
        """
        if (bank > 1) or (bank < 0):
            raise ValueError("Bank should be either 0 (pins 0-7) or 1 (pins 8-15).")

        if mode == digitalio.DriveMode.PUSH_PULL:
            self.out_port_config = _clear_bit(self.out_port_config, bank)
        elif mode == digitalio.DriveMode.OPEN_DRAIN:
            self.out_port_config = _enable_bit(self.out_port_config, bank)
        else:
            raise ValueError(
                "Invalid drive mode. It should be either 'digitalio.DriveMode.PUSH_PULL' "
                "or 'digitalio.DriveMode.OPEN_DRAIN'."
            )

    def get_drive_mode(self, bank):
        """Reads the output drive of an output bank. All pins in bank 0 (pins 0-7) or
        1 (pins 8-15) are set to the same mode.

        :param bank:    The bank to set. Should be 0 or 1.
        :return:        The drive mode. Either 'digitalio.DriveMode.PUSH_PULL'
                        or 'digitalio.DriveMode.OPEN_DRAIN'.
        """
        if (bank > 1) or (bank < 0):
            raise ValueError("Bank should be either 0 (pins 0-7) or 1 (pins 8-15).")

        if _get_bit(self.out_port_config, bank) == 0x01:
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
        self.gpio = 0xFFFF
        self.ipol = 0x0000
        self.iodir = 0xFFFF

        self.out0_drive = 0xFFFF
        self.out1_drive = 0xFFFF
        self.input_latch = 0x0000
        self.pupd_en = 0xFFFF
        self.pupd_sel = 0xFFFF
        self.irq_mask = 0xFFFF
        self.out_port_config = 0x00

    """ Low level register access. These functions directly set or read the values of the
        registers on the device. In general, you should not need to call these
        functions directly.
    """

    @property
    def out0_drive(self):
        """Output drive strength of bank 0 (pins 0-7)."""
        return self._read_u16le(_PCAL9555_OUTPUT_DRIVE_0_0)

    @out0_drive.setter
    def out0_drive(self, val):
        self._write_u16le(_PCAL9555_OUTPUT_DRIVE_0_0, val)

    @property
    def out1_drive(self):
        """Output drive strength of bank 1 (pins 8-15)."""
        return self._read_u16le(_PCAL9555_OUTPUT_DRIVE_1_0)

    @out1_drive.setter
    def out1_drive(self, val):
        self._write_u16le(_PCAL9555_OUTPUT_DRIVE_1_0, val)

    @property
    def input_latch(self):
        """Sets latching or non-latching interrupts per pin."""
        return self._read_u16le(_PCAL9555_INPUT_LATCH_0)

    @input_latch.setter
    def input_latch(self, val):
        self._write_u16le(_PCAL9555_INPUT_LATCH_0, val)

    @property
    def pupd_en(self):
        """Enables pull up/down resistors per pin."""
        return self._read_u16le(_PCAL9555_PUPD_EN_0)

    @pupd_en.setter
    def pupd_en(self, val):
        self._write_u16le(_PCAL9555_PUPD_EN_0, val)

    @property
    def pupd_sel(self):
        """Sets a pull up or pull down resistor per pin."""
        return self._read_u16le(_PCAL9555_PUPD_SEL_0)

    @pupd_sel.setter
    def pupd_sel(self, val):
        self._write_u16le(_PCAL9555_PUPD_SEL_0, val)

    @property
    def irq_mask(self):
        """Masks or unmasks pins for generating interrupts."""
        return self._read_u16le(_PCAL9555_IRQ_MASK_0)

    @irq_mask.setter
    def irq_mask(self, val):
        self._write_u16le(_PCAL9555_IRQ_MASK_0, val)

    @property
    def irq_status(self):
        """Indicates which pin caused an interrupt."""
        return self._read_u16le(_PCAL9555_IRQ_STATUS_0)

    @irq_status.setter
    def irq_status(self, val):
        # This register is read only.
        pass

    @property
    def out_port_config(self):
        """Sets output banks to open drain or push-pull operation."""
        return self._read_u8(_PCAL9555_OUTPUT_PORT_CONFIG)

    @out_port_config.setter
    def out_port_config(self, val):
        self._write_u8(_PCAL9555_OUTPUT_PORT_CONFIG, val)
