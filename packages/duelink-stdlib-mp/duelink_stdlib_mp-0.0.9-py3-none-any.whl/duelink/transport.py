import machine
import time
import struct

class I2CTransportController:
    def __init__(self, sda, scl, i2ccontroller=1, freq=400000, addr=0x52):
        self.i2c = machine.I2C(i2ccontroller, sda = sda, scl = scl, freq=freq)
        self.addr = addr
        self.ReadTimeout = 3000 #ms
        self.TransferBlockSizeMax = 512
        self.TransferBlockDelay = 5 #ms
        #time.sleep(0.2)
        self.sync()
    
    def DiscardInBuffer(self):
        r = self.ReadByte()
        while (r[0] != 255):
            r = self.ReadByte()
            time.sleep(0.001)
            
        
    def sync(self):
        # Synchronize is no longer  send 127 because the device can be host which is runing a loop to control its clients.
        # We jusr send \n as first commands for chain enumeration
        self.i2c.writeto(self.addr, "\n")
        
        time.sleep(0.4)
        
        self.WriteCommand("sel(1)")
        #self.i2c.writeto(self.addr, "sel(1)\n")
        
        
        now = time.ticks_ms()
        end = time.ticks_ms() + self.ReadTimeout
        # dump all sync        
        r = self.ReadByte()
        
        while (r[0] == 255 and now <  end):
            time.sleep(0.001)
            r = self.ReadByte()            
            now = time.ticks_ms()
        
        if (end < time.ticks_ms()):
            raise Exception("Sync device failed.")
        
        # dump all sync
        while (r[0] != 255):
            r = self.ReadByte()
            time.sleep(0.001)
    
        
        #bytes = self.uart.read(3)
        #if bytes is None or len(bytes)<3: # or bytes[2] != 62:
        #    raise Exception("DUELink not responding")
        
        # Sync then discard all bytes
        #if len(bytes)>3:
        #    self.uart.read()
    
    def WriteBytes(self, data):
        self.i2c.writeto(self.addr, data)
        
    def WriteByte(self, b):
        data = bytearray(1)
        data[0] = b
        self.i2c.writeto(self.addr, data)
        
    #def read(self, buf, timeout):
    #    pass
        #startms = time.ticks_ms()
        #bytesToRead = 0;
        #i=0
        #while (time.ticks_ms() - startms < timeout):
        #    bytes = self.i2c.readfrom(self.addr, 1)
        #    if bytes is not None and len(bytes) > 0:
        #        c = bytes[0]
        #        if c >= 0 and c <= 127:
        #            bytesToRead=len(buf)-2
        #            buf[i] = c
        #            i = i + 1
        #            break
        #if bytesToRead > 0 and buf[0] != '>' and buf[0] != '&':
        #    bytes = self.i2c.readfrom(self.addr, bytesToRead)
        #    while (time.ticks_ms() - startms < timeout) and bytesToRead > 0:
        #        for c in bytes:
        #            if c >= 0 and c <= 127:
        #                buf[i] = c
        #                i = i + 1
        #                bytesToRead = bytesToRead - 1
        #                if bytesToRead == 0:
        #                   break
    
    def ReadByte(self):
        data = self.i2c.readfrom(self.addr, 1)
                
        if data is not None and len(data) > 0:
            if data[0] == 254:
                time.sleep(0.001)
                data = self.i2c.readfrom(self.addr, 1)
                data2 = bytearray(1)
                if data[0] == 1:
                    data2[0] = 255
                elif data[0] == 2:
                    data2[0] = 254
                else:
                    raise Exception("Error: special byte 255 detected")
                # return 255 or 254 data
                return data2
            
            # return 255 mean no data, other mean data
            return data
        else:            
            data = bytearray(1)
            data[0] = 255 # no response, just return 255 so mark no data
            return data                    
        
    def WriteCommand(self, command):
        self.DiscardInBuffer()
        self.WriteBytes(command + "\n")
        
    def ReadResponse(self):
        startms = time.ticks_ms()
        str_arr = ""
        total_receviced = 0
        responseValid = True
        dump = 0
        
        while (time.ticks_ms() - startms < self.ReadTimeout):            
            data = self.ReadByte()
               
            if data[0] > 127:
                time.sleep(0.001) # no data available, it is 255 - No data in i2c
                continue
            
            str_arr = str_arr + data.decode("utf-8")
            total_receviced = total_receviced + 1
            
            if data[0] == ord('\n'):
                time.sleep(0.001) # wait 1ms for sure
                dump = self.ReadByte()                
                
                # next byte can be >, &, !, $
                if dump[0] < 255:
                    if dump[0] == ord('>') or dump[0] == ord('!') or dump[0] == ord('$'):
                        time.sleep(0.001) # wait 1ms for sure                        
                        dump = self.ReadByte() # read again
                        if dump[0] < 255:
                            responseValid = False
                    else:
                        # bad data
                        # One cmd send suppose one response, there is no 1234\r\n5678.... this will consider invalid response
                        responseValid = False
                        
                if responseValid == False:                    
                    # dump = 0 # no reset because last dump was read. This is different uart
                    while dump[0] != ord('\n') and time.ticks_ms() - startms < self.ReadTimeout:
                        time.sleep(0.001) # wait 1ms for sure
                        dump = self.ReadByte()
                       
                        if dump[0] == ord('\n'): # \n detected, check next byte
                            time.sleep(0.001) # wait 1ms for sure
                            dump = self.ReadByte()
                            
                            if dump[0] == 255: # after \n if there is no data stop
                                break
                            
                            if dump[0] == ord('>') or dump[0] == ord('!') or dump[0] == ord('$'):
                                time.sleep(0.001) # wait 1ms for sure
                                dump = self.ReadByte()
                                if dump[0] == 255: # after > if there is no data stop
                                    break
                
                if str_arr == "" or len(str_arr) < 2: #reponse valid has to be xxx\r\n or \r\n, mean idx >=2
                    responseValid = False
                elif responseValid == True:
                    if str_arr[len(str_arr)-2] != '\r':
                        responseValid = False
                    else:
                        str_arr = str_arr.replace("\n", "")
                        str_arr = str_arr.replace("\r", "")
                break
            
            startms = time.ticks_ms() #reset timeout after valid data
    
        success = total_receviced > 1 and responseValid == True
        return (success,str_arr)
    
    def ReadResponseRaw(self):
        startms = time.ticks_ms()
        str_arr = ""
        total_receviced = 0                
        
        while (time.ticks_ms() - startms < self.ReadTimeout):            
            data = self.ReadByte()
               
            if data[0] > 127:                
                time.sleep(0.001) # no data available, it is 255 - No data in i2c
                continue
            
            str_arr = str_arr + data.decode("utf-8")
            total_receviced = total_receviced + 1
            
            startms = time.ticks_ms() #reset timeout after valid data
    
        success = total_receviced > 1
        return (success,str_arr)
                    
                    
                    
                
                 
                
            
        #cmdIdx = response.find(command)
        #if cmdIdx == -1:
        #    cmdIdx = 0
        #else:
        #    cmdIdx = len(command)+2 # +2 skip \r\n
        
        #success = response[cmdIdx] != '!'
        #if not success:
        #    cmdIdx = cmdIdx + 1
            
        #if response[cmdIdx] == '>':
        #    return ("", success)
        
        #endIdx = response.find("\r\n>", cmdIdx)
        #if endIdx >= cmdIdx:
        #    return (response[cmdIdx:endIdx], success)
        
        #return ("", success)
               
    def WriteRawData(self, buffer, offset, count):
        block = int(count / self.TransferBlockSizeMax)
        remain = int(count % self.TransferBlockSizeMax)

        idx = offset        
        
        while block > 0:
            self.WriteBytes(buffer[idx:idx + self.TransferBlockSizeMax])
            idx += self.TransferBlockSizeMax
            block = block - 1
            time.sleep(self.TransferBlockDelay/1000.0)

        if remain > 0:
            self.WriteBytes(buffer[idx:idx + remain])
    
    def ReadRawData(self, buffer, offset, count):
        end = time.ticks_ms() + self.ReadTimeout
        totalRead = 0
        i = offset
        
        while time.ticks_ms() < end and totalRead < count:
            time.sleep(0.001) # make sure we have data
            rev = self.ReadByte()
            buffer[i] = rev[0]
            i = i + 1
            totalRead = totalRead + 1

        return totalRead

    
class UartTransportController:
    def __init__(self, id):
        self.ReadTimeout = 3000 #ms
        self.uart = machine.UART(id,115200)
        self.uart.init(115200, bits=8, parity=None, stop=1)        
        self.TransferBlockSizeMax = 512
        self.TransferBlockDelay = 5 #ms
        self.sync()
        
    def DiscardInBuffer(self):        
        #self.uart.readall()
        while self.uart.any() > 0:
            dump = self.ReadByte()    
        
    def sync(self):
        # Synchronize is no longer  send 127 because the device can be host which is runing a loop to control its clients.
        # We jusr send \n as first commands for chain enumeration
        self.uart.write('\n')
        
        time.sleep(0.4)
        
        self.WriteCommand("sel(1)")
        
        now = time.ticks_ms()
        end = time.ticks_ms() + self.ReadTimeout
        
        while (self.uart.any() == 0 and now <  end):
            time.sleep(0.001)
            r = self.ReadByte()            
            now = time.ticks_ms()
        
        if (end < time.ticks_ms()):
            raise Exception("Sync device failed.")
        
        # dump all sync
        self.DiscardInBuffer()      
    
    #def write(self, str):
    #    self.uart.write(str+"\n")
    #    
    #def read(self, buf, timeout):
    #    pass           
    
    #def execute(self, command):
    #    buf = bytearray(128)
    #    self.write(command)
    #    #self.read(buf, 100000)
    #    return self.__getResponse(command, buf.decode("utf-8"))
    
    #def streamOutBytes(self, bytes):
    #    buf = bytearray(128)
    #    self.uart.write(bytearray(bytes))
    #    self.read(buf, 1000)
    #    return self.__getResponse("", buf.decode("utf-8"))
    
    #def streamOutFloats(self, floats):
    #    buf = bytearray(128)
    #   for f in floats:
    #       bf = struct.pack("<f",f)            
    #        self.uart.write(bf)   
    #    self.read(buf, 1000)
    #    return self.__getResponse("", buf.decode("utf-8"))
    
    def WriteBytes(self, data):
        self.uart.write(data)
        
    def WriteByte(self, b):
        data = bytearray(1)
        data[0] = b
        self.uart.write(data)        
    
    def ReadByte(self):
        data = self.uart.read(1) 
        return data
    
    def WriteRawData(self, buffer, offset, count):
        block = int(count / self.TransferBlockSizeMax)
        remain = int(count % self.TransferBlockSizeMax)

        idx = offset        
        
        while block > 0:
            self.WriteBytes(buffer[idx:idx + self.TransferBlockSizeMax])
            idx += self.TransferBlockSizeMax
            block -= 1
            time.sleep(self.TransferBlockDelay/1000.0)

        if remain > 0:
            self.WriteBytes(buffer[idx:idx + remain])
    
    def ReadRawData(self, buffer, offset, count):
        end = time.ticks_ms() + self.ReadTimeout
        totalRead = 0
        i = offset
        
        while time.ticks_ms() < end and totalRead < count:
            time.sleep(0.001) # make sure we have data
            rev = self.ReadByte()
            buffer[i] = rev[0]
            i = i + 1
            totalRead = totalRead + 1

            
        return totalRead
        
    def WriteCommand(self, command):
        self.DiscardInBuffer()
        self.WriteBytes(command + "\n")
        
    def ReadResponse(self):        
        startms = time.ticks_ms()
        str_arr = ""
        total_receviced = 0
        responseValid = True
        dump = 0
        
        while (time.ticks_ms() - startms < self.ReadTimeout):            
            if self.uart.any() > 0:
                data = self.uart.read(1)                            
                str_arr = str_arr + data.decode("utf-8")
                
                total_receviced = total_receviced + 1                
                
                if data[0] == ord('\n'):
                    if self.uart.any() == 0:
                        time.sleep(0.001) # wait 1ms for sure
                    
                    # next byte can be >, &, !, $
                    if self.uart.any() > 0: 
                        dump = self.uart.read(1)
                        if dump[0] == ord('>') or dump[0] == ord('!') or dump[0] == ord('$'):
                            time.sleep(0.001) # wait 1ms for sure
                            
                            if self.uart.any() > 0:
                                responseValid = False
                        #elif dump[0] == ord('\r'):#there is case 0\r\n\r\n> if use println("btnup(0)") example, this is valid
                        #    if self.uart.any() == 0:
                        #        time.sleep(0.001) # wait 1ms for sure
                        #        
                        #    if self.uart.any() > 0:
                        #        dump = self.uart.read(1)
                        #        
                        #        if dump[0] == ord('\n'):
                        #            if self.uart.any() > 0:
                        #                dump = self.uart.read(1)
                        #        else:
                        #            responseValid = False
                        #    else:
                        #        responseValid = False
                        else:
                            # bad data
                            # One cmd send suppose one response, there is no 1234\r\n5678.... this will consider invalid response
                            responseValid = False
                            
                    if responseValid == False:
                        d = 0
                        while d != ord('\n') and time.ticks_ms() - startms < self.ReadTimeout:
                            if self.uart.any() > 0:
                                dump = self.uart.read(1)
                                d = dump[0]
                            else:
                                time.sleep(0.001) # wait 1ms for sure
                                
                            if d == ord('\n'):
                                if self.uart.any() > 0: # still bad data, repeat clean up
                                    d = 0 #reset to repeat the condition while loop
                    if str_arr == "" or len(str_arr) < 2: #reponse valid has to be xxx\r\n or \r\n, mean idx >=2
                        responseValid = False
                    elif responseValid == True:
                        if str_arr[len(str_arr)-2] != '\r':
                            responseValid = False
                        else:
                            str_arr = str_arr.replace("\n", "")
                            str_arr = str_arr.replace("\r", "")
                    break
                
                startms = time.ticks_ms() #reset timeout after valid data 
                
        success = total_receviced > 1 and responseValid == True
                
        return (success,str_arr)
    
    def ReadResponseRaw(self):        
        startms = time.ticks_ms()
        str_arr = ""
        total_receviced = 0
        
        while (time.ticks_ms() - startms < self.ReadTimeout):            
            if self.uart.any() > 0:
                data = self.uart.read(1)                            
                str_arr = str_arr + data.decode("utf-8")
                
                total_receviced = total_receviced + 1                                
                startms = time.ticks_ms() #reset timeout after valid data 
                
        success = total_receviced > 1
                
        return (success,str_arr)

                
        
    
