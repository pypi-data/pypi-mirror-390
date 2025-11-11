
class AnalogController:        
    def __init__(self, serialPort):
        self.transport = serialPort

    def VoltRead(self, pin):
        cmd = "vread({0})".format(pin)

        self.transport.WriteCommand(cmd)

        r,s = self.transport.ReadResponse()

        if r:
            try:
                return float(s)
            except:
                pass

        return 0
    
    def Read(self, pin):
        cmd = "aread({0})".format(pin)

        self.transport.WriteCommand(cmd)

        r,s = self.transport.ReadResponse()

        if r:
            try:
                return float(s)
            except:
                pass

        return 0
    
    def Write(self, pin, duty_cycle):
               
        if duty_cycle < 0 or duty_cycle > 1:
            raise ValueError('Duty cycle must be in the range 0..1')

        cmd = f'awrite({pin}, {duty_cycle})'
        self.transport.WriteCommand(cmd)

        r,s = self.transport.ReadResponse()

        return r
    
    def ReadVcc(self):
        cmd = f"readvcc()"
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        if r:
            try:
                return float(s)
            except:
                pass

        return 0
    
