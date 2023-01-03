# -*- coding: utf-8 -*-

from .webcolours import colours

class HueException(Exception):

    def __init__(self,msg):
        super().__init__(msg)

class Hue(object):

    webHues = { col["name"].lower():"#"+col["hex"] for col in colours }

    def __init__(self,min_value=None,max_value=None,defaultHue="red",colors=["black","white"]):
        self.min_value = min_value
        self.max_value = max_value
        self.default_hue = Hue.toHEX(defaultHue)
        self.rgbas = [self.parseHue(color) for color in colors]
        self.value_interval = (max_value - min_value) / (len(self.rgbas)-1)

    @staticmethod
    def parseHue(col):
        if not isinstance(col,str):
            raise HueException("Unable to parse hue from non-string (%s)" % (str(col)))
        if col and (len(col) != 7 or col[0] != "#"):
            if col.lower() in Hue.webHues:
                col = Hue.webHues[col.lower()]
        if not col or col[0] != "#" or (len(col) != 7 and len(col) != 9):
            raise HueException("Unable to parse hue (%s)"%(col))
        r = int(col[1:3],16)
        g = int(col[3:5],16)
        b = int(col[5:7],16)
        a = 255 if len(col) == 7 else int(col[7:9],16)
        return (r,g,b,a)

    def computeHue(self,col1,col2,frac):
        r = col1[0]+int(frac*(col2[0]-col1[0]))
        g = col1[1]+int(frac*(col2[1]-col1[1]))
        b = col1[2]+int(frac*(col2[2]-col1[2]))
        a = col1[3] + int(frac * (col2[3] - col1[3]))
        return (r,g,b,a)

    @staticmethod
    def toHEX(hue):
        if hue is None:
            return None
        return Hue.rgb2hue(Hue.parseHue(hue))
    
    @staticmethod
    def rgb2hue(rgba):
        (r,g,b,a) = rgba
        return "#%02X%02X%02X" % (r, g, b)

    def getDefaultHue(self):
        return self.defaultHue

    @staticmethod
    def applyOpacity(hue,opacity):
        if opacity < 1.0:
            (r,g,b,a) = Hue.parseHue(hue)
            return "#%02X%02X%02X%02X"%(r,g,b,round(opacity*255))
        else:
            return hue


    def getHue(self,val):
        if val < self.min_value:
            return self.default_hue
        if val > self.max_value:
            return self.default_hue
        idx = int((val - self.min_value)/self.value_interval)
        if idx > len(self.rgbas)-2:
            idx = len(self.rgbas)-2
        col1 = self.rgbas[idx]
        col2 = self.rgbas[idx+1]
        frac = (val - self.min_value+idx*self.value_interval) / self.value_interval
        return self.computeHue(col1,col2,frac)





