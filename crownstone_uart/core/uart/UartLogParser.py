import logging
import re
import os
import datetime
import sys

from crownstone_core.util.Conversion import Conversion
from crownstone_core.util.DataStepper import DataStepper

_LOGGER = logging.getLogger(__name__)

class UartLogParser:
	# sourceFilesDir = "/opt/bluenet-workspace/bluenet/source"
	sourceFilesDir = "/home/vliedel/dev/bluenet-workspace-cmake/bluenet/source"

	timestampFormat = "%Y-%m-%d %H:%M:%S.%f"

	# Key: filename
	# Data: all lines in file as list.
	bluenetFiles = {}

	# Key: filename hash.
	# Data: filename.
	fileNameHashMap = {}

	# A list with the full path of all the source files (and maybe some more).
	fileNames = []

	class LogFlags:
		prefix = False
		newLine = False

		def parse(self, flags):
			self.prefix =  (flags & (1 << 0)) != 0
			self.newLine = (flags & (1 << 1)) != 0

	def __init__(self):

		# We could also get all source files from: build/default/CMakeFiles/crownstone.dir/depend.internal

		# Simply get all files in a dir.
		for root, dirs, files in os.walk(self.sourceFilesDir):
			for fileName in files:
				self.fileNames.append(os.path.join(root, fileName))

		for fileName in self.fileNames:
			# Cache hash of all file names.
			fileNameHash = self.getFileNameHash(fileName)
			self.fileNameHashMap[fileNameHash] = fileName

			# Cache contents of all files.
			filePath = fileName
			file = open(filePath, "r")
			lines = file.readlines()
			file.close()
			self.bluenetFiles[fileName] = lines

#		print(self.fileNameHashMap[1813393213]) # Should be cs_Crownstone.cpp

	def getFileNameHash(self, fileName: str):
		byteArray = bytearray()
		byteArray.extend(map(ord, fileName))

		hashVal: int = 5381
		# A string in C ends with 0.
		hashVal = (hashVal * 33 + 0) & 0xFFFFFFFF
		for c in reversed(byteArray):
			if c == ord('/'):
				return hashVal
			hashVal = (hashVal * 33 + c) & 0xFFFFFFFF
		return hashVal

	logPattern = re.compile(".*?LOG[a-zA-Z]+\(\"([^\"]*)\"")
	rawLogPattern = re.compile(".*?_log\([^,]+,[^,]+,[^,]+,\s*\"([^\"]*)\"")

	def getLogFmt(self, fileName, lineNr):
		lines = self.bluenetFiles[fileName]
		lineNr = lineNr - 1 # List starts at 0, line numbers start at 1.

		if lineNr < 0 or lineNr >= len(lines):
			_LOGGER.warning("Invalid line number " + str(lineNr + 1))
			return None
		line = lines[lineNr]
		match = self.logPattern.match(line)
		if match:
			return match.group(1)
		match = self.rawLogPattern.match(line)
		if match:
			return match.group(1)
		else:
			_LOGGER.warning(f"Can't find log format in: {fileName[-30:]}:{lineNr} {line.rstrip()}")
			return None

	def parse(self, buffer):
		timestamp = datetime.datetime.now()
		dataStepper = DataStepper(buffer)
		fileNameHash = dataStepper.getUInt32()
		lineNr = dataStepper.getUInt16()
		flags = dataStepper.getUInt8()
		numArgs = dataStepper.getUInt8()
		argBufs = []
		for i in range(0, numArgs):
			argSize = dataStepper.getUInt8()
			argBufs.append(dataStepper.getAmountOfBytes(argSize))

		fileName = self.fileNameHashMap.get(fileNameHash, None)
		if fileName is None:
			return

		logFlags = UartLogParser.LogFlags()
		logFlags.parse(flags)

		# print(f"{fileName}:{lineNr} {argBufs}")
		logFmt = self.getLogFmt(fileName, lineNr)
		_LOGGER.debug(f"Log {fileName}:{lineNr} {logFmt} {argBufs}")

		if logFmt is not None:
			formattedString = ""
			i = 0
			argNum = 0
			while i < len(logFmt):
				if logFmt[i] == '%':
					# Check the arg format.
					i += 1
				else:
					# Just append the character
					formattedString += logFmt[i]
					i += 1
					continue

				if logFmt[i] == '%':
					# Actually not an arg, but an escaped '%'
					formattedString += logFmt[i]
					i += 1
					continue

				# Check arg type and let python do the formatting.
				argVal = 0     # Value of this arg
				argFmt = "%"   # Format of this arg
				while True:
					c = logFmt[i]
					argBuf = argBufs[argNum]
					argLen = len(argBuf)

					if c == 'd' or c == 'i':
						# Signed integer
						argVal = 0
						if argLen == 1:
							argVal = Conversion.uint8_to_int8(argBuf[0])
						elif argLen == 2:
							argVal = Conversion.uint8_array_to_int16(argBuf)
						elif argLen == 4:
							argVal = Conversion.uint8_array_to_int32(argBuf)
						elif argLen == 8:
							argVal = Conversion.uint8_array_to_int64(argBuf)

						argFmt += c
						break

					elif c == 'u' or c == 'x' or c == 'X' or c == 'o' or c == 'p':
						# Unsigned integer
						argVal = 0
						if argLen == 1:
							argVal = argBuf[0]
						elif argLen == 2:
							argVal = Conversion.uint8_array_to_uint16(argBuf)
						elif argLen == 4:
							argVal = Conversion.uint8_array_to_uint32(argBuf)
						elif argLen == 8:
							argVal = Conversion.uint8_array_to_uint64(argBuf)

						if c == 'p':
							# Python doesn't do %p
							argFmt += 'x'
						else:
							argFmt += c
						break

					elif c == 'f' or c == 'F' or c == 'e' or c == 'E' or c == 'g' or c == 'G':
						# Floating point
						argVal = 0.0
						if argLen == 4:
							argVal = Conversion.uint8_array_to_float(argBuf)

						argFmt += c
						break

					elif c == 'a':
						# Character
						argVal = ' '
						if argLen == 1:
							argVal = argBuf[0]

						argFmt += c
						break

					elif c == 's':
						# String
						argVal = Conversion.uint8_array_to_string(argBuf)

						argFmt += c
						break

					else:
						i += 1
						argFmt += c
						continue

				# Let python do the formatting
				argStr = argFmt % argVal
				formattedString += argStr
				argNum += 1
				i += 1

			logStr = formattedString
			# sys.stdout.write(f" {{ {flags} {logFlags.prefix} {logFlags.newLine} }} ")
			if logFlags.prefix:
				logStr = f"LOG: [{timestamp.strftime(self.timestampFormat)}] [{fileName[-30:]}:{lineNr:4n}] {logStr}"

			sys.stdout.write(logStr)
			if logFlags.newLine:
				# print(logStr)
				sys.stdout.write('\n')
			else:
				# print(logStr, end='')
				pass

if __name__ == "__main__":
	uartLogParser = UartLogParser()


