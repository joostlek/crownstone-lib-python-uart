
class UartTopics:

    newDataAvailable = "UART_newDataAvailable"  # data is dictionary {
    #   id:                           int    # crownstone id (0-255)
    #   setupMode:                    bool   # is in setup mode
    #   switchState:                  int
    #   temperature:                  int    # chip temp in Celcius
    #   powerFactor:                  int    # factor between real and apparent
    #   powerUsageReal:               int    # power usage in watts (W)
    #   powerUsageApparent:           int    # power usage in VA
    #   accumulatedEnergy:            int
    #   timestamp:                    int    # time on Crownstone seconds since epoch with locale correction
    #   dimmerReady:                  bool   # dimming is available for use (it is not in the first 60 seconds after boot)
    #   dimmingAllowed:               bool   # this Crownstone can dim
    #   switchLocked:                 bool   # this Crownstone is switch-locked
    #   hasError:                     bool   # this crownstone has an error, if the crownstone has an error, the errors: {} dict is only valid if errorMode: true. This boolean is always valid.
    #   errorMode:                    bool   # summary type errorMode : the errors JSON is valid. This alternates with normal advertisements
    #   errors: {
    #       overCurrent:              bool
    #       overCurrentDimmer:        bool
    #       temperatureChip:          bool
    #       temperatureDimmer:        bool
    #       dimmerOnFailure:          bool
    #       dimmerOffFailure:         bool
    #       bitMask:                  int
    #   }
    #   timeIsSet:                    bool   # this crownstone knows what time it is
    # }

    uartMessage = "UART_Message" # data is dictionary: {"string": str, "data": [uint8, uint8, ...] }

