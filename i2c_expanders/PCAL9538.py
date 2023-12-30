# SPDX-FileCopyrightText: 2023 Pat Satyshur
# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Carter Nelson
#
# SPDX-License-Identifier: MIT

# pylint: disable=too-many-public-methods, duplicate-code
# Note: there is a bit of duplicated code between this and the other PCAL parts. This code is
#       duplicated for these two expanders, but may not be if other expanders are added to this
#       library. I therefore  want to keep is separate in these two classes. The line above
#       disables the pylint check for this.

"""
`PCAL9538`
====================================================

CircuitPython module for the PCAL9538 I2C I/O extenders.
The PCAL9554 is a 8 pin IO Expander. It is software compatible with the PCA9554, but has a
bunch of added functions.

Added features of these expanders include:

* Built in pull up and pull down resistors.
* Per pin selectable drive strength.
* Maskable interrupt pins
* Latching interrupt option
* Per bank push-pull/open drain pin setup.

Required library files (.py or their .mpy equivalent):

* PCAL9538.py
* PCAL9554.py
* PCA9554.py
* i2c_expander.py
* digital_inout.py
* helpers.py

Compatible Devices

* PCAL9554
* PCAL9538

These are devices I have specifically tested and know work. There appear to be a lot more devices
with similar naming schemes that use the same register map. These should also be compatible, but
make sure you check the i2c address and default register state.

:Note: By default if an (non-latched) interrupt enabled pin changes state, but changes back before
       the GPIO state register is read, the interrupt state will be cleared. Setting the interrupt
       latch will cause the device to latch on a state change of the input pin. With latching
       enabled, on a state change to the pin, the interrupt pin will be asserted and will not
       deassert until the input register is read. The value read from the input register will be
       the value that caused the interrupt, not nessecarially the current value of the pin. If the
       pin changed state, but changed back before the input register was read, the changed state
       will be what is returned in the register. The state change back to the original state will
       not trigger another interrupt as long as it happens before the input register is read. If
       the input register is read before the pin state changes back to the original value, both
       state changes will cause an interrupt.

Heavily based on the code written by Tony DiCola for the MCP230xx library.

* Author(s): Pat Satyshur
"""

# TODO: Disable unused imports here. After I finish this code, turn that off and see if they
# are still unused.
# pylint: disable=unused-import
from micropython import const
import digitalio

from i2c_expanders.PCAL9554 import PCAL9554
from i2c_expanders.helpers import Capability, _get_bit, _enable_bit, _clear_bit


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/ilikecake/CircuitPython_I2C_Expanders.git"

# This is the default address for the PCA9538 with all addr pins grounded.
_PCAL9538_DEFAULT_ADDRESS = const(0x70)


class PCAL9538(PCAL9554):
    """The class for the PCAL9538 expander. Instantiate one of these for each expander on the bus.
    Make sure you get the address right.
    """

    def __init__(self, i2c, address=_PCAL9538_DEFAULT_ADDRESS, reset=True):
        super().__init__(
            i2c, address, False
        )  # This initializes the PCA9554 compatible registers.
        self._capability = (
            _enable_bit(0x00, Capability.PULL_UP)
            | _enable_bit(0x00, Capability.PULL_DOWN)
            | _enable_bit(0x00, Capability.INVERT_POL)
        )

        if reset:
            self.reset_to_defaults()

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
        self.pupd_en = 0x00
        self.pupd_sel = 0xFF
        self.irq_mask = 0xFF
        self.out_port_config = 0x00
