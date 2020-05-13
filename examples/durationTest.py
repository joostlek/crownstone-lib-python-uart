#!/usr/bin/env python3

"""An example that prints all Crownstone IDs seen on the mesh."""

import time, json

from crownstone_uart.topics.UsbTopics import UsbTopics
from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.CrownstoneUart import CrownstoneUart

uart = CrownstoneUart()

# Start up the USB bridge.
uart.initialize_usb_sync()

def showNewData(data):
	print("New data received!")
	print(json.dumps(data, indent=2))
	print("-------------------")

	print("PING!")
	uart.uartEcho("PONG!")

def showUartMessage(data):
	print("Received Uart Message " + data["string"])

# Set up event listeners
UartEventBus.subscribe(UsbTopics.newDataAvailable, showNewData)
UartEventBus.subscribe(UsbTopics.uartMessage, showUartMessage)

print("Listening for Crownstones on the mesh, this might take a while.")
# the try except part is just to catch a control+c, time.sleep does not appreciate being killed.
try:
	while uart.running:
		time.sleep(1)
except KeyboardInterrupt:
	print("Closing example.... Thanks for your time!")

uart.stop()
