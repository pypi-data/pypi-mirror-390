# CT: 05/26/2025 - Tested
class DigitalController:    

    def __init__(self, serialPort):
        self.transport = serialPort

    def Read(self, pin, pull):
        self.transport.WriteCommand(f"dread({pin},{pull})")        
        r, s = self.transport.ReadResponse()        
        if r:
            return int(s, 10)        

    def Write(self, pin, value):
        self.transport.WriteCommand(f"dwrite({pin},{value})")
        r, s = self.transport.ReadResponse()
        return r
