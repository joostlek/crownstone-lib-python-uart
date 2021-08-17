#!/usr/bin/env python3

"""An example that switches a Crownstone, and prints the power usage of the selected Crownstone."""

import time

from crownstone_core.packets.serviceDataParsers.containers.elements.AdvTypes import AdvType

from crownstone_uart import CrownstoneUart, UartEventBus, UartTopics


# This is the id of the Crownstone we will be switching
# change it to match the Crownstone Id you want to switch!
targetCrownstoneId = 3

def showNewData(data):
	global targetCrownstoneId
	if data.crownstoneId == targetCrownstoneId:
		print("New data received!")
		if data.type == AdvType.CROWNSTONE_STATE or data.type == AdvType.EXTERNAL_STATE:
			print(f"PowerUsage of crownstone {data.crownstoneId} is {data.powerUsageReal}W")
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
