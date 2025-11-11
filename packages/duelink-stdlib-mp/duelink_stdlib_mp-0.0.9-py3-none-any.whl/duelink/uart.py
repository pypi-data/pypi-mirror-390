class UartController:
    def __init__(self, serialPort, stream):
        self.transport = serialPort
        self.stream = stream

    def Configuration(self, baudrate: int, rx_buf_size: int)->bool:
        cmd = "SerCfg({0}, {1})".format(baudrate, rx_buf_size)
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()
        return r

    def WriteByte(self, data: int)->bool:
        cmd = "SerWr({})".format(data)
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()
        return r        
    
    def WriteBytes(self, data: bytes)->int:
        count = len(data)
        cmd = f"dim b9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        written = self.stream.WriteBytes("b9", data)

        self.transport.WriteCommand("SerWrs(b9)")
        r,s = self.transport.ReadResponse()

        if (r):
            return written

        return 0
    
    def ReadByte(self):        
        self.transport.WriteCommand("SerRd()")
        r,s = self.transport.ReadResponse()
        if r:
            try:
                data = int(s)
                return data
            except:
                pass
        return 0
    
    def ReadBytes(self, data: bytearray, timeout_ms: int)->int:
        count = len(data)
        cmd = f"dim b9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        cmd = f"SerRds(b9, {timeout_ms})"
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        read = self.stream.ReadBytes("b9",data )

        if (r):
            return read

        return 0

    def BytesToRead(self)->int:        
        self.transport.WriteCommand("SerB2R()")
        r,s = self.transport.ReadResponse()
        if r:
            try:
                ready = int(s)
                return ready
            except:
                pass
        return 0
    
    def Discard(self)->bool:        
        self.transport.WriteCommand("SerDisc()")
        r,s = self.transport.ReadResponse()
        
        return r
    

    
