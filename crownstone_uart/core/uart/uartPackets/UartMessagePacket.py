import logging

from crownstone_core.Exceptions import CrownstoneError
from crownstone_core.util.Conversion import Conversion
from crownstone_core.util.DataStepper import DataStepper

from crownstone_uart.core.uart.UartTypes import UartTxType

_LOGGER = logging.getLogger(__name__)

class UartMessagePacket:
	"""
	UART message packet:
	1B device ID
	2B data type (aka opcode)
	xB data
	"""

	def __init__(self, deviceId: int = 0, opCode: UartTxType = UartTxType.UNKNOWN, payload: list = None):
		"""
		:param deviceId:     uint8
		:param opCode:       uint16 data type.
		:param payload:      List of uint8, according to data type
		"""
		self.deviceId = deviceId
		self.opCode = opCode
		if payload is None:
			self.payload = []
		else:
			self.payload = payload

	def parse(self, buffer: list):
		"""
		Parses data.

		:returns True on success.
		"""
		try:
			streamBuf = DataStepper(buffer)
			self.deviceId = streamBuf.getUInt8()
			self.opCode = streamBuf.getUInt16()
			self.payload = streamBuf.getRemainingBytes()
			return True
		except CrownstoneError as e:
			_LOGGER.warning(F"Parse error: {e}")
			return False

	def getPacket(self):
		# Header: 1B device ID, 2B opcode

		# construct the basePacket, which is used for CRC calculation
		uartMsg = []
		uartMsg.append(self.deviceId)
		uartMsg += Conversion.uint16_to_uint8_array(self.opCode)
		uartMsg += self.payload

		return uartMsg