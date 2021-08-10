#!/usr/bin/env python3

"""An example that prints all Crownstone IDs seen on the mesh."""

import time, json

from crownstone_uart import CrownstoneUart, UartEventBus, UartTopics

uart = CrownstoneUart()

# Start up the USB bridge.
uart.initialize_usb_sync()

def showNewData(data):
	print("New data received!")
	print(data)
	print("-------------------")

	print("PING!")
	uart.uart_echo("PONG!")

def showUartMessage(data):
	print("Received Uart Message " + data["string"])

# Set up event listeners
UartEventBus.subscribe(UartTopics.newDataAvailable, showNewData)
UartEventBus.subscribe(UartTopics.uartMessage, showUartMessage)

print("Listening for Crownstones on the mesh, this might take a while.")
# the try except part is just to catch a control+c, time.sleep does not appreciate being killed.
try:
	while uart.running:
		time.sleep(1)
except KeyboardInterrupt:
	print("Closing example.... Thanks for your time!")

uart.stop()
