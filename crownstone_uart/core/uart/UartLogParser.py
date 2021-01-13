import logging
import re
import os
import datetime
import sys

from crownstone_core.util.Conversion import Conversion
from crownstone_core.util.DataStepper import DataStepper

_LOGGER = logging.getLogger(__name__)

class UartLogParser:
	sourceFilesDir = "/opt/bluenet-workspace/bluenet/source"

	timestampFormat = "%Y-%m-%d %H:%M:%S.%f"

	# Whether to enable colors in logs.
	enableColors = True
	if sys.platform == "win32":
		enableColors = False

	# Key: filename
	# Data: all lines in file as list.
	bluenetFiles = {}

	# Key: filename hash.
	# Data: filename.
	fileNameHashMap = {}

	# A list with the full path of all the source files (and maybe some more).
	fileNames = []

	# Whether the next log line should get a prefix.
	printPrefix = True

	class LogFlags:
		newLine = False

		def parse(self, flags):
			self.newLine = (flags & (1 << 0)) != 0

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
	rawLogPattern = re.compile(".*?_log\([^,]+,[^,]+,\s*\"([^\"]*)\"")

	logDefinedStringPattern = re.compile(".*?LOG[a-zA-Z]+\(([A-Z_]+)")
	rawLogDefinedStringPattern = re.compile(".*?_log\([^,]+,[^,]+,\s*([A-Z_]+)")

	def getLogFmt(self, fileName, lineNr):
		lines = self.bluenetFiles[fileName]
		lineNr = lineNr - 1 # List starts at 0, line numbers start at 1.

		if lineNr < 0 or lineNr >= len(lines):
			_LOGGER.warning("Invalid line number " + str(lineNr + 1))
			return None

		line = lines[lineNr]
		result = self.getLogFmtFromLine(line)
		if result is not None:
			return result

		# Maybe the log line is spread over multiple lines.
		brackets = 0
		for c in line[::-1]:
			if c == ')':
				brackets = brackets - 1
			if c == '(':
				brackets = brackets + 1
		if brackets < 0:
			# There are more closing than opening brackets, so the log format is probably on a line before the given line number.
			# Iterate back over lines, and merge the lines together.
			# Loop until the brackets are balanced (as many opening as closing brackets).
			# Then check if the format can be found in the merged line.
			mergedLine = line
			i = lineNr - 1
			while (i > 0):
				curLine = lines[i]
				for c in curLine[::-1]:
					if c == ')':
						brackets = brackets - 1
					if c == '(':
						brackets = brackets + 1
				mergedLine = curLine + mergedLine
				if brackets == 0:
					# Looks like we're at the first opening bracket.
					result = self.getLogFmtFromLine(mergedLine)
					if result is not None:
						return result
				i = i - 1

		_LOGGER.warning(f"Can't find log format in: {fileName[-30:]}:{lineNr} {line.rstrip()}")
		return None



	def getLogFmtFromLine(self, fileLine):
		match = self.logPattern.match(fileLine)
		if match:
			return match.group(1)

		match = self.rawLogPattern.match(fileLine)
		if match:
			return match.group(1)

		# Logs like: LOGi(FMT_INIT, "relay");
		# The string definition file contains lines like: #define FMT_INIT     "Init %s"
		# We search for the line with "FMT_INIT", and return "Init %s".
		match = self.logDefinedStringPattern.match(fileLine)
		if not match:
			match = self.rawLogDefinedStringPattern.match(fileLine)
		stringsDefFileName = self.sourceFilesDir + "/include/cfg/cs_Strings.h"
		if match and stringsDefFileName in self.bluenetFiles:
			for strDefLine in self.bluenetFiles[stringsDefFileName]:
				strDefWords = strDefLine.split()
				if len(strDefWords) >= 3 and strDefWords[0] == "#define" and strDefWords[1] == match.group(1):
					# Return the string, with quotes removed.
					return " ".join(strDefWords[2:])[1:-1]

		return None



	def parse(self, buffer):
		timestamp = datetime.datetime.now()
		dataStepper = DataStepper(buffer)
		fileNameHash = dataStepper.getUInt32()
		lineNr = dataStepper.getUInt16()
		logLevel = dataStepper.getUInt8()
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
			if self.printPrefix:
				logStr = self.getPrefix(timestamp, fileName, lineNr, logLevel) + logStr

			sys.stdout.write(logStr)
			if logFlags.newLine:
				# Next line should be prefixed.
				self.printPrefix = True
				sys.stdout.write(self.getEndColor())
				sys.stdout.write('\n')
			else:
				self.printPrefix = False

	def parseArray(self, buffer):
		timestamp = datetime.datetime.now()
		dataStepper = DataStepper(buffer)
		fileNameHash = dataStepper.getUInt32()
		lineNr = dataStepper.getUInt16()
		logLevel = dataStepper.getUInt8()
		flags = dataStepper.getUInt8()
		elementType = dataStepper.getUInt8()
		elementSize = dataStepper.getUInt8()
		dataSize = dataStepper.remaining()

		fileName = self.fileNameHashMap.get(fileNameHash, None)
		if fileName is None:
			return

		logFlags = UartLogParser.LogFlags()
		logFlags.parse(flags)


		if dataSize % elementSize != 0:
			return

		logStr = "["
		numElements = int(dataSize / elementSize)
		_LOGGER.debug(f"dataSize={dataSize} elementSize={elementSize} numElements={numElements}")
		for i in range(0, numElements):
			if elementType == 0:
				# Signed integer
				elemVal = 0
				if elementSize == 1:
					elemVal = dataStepper.getInt8()
					logStr += "%3i, " % elemVal
				elif elementSize == 2:
					elemVal = dataStepper.getInt16()
					logStr += "%5i, " % elemVal
				elif elementSize == 4:
					elemVal = dataStepper.getInt32()
					logStr += "%10i, " % elemVal
				elif elementSize == 8:
					elemVal = dataStepper.getInt64()
					logStr += "%20i, " % elemVal

			elif elementType == 1:
				# Unsigned integer
				elemVal = 0
				if elementSize == 1:
					elemVal = dataStepper.getUInt8()
					logStr += "%3u, " % elemVal
				elif elementSize == 2:
					elemVal = dataStepper.getUInt16()
					logStr += "%5u, " % elemVal
				elif elementSize == 4:
					elemVal = dataStepper.getUInt32()
					logStr += "%10u, " % elemVal
				elif elementSize == 8:
					elemVal = dataStepper.getUInt64()
					logStr += "%20u, " % elemVal

			elif elementType == 2:
				# Floating point
				elemVal = 0.0
				if elementSize == 4:
					argVal = dataStepper.getFloat()
				logStr += "%f, " % elemVal

		# Remove last ", " and add closing bracket.
		logStr = logStr[0:-2] + "]"

		if self.printPrefix:
			logStr = self.getPrefix(timestamp, fileName, lineNr, logLevel) + logStr

		sys.stdout.write(logStr)
		if logFlags.newLine:
			# Next line should be prefixed.
			self.printPrefix = True
			sys.stdout.write(self.getEndColor())
			sys.stdout.write('\n')
		else:
			self.printPrefix = False

	def getPrefix(self, timestamp, fileName, lineNr, logLevel):
		return f"LOG: [{timestamp.strftime(self.timestampFormat)}] [{fileName[-30:]}:{lineNr:4n}] {self.getLogLevelStr(logLevel)}{self.getLogLevelColor(logLevel)} "

	def getLogLevelStr(self, logLevel):
		if logLevel == 8: return "V"
		if logLevel == 7: return "D"
		if logLevel == 6: return "I"
		if logLevel == 5: return "W"
		if logLevel == 4: return "E"
		if logLevel == 3: return "F"
		return " "

	def getLogLevelColor(self, logLevel):
		if self.enableColors:
			if logLevel == 8: return "\033[37;1m" # White
			if logLevel == 7: return "\033[37;1m" # White
			if logLevel == 6: return "\033[34;1m" # Blue
			if logLevel == 5: return "\033[33;1m" # Yellow
			if logLevel == 4: return "\033[35;1m" # Purple
			if logLevel == 3: return "\033[31;1m" # Red
		return ""

	def getEndColor(self):
		if self.enableColors:
			return "\033[0m"
		return ""

