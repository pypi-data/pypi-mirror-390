import time
import struct
class StreamController:    

    def __init__(self, serialPort):
        self.transport = serialPort        

    def WriteSpi(self, dataWrite: bytes)->int:
        count = len(dataWrite)

        cmd = f"strmspi({count})"        
        self.transport.WriteCommand(cmd)
        
        # wait for prompt &
        prompt = 0
        while True:            
            data = self.transport.ReadByte()
            if data[0] == ord('&'):
                prompt = data[0]
                break
        
        if prompt != ord('&'):
            raise Exception("Invalid or no responses")
        
        # ready to write data
        self.transport.WriteRawData(dataWrite,0, count)
        
        # read x\r\n>
        r,s = self.transport.ReadResponse()
        
        if r == True:
            try:
                return int(s)
            except:
                return 0                
        
        return 0
    
    def WriteBytes(self, arr: str, dataWrite: bytes)->int:
        count = len(dataWrite)

        # declare b1 array
        cmd = f"strmwr({arr},{count})"       
        self.transport.WriteCommand(cmd)
        
        # wait for prompt &
        prompt = 0
        startms = time.ticks_ms()
        while (time.ticks_ms() - startms < self.transport.ReadTimeout):            
            data = self.transport.ReadByte()
            if data != None and data[0] == ord('&'):
                prompt = data[0]
                break
            
            
        
        if prompt != ord('&'):
            raise Exception("Invalid or no responses")
        
        # ready to write data
        self.transport.WriteRawData(dataWrite,0, count)
        
        # read x\r\n>
        r,s = self.transport.ReadResponse()
        if r == True:
            try:
                return int(s)
            except:
                return 0                
        
        return 0
    
    def ReadBytes(self, arr: str, dataRead: bytes):
        if dataRead is None or dataRead == 0:
            return 0
        count = len(dataRead)

        # declare b1 array
        cmd = f"strmrd({arr},{count})"
        self.transport.WriteCommand(cmd)

        # wait for prompt &
        prompt = 0
        startms = time.ticks_ms()
        while (time.ticks_ms() - startms < self.transport.ReadTimeout):            
            data = self.transport.ReadByte()
            if data != None and data[0] == ord('&'):
                prompt = data[0]
                break
        
        if prompt != ord('&'):
            raise Exception("Invalid or no responses")
        
        # ready to read data
        self.transport.ReadRawData(dataRead,0, count)

        # read x\r\n> (asio(1) not return this)
        r,s = self.transport.ReadResponse()
        
        if r == True:
            try:
                return int(s)
            except:
                return 0                
        
        return 0
    
    def WriteFloats(self, arr: str, dataWrite: float):
        if dataWrite is None or dataWrite == 0:
            return 0
        count = len(dataWrite)

        # declare b1 array
        cmd = f"strmwr({arr},{count})"
        self.transport.WriteCommand(cmd)

        # wait for prompt &
        prompt = 0
        startms = time.ticks_ms()
        while (time.ticks_ms() - startms < self.transport.ReadTimeout):            
            time.sleep(0.001)
            data = self.transport.ReadByte()
            if data != None and data[0] == ord('&'):
                prompt = data[0]
                break

        if prompt != ord('&'):
            raise Exception("Invalid or no responses")
        
        # ready to write data
        for i in range (0, count):
            float_bytes = struct.pack('>f', dataWrite[i])
            #float_bytes_lsb = float_bytes[::-1]
            float_bytes_lsb = bytes([float_bytes[3],float_bytes[2],float_bytes[1],float_bytes[0]])
              
            self.transport.WriteRawData(float_bytes_lsb,0, 4)        

        # read x\r\n>
        r,s = self.transport.ReadResponse()
        if r == True:
            try:
                return int(s)
            except:
                return 0                
        
        return 0
    
    def ReadFloats(self, arr: str, dataRead: float):
        if dataRead is None or dataRead == 0:
            return 0
        count = len(dataRead)

        # declare b1 array
        cmd = f"strmrd({arr},{count})"
        self.transport.WriteCommand(cmd)

        # wait for prompt &
        prompt = 0
        startms = time.ticks_ms()
        while (time.ticks_ms() - startms < self.transport.ReadTimeout):            
            time.sleep(0.001)
            data = self.transport.ReadByte()
            if data != None and data[0] == ord('&'):
                prompt = data[0]
                break

        if prompt != ord('&'):
            raise Exception("Invalid or no responses")
        
        # ready to read data
        raw_bytes = bytearray(4)
        for i in range (0, count):
            self.transport.ReadRawData(raw_bytes,0, 4)
            #raw_bytes_lsb = bytes([raw_bytes[3],raw_bytes[2],raw_bytes[1],raw_bytes[0]])
            dataRead[i] = struct.unpack('f', raw_bytes)[0]        

        # read x\r\n>
        r,s = self.transport.ReadResponse()
        if r == True:
            try:
                return int(s)
            except:
                return 0                
        
        return 0
        
            
            
            
            
            
            
            
        
    