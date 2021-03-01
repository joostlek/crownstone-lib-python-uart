import logging

from crownstone_core.Exceptions import CrownstoneError
from crownstone_core.util.DataStepper import DataStepper

from crownstone_uart.core.uart.uartPackets.UartLogHeaderPacket import UartLogHeaderPacket

_LOGGER = logging.getLogger(__name__)

class UartLogArrayPacket:
	"""
	UART log array packet
	"""

	def __init__(self, buffer: list = None):
		self.header = UartLogHeaderPacket()
		self.elementType = None
		self.elementSize = 0
		self.elementData = None
		if buffer != None:
			self.parse(buffer)

	def parse(self, buffer: list):
		"""
		Parses data.

		:returns True on success.
		"""
		try:
			streamBuf = DataStepper(buffer)
			self.header.parse([], streamBuf)
			self.elementType = streamBuf.getUInt8()
			self.elementSize = streamBuf.getUInt8()
			self.elementData = streamBuf.getRemainingBytes()
			return True
		except CrownstoneError as e:
			_LOGGER.warning(F"Parse error: {e}")
			return False
