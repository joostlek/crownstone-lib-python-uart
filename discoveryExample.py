#!/usr/bin/env python3

"""An example that prints all Crownstone IDs seen on the mesh."""

import time


# Create new instance of Bluenet
from crownstone_uart.core.CrownstoneUart import CrownstoneUart

bluenet = CrownstoneUart()
# Start up the USB bridge.
# Fill in the correct device, see the readme.
bluenet.initialize_usb_sync()

# List the ids that have been seen
# print("Listening for Crownstones on the mesh, this might take a while.")
# while bluenet.running:
# 	time.sleep(2)
# 	ids = bluenet.getCrownstoneIds()
# 	print("Crownstone IDs seen so far:", ids)
#
#
# bluenet.stop()
