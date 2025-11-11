
class HumiditySensorType():  
    def __init__(self):
        pass

    def __get_Dht11(self):
        return 1
    def __get_Dht12(self):
        return 2
    def __get_Dht21(self):
        return 3
    def __get_Dht22(self):
        return 4

    def __set_empty(self, value: int):
        return   

    DHT11 = property(__get_Dht11, __set_empty)  
    DHT12 = property(__get_Dht12, __set_empty)  
    DHT21 = property(__get_Dht21, __set_empty)  
    DHT22 = property(__get_Dht22, __set_empty)
    
class HudimityController:
    def __init__(self, serialPort):
        self.transport = serialPort

    def Read(self, pin: int, sensortype: int) -> float:
    
        cmd = f"humid({pin},{sensortype})"
        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()

        if r:
            try:
                return float(s)
            except:
                pass

        return 0 
        
    
    
