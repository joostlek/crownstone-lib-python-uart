
class SystemTopics:
    newCrownstoneFound    = "newCrownstoneFound"
    stateUpdate           = "stateUpdate"            # used to propagate verified state messages through the system
    uartNewPackage        = 'uartNewPackage'         # Sent when a UART packet is received. Data is a UartWrapperPacket.
    uartNewMessage        = 'uartNewMessage'         # Sent when a UART message is received. Data is a UartMessagePacket.
    uartWriteData         = 'uartWriteData'          # used to write to the UART. Data is array of bytes.

    uartWriteError        = 'uartWriteError'         # used to write to the UART. Data is array of bytes.
    uartWriteSuccess      = 'uartWriteSuccess'       # used to write to the UART. Data is array of bytes.

    resultPacket          = 'resultPacket'           # data is a ResultPacket class instance
    meshResultPacket      = 'meshResultPacket'       # data is a list [CID, ResultPacket]
    meshResultFinalPacket = 'meshResultFinalPacket'  # data is a ResultPacket class instance

    connectionClosed      = 'connectionClosed'
    connectionEstablished = 'connectionEstablished'

