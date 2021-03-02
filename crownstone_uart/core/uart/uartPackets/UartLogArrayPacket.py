import logging

from crownstone_core.packets.BasePacket import BasePacket
from crownstone_core.util.DataStepper import DataStepper

from crownstone_uart.core.uart.uartPackets.UartLogHeaderPacket import UartLogHeaderPacket

_LOGGER = logging.getLogger(__name__)

class UartLogArrayPacket(BasePacket):
	"""
	UART log array packet
	"""

	def __init__(self, data = None):
		self.header = UartLogHeaderPacket()
		self.elementType = None
		self.elementSize = 0
		self.elementData = None
		if data != None:
			self.parse(data)

	def _parse(self, dataStepper: DataStepper):
		self.header.parse(dataStepper)
		self.elementType = dataStepper.getUInt8()
		self.elementSize = dataStepper.getUInt8()
		self.elementData = dataStepper.getRemainingBytes()

	def __str__(self):
		return f"UartLogArrayPacket(" \
		       f"header={self.header}, " \
		       f"elementType={self.elementType}, " \
		       f"elementSize={self.elementSize}, " \
		       f"elementData={self.elementData})"
