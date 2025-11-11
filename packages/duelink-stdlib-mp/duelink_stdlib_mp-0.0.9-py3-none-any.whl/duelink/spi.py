

class SpiController:
    def __init__(self, serialPort, stream):
        self.transport = serialPort
        self.stream = stream

    def Configuration(self, mode, frequency)->bool:                    
        cmd = f"spicfg({mode}, {frequency})"
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()
        return r
    
    def WriteByte(self, data: int)->int:            
        cmd = f"spiwr({data})"
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()
        if r:            
            try:
                value = int(s)
                return value
            except:
                pass

        return 0


    def WriteRead(self, dataWrite: bytes, dataRead: bytearray) -> bool:
        countWrite = len(dataWrite)
        countRead = len(dataRead)
        written = 0
        read = 0
        

        # declare b9 to write
        if countWrite > 0:    
            cmd = f"dim b9[{countWrite}]"
            self.transport.WriteCommand(cmd)
            self.transport.ReadResponse()

        # declare b8 to read
        if countRead > 0:
            cmd = f"dim b8[{countRead}]"
            self.transport.WriteCommand(cmd)
            self.transport.ReadResponse()

        # write data to b9 by stream
        if countWrite > 0:    
            written = self.stream.WriteBytes("b9", dataWrite)

        # issue spi cmd
        if countWrite > 0 and countRead > 0:
            cmd = f"SpiWrs(b9, b8)"
        elif countWrite > 0:
            cmd = f"SpiWrs(b9, 0)"
        else:
            cmd = f"SpiWrs(0, b8)"

        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # use stream to read data to b8
        if countRead > 0:
            read = self.stream.ReadBytes("b8", dataRead)

        # return true since we can't check status if Asio(1)
        return (written == countWrite) and (read == countRead)

    
    
    

