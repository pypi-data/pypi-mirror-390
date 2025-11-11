
class ButtonController:    

    def __init__(self, serialPort):
        self.transport = serialPort

    def Enable(self, pin: int, state: int) -> bool:      
        cmd = f"btnen({pin}, {int(state)})"

        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        return r
            
    def Up(self, pin):
        cmd = f"btnup({pin})"

        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        if r:
            try:
                return int(s) == 1
            except:
                pass

        return False   
    
    def Down(self, pin):
        cmd = f"btndown({pin})"

        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        if r:
            try:
                return int(s) == 1
            except:
                pass

        return False
        
    def Read(self, pin):
        cmd = f"btnread({pin})"

        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        if r:
            try:
                return int(s) == 1
            except:
                pass

        return False
