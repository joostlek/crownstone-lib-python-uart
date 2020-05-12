#!/usr/bin/env python3

"""An example that switches a Crownstone, and prints the power usage of all Crownstones."""

import time, json
from BluenetLib import Bluenet, UartEventBus, UsbTopics


# Function that's called when the power usage is updated.

def showNewData(data):
	print("New data received!")
	print(json.dumps(data, indent=2))
	print("-------------------")

# Create new instance of Bluenet
bluenet = Bluenet()

# Start up the USB bridge.
# Fill in the correct device, see the readme.
# For firmware versions below 2.1, add the parameter baudrate=38400
bluenet.initializeUSB("/dev/tty.SLAB_USBtoUART")

# Set up event listeners
UartEventBus.subscribe(UsbTopics.newDataAvailable, showNewData)

# This is the id of the Crownstone we will be switching
targetCrownstoneId = 3

# Switch this Crownstone on and off.
switchState = True
for i in range(0,100):
	if not bluenet.running:
		break

	if switchState:
		print("Switching Crownstone on  (iteration: ", i,")")
	else:
		print("Switching Crownstone off (iteration: ", i,")")
	bluenet.switchCrownstone(targetCrownstoneId, on = switchState)

	switchState = not switchState
	time.sleep(2)


bluenet.stop()
