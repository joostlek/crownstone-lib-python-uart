from crownstone_core.util.Conversion import Conversion
from crownstone_uart.util.UartUtil import UartUtil

ESCAPE_TOKEN = 0x5c
BIT_FLIP_MASK = 0x40
START_TOKEN = 0x7e


class UartWrapper:

	def __init__(self, opCode, payload):
		self.opCode = opCode
		self.payload = payload


	def escapeCharacters(self, payload):
		escapedPayload = []
		for byte in payload:
			if byte is ESCAPE_TOKEN or byte is START_TOKEN:
				escapedPayload.append(ESCAPE_TOKEN)
				escapedByte = byte ^ BIT_FLIP_MASK
				escapedPayload.append(escapedByte)
			else:
				escapedPayload.append(byte)

		return escapedPayload


	def getPacket(self):
		# get the length of the payload before escaping
		baseLength = len(self.payload)

		# construct the basePacket, which is used for CRC calculation
		basePacket = []
		basePacket += Conversion.uint16_to_uint8_array(self.opCode)
		basePacket += Conversion.uint16_to_uint8_array(baseLength)
		basePacket += self.payload

		# calculate the CRC of the packet so 
		baseCrc = UartUtil.crc16_ccitt(basePacket)

		# append the CRC to the base packet to escape the entire thing
		basePacket += Conversion.uint16_to_uint8_array(baseCrc)

		# escape everything except the START_TOKEN
		escapedPayload = self.escapeCharacters(basePacket)

		uartPacket = []
		uartPacket.append(START_TOKEN)
		uartPacket += escapedPayload

		return uartPacket