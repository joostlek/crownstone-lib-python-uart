from enum import Enum


class SystemTopics(Enum):
    newCrownstoneFound = "newCrownstoneFound"
    stateUpdate = "stateUpdate"  # used to propagate verified state messages through the system
    uartNewPackage = 'uartNewPackage'  # used for Ready Packets. This comes from the UartReadBuffer and data is a UartPacket.
    uartWriteData = 'uartWriteData'  # used to write to the UART. Data is array of bytes.
    cleanUp = 'cleanUp'  # used to propagate CTRL+C throughout the modules.
