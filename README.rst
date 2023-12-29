Introduction
============


.. image:: https://readthedocs.org/projects/circuitpython-i2c-expanders/badge/?version=latest
    :target: https://circuitpython-i2c-expanders.readthedocs.io/
    :alt: Documentation Status



.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/ilikecake/CircuitPython_I2C_Expanders/workflows/Build%20CI/badge.svg
    :target: https://github.com/ilikecake/CircuitPython_I2C_Expanders/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

Drivers for various I2C GPIO expanders. The library does not require any libraries other than the standard install of circuit python. Once the exapander has been initialized, the pins can be defined and interacted with in the same way as GPIOs on the CPU. 

This library currently supports

* PCA9555
* PCAL9555
* PCA9554
* PCAL9554
* PCA9538
* PCAL9538

Other expanders will likely be added over time as I use them. 

Based on Adafruit's library for the `MCP230xx expanders <https://github.com/adafruit/Adafruit_CircuitPython_MCP230xx>`_

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing from PyPI
=====================
.. note:: This library is not available on PyPI yet. Install documentation is included
   as a standard element. Stay tuned for PyPI availability!

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install i2c_expanders

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============
Take a look in the examples folder for a basic example of using this library.

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-i2c-expanders.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/ilikecake/CircuitPython_I2C_Expanders/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
