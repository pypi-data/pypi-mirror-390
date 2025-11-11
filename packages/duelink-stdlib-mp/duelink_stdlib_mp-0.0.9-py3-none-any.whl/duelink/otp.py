
class OtpController:   

    def __init__(self, serialPort, stream):
        self.transport = serialPort
        self.stream = stream

    def Write(self, address: int, data: bytes)->bool:
        count = len(data)
        # declare b9 array
        cmd = f"dim b9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # write data to b9
        ret = self.stream.WriteBytes("b9",data)

        # write b9 to dmx
        cmd = f"OtpW({address},b9)"
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        return r

    def Read(self, address: int)->int:
        cmd = f"OtpR({address})"
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        if r:            
            try:
                value = int(s)
                return value
            except:
                pass

        return -1
        
        




       



