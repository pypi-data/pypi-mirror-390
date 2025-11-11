import machine
import time

from duelink.analog import AnalogController
from duelink.button import ButtonController
from duelink.digital import DigitalController
from duelink.graphics import GraphicsController
from duelink.distancesensor import DistanceSensorController
from duelink.frequency import FrequencyController
from duelink.i2c import I2cController
from duelink.infrared import InfraredController
from duelink.system import SystemController
from duelink.servo import ServoController
from duelink.spi import SpiController
from duelink.engine import EngineController
from duelink.deviceconfiguration import DeviceConfiguration
from duelink.temperature import TemperatureController
from duelink.humidity import HudimityController
from duelink.sound import SoundController
from duelink.temperature import TemperatureSensorType
from duelink.humidity import HumiditySensorType
from duelink.stream import StreamController
from duelink.dmx import DMXController
from duelink.filesystem import FileSystemController
from duelink.otp import OtpController
from duelink.pulse import PulseController
from duelink.rtc import RtcController
from duelink.uart import UartController

   
class DUELinkController:
    def __init__(self, serialPort):
        self.transport = serialPort
        self.Stream = StreamController(self.transport)
        self.Analog = AnalogController(self.transport)
        self.Digital = DigitalController(self.transport)        
        self.Servo = ServoController(self.transport)
        self.Frequency = FrequencyController(self.transport)        
        self.Infrared = InfraredController(self.transport)
        self.Button = ButtonController(self.transport)
        self.Distance = DistanceSensorController(self.transport)        
        self.Engine = EngineController(self.transport)
        self.Temperature = TemperatureController(self.transport)
        self.Humidity = HudimityController(self.transport)
        self.System = SystemController(self.transport)                        
        self.TemperatureSensorType = TemperatureSensorType()
        self.HumiditySensorType = HumiditySensorType()       
        self.Pulse = PulseController(self.transport)        
        
        self.DMX = DMXController(self.transport,self.Stream)
        self.FileSystem = FileSystemController(self.transport,self.Stream)
        self.Otp = OtpController(self.transport,self.Stream)        
        self.Rtc = RtcController(self.transport,self.Stream)
        self.I2c = I2cController(self.transport,self.Stream)
        self.Spi = SpiController(self.transport,self.Stream)
        self.Uart = UartController(self.transport,self.Stream)
        self.Sound = SoundController(self.transport,self.Stream)
        self.Graphics = GraphicsController(self.transport,self.Stream)
        
    
    def __get_ReadTimeout(self):
        return self.transport.ReadTimeout

    def __set_ReadTimeout(self, value: int):
        self.transport.ReadTimeout = value 

    ReadTimeout = property(__get_ReadTimeout, __set_ReadTimeout)
    
    
    


