class InfraredController:
    def __init__(self, serialPort):
        self.transport = serialPort

    def Read(self)->int:
        cmd = "irread()"
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        if r:
            try:
                return int(s)
            except:
                pass
        return -1
    
    def Write(self, command: int)->bool:
        cmd = f"IrWrite({command})"
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()
        return r

    def Enable(self, txpin:int, rxpin: int)->bool:
        cmd = f"iren({txpin}, {rxpin})"
        self.transport.WriteCommand(cmd)

        r,s = self.transport.ReadResponse()
        return r
