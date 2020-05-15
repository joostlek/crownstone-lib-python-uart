#!/usr/bin/env python3

"""An example that switches a Crownstone, and prints the power usage of all Crownstones."""

import time

# Create new instance of uart
from crownstone_uart import CrownstoneUart, UartEventBus, UartTopics

uart = CrownstoneUart()

# Start up the USB bridge.
uart.initialize_usb_sync()
# you can alternatively do this async by
# await uart.initialize_usb()

# Function that's called when the power usage is updated.
def showUartMessage(data):
	print("Received payload", data)

# Set up event listeners
UartEventBus.subscribe(UartTopics.uartMessage, showUartMessage)

# the try except part is just to catch a control+c, time.sleep does not appreciate being killed.
try:
	uart.uartEcho("HelloWorld")
	time.sleep(0.2)
	uart.uartEcho("HelloWorld")
	time.sleep(0.2)
	uart.uartEcho("HelloWorld")
	time.sleep(0.2)
	uart.uartEcho("HelloWorld")
	time.sleep(0.2)
	uart.uartEcho("HelloWorld")
	time.sleep(0.2)
	uart.uartEcho("HelloWorld")
	time.sleep(0.2)
	uart.uartEcho("HelloWorld")
	time.sleep(0.2)
	uart.uartEcho("HelloWorld")
	time.sleep(0.2)
	uart.uartEcho("HelloWorld")
	time.sleep(0.2)
	uart.uartEcho("HelloWorld")
	time.sleep(0.2)
	uart.uartEcho("HelloWorld")
	time.sleep(0.2)
except KeyboardInterrupt:
	print("Closing example.... Thanks for your time!")

uart.stop()