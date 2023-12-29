# SPDX-FileCopyrightText: 2023 Pat Satyshur
#
# SPDX-License-Identifier: MIT

"""
`helpers`
====================================================

Helper functions that are used by the various other classes.
These are a bunch of helper functions that are collected here to avoid circular import references.

* Author(s): Pat Satyshur
"""


# TODO: Look at this later, it does not look right.
class Capability:  # pylint: disable=too-few-public-methods
    """IO Expander Capability
    A one in the corresponding bit position below indicates
    that feature is supported by the IO expander.
    """

    PULL_UP = 0
    PULL_DOWN = 1
    INVERT_POL = 2
    DRIVE_MODE = 3


Capability = Capability()


# Internal helpers to simplify setting and getting a bit inside an integer.
def _get_bit(val, bit):
    return val & (1 << bit) > 0


def _enable_bit(val, bit):
    return val | (1 << bit)


def _clear_bit(val, bit):
    return val & ~(1 << bit)
