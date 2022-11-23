# Crownstone UART

Official Python lib for Crownstone: "Crownstone Unified System Bridge", or **Crownstone USB** implementation.

This works on all platforms and requires a **Crownstone USB** to work.

# Install guide

This module is written in Python 3 and needs Python 3.7 or higher. The reason for this is that most of the asynchronous processes use the embedded asyncio core library.

If you want to use python virtual environments, take a look at the [README_VENV](README_VENV.MD)

You can install the package by pip:
```
pip3 install crownstone-uart
```

If you prefer the cutting edge (which may not always work!) or want to work on the library itself, use the setuptools: `python3 setup.py install`


## Requirements for the Crownstone USB

### OS X
OS X requires installation of the SiliconLabs driver: [https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers](https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers)

### Ubuntu
In order to use serial without root access, you should be in the `dialout` group.

You can check if you're in the group:
```
$ groups
```

To add yourself:
```
$ sudo adduser $USER dialout
```

You may need to logout and login again.


### Raspbian
Similar to Ubuntu.

### Arch Linux
To use serial in Arch Linux, add yourself to the `uucp` group.

To add yourself to the group:
```console
$ sudo gpasswd -a $USER uucp
```
Make sure to logout and login again to register the group change.

# Example

An example is provided in the root of this repository.

## Prerequisites

- First use the [phone app](https://crownstone.rocks/app) to setup your Crownstones and the Crownstone USB.
- Make sure you update the Crownstones' firmware to at least 5.4.0.
- Find out what port to use (e.g. `COM1`, `/dev/ttyUSB0`, or `/dev/tty.SLAB_USBtoUART`), use this to initialize the library.
- Have this library installed.

## Find the IDs of your Crownstones

Firstly run the example script that simply lists the IDs of the Crownstones.:
```
$ python3 ./examples/discovery_example.py
```

Once some IDs are printed, use one of them for the next example. This can take a while because Crownstones, if not switched, only broadcast their state every 60 seconds.


## Switch a Crownstone, and show power usage.

Edit the file `switch_example.py`:
- Set `targetCrownstoneId` to a Crownstone ID that was found in the previous example.

Run the file:
```
$ python3 ./examples/switch_example.py
```


# API documentation

[The API documentation can be found here.](./DOCUMENTATION.md)

## Open-source license

This firmware is provided under a noncontagious open-source license towards the open-source community. It's available under three open-source licenses:
 
* License: LGPL v3+, Apache, MIT

<p align="center">
  <a href="http://www.gnu.org/licenses/lgpl-3.0">
    <img src="https://img.shields.io/badge/License-LGPL%20v3-blue.svg" alt="License: LGPL v3" />
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  </a>
  <a href="https://opensource.org/licenses/Apache-2.0">
    <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0" />
  </a>
</p>

## Commercial license

This firmware can also be provided under a commercial license. If you are not an open-source developer or are not planning to release adaptations to the code under one or multiple of the mentioned licenses, contact us to obtain a commercial license.

* License: Crownstone commercial license

# Contact

For any question contact us at <https://crownstone.rocks/contact/> or on our discord server through <https://crownstone.rocks/forum/>.
