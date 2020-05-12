#!/usr/bin/env python3

"""An example that prints all Crownstone IDs seen on the mesh."""

import time, datetime, json
from BluenetLib import Bluenet, UartEventBus, UsbTopics

# Create new instance of Bluenet
bluenet = Bluenet()

# Start up the USB bridge.
# Fill in the correct device, see the readme.
# For firmware versions below 2.1, add the parameter baudrate=38400
bluenet.initializeUSB("/dev/ttyUSB0")

def log(string):
	now = datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")
	payload = now + " - " + string
	filename = datetime.datetime.now().strftime("%Y-%m-%d %H") + ".txt"
	handle = open(filename, "a")
	handle.write(payload + "\n")
	handle.close()

	print(payload)

def showNewData(data):
	print("New data received!")
	print(json.dumps(data, indent=2))
	print("-------------------")

	log("PING!")
	bluenet.uartEcho("PONG!")

def showUartMessage(data):
	log("Received Uart Message " + data["string"])

# Set up event listeners
UartEventBus.subscribe(UsbTopics.newDataAvailable, showNewData)
UartEventBus.subscribe(UsbTopics.uartMessage, showUartMessage)

# List the ids that have been seen
print("Listening for Crownstones on the mesh, this might take a while.")
while bluenet.running:
	time.sleep(1)
	# ids = bluenet.getCrownstoneIds()
	# print("Crownstone IDs seen so far:", ids)

