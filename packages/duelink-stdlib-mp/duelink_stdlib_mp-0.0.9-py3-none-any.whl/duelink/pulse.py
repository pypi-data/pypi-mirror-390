
class PulseController:   

    def __init__(self, serialPort):
        self.transport = serialPort


    def Read(self, pin: int, charge_t: int, charge_s: int, timeout: int)->int:                
        cmd = "PulseIn({0}, {1}, {2}, {3})".format(pin, charge_t, charge_s, timeout)
        self.transport.WriteCommand(cmd)        

        r,s = self.transport.ReadResponse()

        if r:            
            try:
                value = int(s)
                return value
            except:
                pass

        return 0

        
        




       



