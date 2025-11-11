

class EngineController:
    def __init__(self, serialPort):
        self.transport = serialPort
        self.loadscript = ""    
    
    def Record(self, script,region) -> bool:
        if region == 0:
            self.transport.WriteCommand("new all")  
            r,s = self.transport.ReadResponse() 
            if r == False:
                return False
        elif region == 1:
            self.transport.WriteCommand("region(1)")  
            r,s = self.transport.ReadResponse() 
            if r == False:
                return False
            
            self.transport.WriteCommand("new")  
            r,s = self.transport.ReadResponse() 
            if r == False:
                return False
        else:
            return False
               
        cmd = "pgmbrst()"

        raw = script.encode('ASCII')

        data = bytearray(len(raw) + 1)

        data[len(raw)] = 0

        data[0:len(raw)] = raw        

        self.transport.WriteCommand(cmd)

        r,s = self.transport.ReadResponse()

        if (r == False) :
            return False
        
        self.transport.WriteRawData(data, 0, len(data))

        r,s = self.transport.ReadResponse()

        return r
            
    def Read(self) -> str:
        cmd = "list"

        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponseRaw()

        return s   
    
    def Run(self) -> str:
        self.transport.WriteCommand("run")        
        r,s = self.transport.ReadResponse()        
        return s
    
    def Stop(self) -> str:                
        data = bytearray(1)
        data[0] = 27
        self.transport.WriteRawData(data, 0, len(data))
        
        res = self.transport.ReadResponse()

        return res.response
    
    def New(self):
        self.transport.WriteCommand(f"new")        
        r,s = self.transport.ReadResponse()           
        return r

    def Select(self, num):
        cmd = f"sel({num})"
        self.transport.WriteCommand(cmd)
        
        r,s = self.transport.ReadResponse()
        
        return r
    
    def ExecuteCommand(self, cmd:str) -> float:
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        if r:
            try:
                return float(s)
            except:
                pass

        return 0
    
    def ExecuteCommandRaw(self, cmd:str):
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        return s
        
        


       