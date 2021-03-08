# crownstone-lib-python-uart

Official Python lib for Crownstone: "Crownstone Unified System Bridge", or **Crownstone USB** implementation.

This works on all platforms and requires a **Crownstone USB** to work.

# Install guide

This module is written in Python 3 and needs Python 3.7 or higher. The reason for this is that most of the asynchronous processes use the embedded asyncio core library.

If you want to use python virtual environments, take a look at the [README_VENV](README_VENV.MD)

You can install the package by pip
```python
pip3 install crownstone-uart
```
If you prefer the cutting edge (which may not always work!) or want to work on the library itself, use the setuptools.

```
python3 setup.py install
```


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
- Find out what port to use (e.g. `COM1`, `/dev/ttyUSB0`, or `/dev/tty.SLAB_USBtoUART`) and fill this in at `discoveryExample.py` and `example.py` at the `initializeUSB` method.
- install the CrownstoneUartLib library using the setup.py:

```python
python3 setup.py install

# or:

python setup.py install
```

## Find the IDs of your Crownstones

Firstly run the example script that simply lists the IDs of the Crownstones. They are located in /examples/examplesUsb:
```
$ python3 ./examples/discoveryExample.py
```

Some systems may require calling python3 specifically:
```
$ python3 ./examples/discoveryExample.py
```

Once some IDs are printed, use one of them for the next example. This can take a while because Crownstones, if not switched, only broadcast their state every 60 seconds.


## Switch a Crownstone, and show power usage.

After filling in the port to use, and the Crownstone ID to switch, run the example with python 3:
```
$ python example.py
```

Some systems may require calling python3 specifically:
```
$ python3 example.py
```

## The code

The example is shown below to get an idea of how everything works:

```python
#!/usr/bin/env python3

"""An example that switches a Crownstone, and prints the power usage of the selected Crownstone."""

import time
from crownstone_uart import CrownstoneUart, UartEventBus, UartTopics


# This is the id of the Crownstone we will be switching
# change it to match the Crownstone Id you want to switch!
targetCrownstoneId = 3

def showNewData(data):
	global targetCrownstoneId
	if data["id"] == targetCrownstoneId:
		print("New data received!")
		print("PowerUsage of crownstone", data["id"], data["powerUsageReal"])
		print("-------------------")


uart = CrownstoneUart()

# Start up the USB bridge.
uart.initialize_usb_sync()
# you can alternatively do this async by
# await uart.initialize_usb()

# Set up event listeners
UartEventBus.subscribe(UartTopics.newDataAvailable, showNewData)

# Switch this Crownstone on and off.
turnOn = True

# The try except part is just to catch a control+c, time.sleep does not appreciate being killed.
try:
	for i in range(0, 10):
		if not uart.running:
			break

		if turnOn:
			print("Switching Crownstone on  (iteration: ", i,")")
		else:
			print("Switching Crownstone off (iteration: ", i,")")
		uart.switch_crownstone(targetCrownstoneId, on = turnOn)

		turnOn = not turnOn
		time.sleep(2)
except KeyboardInterrupt:
	print("\nClosing example.... Thanks for your time!")

uart.stop()

```


# Documentation

[The docs can be found here.](./DOCUMENTATION.md)


# License

MIT
