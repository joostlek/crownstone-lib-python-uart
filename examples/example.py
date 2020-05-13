#!/usr/bin/env python3

"""An example that switches a Crownstone, and prints the power usage of all Crownstones."""

import time, json


# Function that's called when the power usage is updated.
from core.UartEventBus import UartEventBus
from topics.UsbTopics import UsbTopics


def showNewData(data):
	print("New data received!")
	print(json.dumps(data, indent=2))
	print("-------------------")

# Create new instance of Bluenet
from crownstone_uart.core.CrownstoneUart import CrownstoneUart

uart = CrownstoneUart()

# Start up the USB bridge.
uart.initialize_usb_sync()
# you can alternatively do this async by
# await uart.initialize_usb()

# Set up event listeners
UartEventBus.subscribe(UsbTopics.newDataAvailable, showNewData)

# This is the id of the Crownstone we will be switching
# change it to match the Crownstone Id you want to switch!
targetCrownstoneId = 3

# Switch this Crownstone on and off.
switchState = True

# the try except part is just to catch a control+c, time.sleep does not appreciate being killed.
try:
	for i in range(0,100):
		if not uart.running:
			break

		if switchState:
			print("Switching Crownstone on  (iteration: ", i,")")
		else:
			print("Switching Crownstone off (iteration: ", i,")")
		uart.switchCrownstone(targetCrownstoneId, on = switchState)

		switchState = not switchState
		time.sleep(2)
except KeyboardInterrupt:
	print("Closing example.... Thanks for your time!")

uart.stop()
