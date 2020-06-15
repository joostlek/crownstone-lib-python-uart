
class SystemTopics:
    newCrownstoneFound    = "newCrownstoneFound"
    stateUpdate           = "stateUpdate"            # used to propagate verified state messages through the system
    uartNewPackage        = 'uartNewPackage'         # used for Ready Packets. This comes from the UartReadBuffer and data is a UartPacket.
    uartWriteData         = 'uartWriteData'          # used to write to the UART. Data is array of bytes.
    resultPacket          = 'resultPacket'           # data is a ResultPacket class instance
    meshResultPacket      = 'meshResultPacket'       # data is a list [CID, ResultPacket]
    meshResultFinalPacket = 'meshResultFinalPacket'  # data is a ResultPacket class instance

    connectionClosed      = 'connectionClosed'
    connectionEstablished = 'connectionEstablished'

