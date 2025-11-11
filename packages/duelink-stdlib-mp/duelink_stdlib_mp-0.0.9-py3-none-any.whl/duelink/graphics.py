import duelink as DL

class GraphicsType:
    I2c = 1
    Spi = 2
    Neo = 3
    Matrix5x5 = 4
    
class GraphicsController:
    def __init__(self, serialPort, stream):
        self.transport = serialPort
        self.stream = stream

    def Configuration(self, type, config, width, height, mode):
        #cfg_array = "{"
        #for n in config:
        #    if len(cfg_array)>1:
        #        cfg_array = cfg_array + ","
        #    cfg_array = cfg_array + str(n)
        #cfg_array = cfg_array + "}"
        
        # declare a9 array
        count = len(config)
        # declare a9 array
        cmd = f"dim a9[{count}]"
        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        # write data to a9
        ret = self.stream.WriteFloats("a9",config)
        
        cmd = f"gfxcfg({type},a9,{width},{height},{mode})"
        
        self.transport.WriteCommand(cmd)        
        r,s = self.transport.ReadResponse()

        return r
    
    def Show(self):
        cmd = "show()"
        self.transport.WriteCommand(cmd)
        
        r,s = self.transport.ReadResponse()

        return r
    
    def Clear(self, color):
        cmd =f"clear({color})"
        self.transport.WriteCommand(cmd)        
        r,s = self.transport.ReadResponse()

        return r
    
    def Pixel(self, color, x, y):
        cmd =f"pixel({color},{x},{y})"
        self.transport.WriteCommand(cmd)        
        r,s = self.transport.ReadResponse()

        return r

    
    def Circle(self, color, x, y, r):
        cmd =f"circle({color},{x},{y},{r})"
        self.transport.WriteCommand(cmd)        
        r,s = self.transport.ReadResponse()

        return r

    
    def Rect(self, color, x, y, w, h):
        cmd =f"rect({color},{x},{y},{w},{h})"
        self.transport.WriteCommand(cmd)        
        r,s = self.transport.ReadResponse()

        return r

    
    def Fill(self, color, x, y, w, h):
        cmd =f"fill({color},{x},{y},{w},{h})"
        self.transport.WriteCommand(cmd)        
        r,s = self.transport.ReadResponse()

        return r

    
    def Line(self, color, x1, y1, x2, y2):
        cmd =f"line({color},{x1},{y1},{x2},{y2})"
        self.transport.WriteCommand(cmd)        
        r,s = self.transport.ReadResponse()

        return r

        
    def Text(self, text, color, x, y):
        cmd =f"text(\"{text}\",{color},{x},{y})"
        self.transport.WriteCommand(cmd)        
        r,s = self.transport.ReadResponse()

        return r

        
    def TextS(self, text, color, x, y, sx, sy):
        cmd =f"texts(\"{text}\",{color},{x},{y},{sx},{sy})"
        self.transport.WriteCommand(cmd)        
        r,s = self.transport.ReadResponse()

        return r

    
    def TextT(self, text, color, x, y):
        cmd =f"textt(\"{text}\",{color},{x},{y})"
        self.transport.WriteCommand(cmd)        
        r,s = self.transport.ReadResponse()

        return r

    
    def DrawImage(self, img, x, y, w, h, transform):
        return self.DrawImageScale(img, x, y, w, h, transform, 1, 1)
    
    def DrawImageScale(self, img, x, y, w, h, transform, sw, sh):
        if (img is None or w<=0 or h<=0):
            raise Exception("Invalid argument")
        #img_arr = ""
        #if isinstance(img, (list)):
        #    img_arr = DL.build_floatarray(img)
        #elif isinstance(img, str):
        #    img_arr = img
        #else:
        #    t = type(img)
        #    raise Exception("Invalid image type '{t}'")
        
        #cmd =f"imgs({img_arr},{x},{y},{w},{h},{sx},{sy},{transform})"
        #self.transport.WriteCommand(cmd)        
        #r,s = self.transport.ReadResponse()

        #return r
        cmd = f"dim a9[{len(img)}]"

        self.transport.WriteCommand(cmd)
        self.transport.ReadResponse()

        written = self.stream.WriteFloats("a9", img)

        
        cmd = f"imgs(a9, {x}, {y}, {w}, {h}, {transform}, {sw}, {sh})"

        self.transport.WriteCommand(cmd)
        r,s = self.transport.ReadResponse()
        
        return r

            