
class FrequencyController:    
    def __init__(self, serialPort):
        self.transport = serialPort

    def Write(self, pin: int, frequency, duration_ms=0, dutycyle=0.5)->bool:
        if frequency < 16 or frequency > 24000000:
            raise Exception("Frequency must bin range 16Hz..24,000,000Hz")
        if dutycyle < 0 or dutycyle > 1:
            raise Exception("Duty cycle must be in range 0..1")
        
        cmd = "freq({}, {}, {}, {})".format(pin, frequency, duration_ms, dutycyle)
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        return r


