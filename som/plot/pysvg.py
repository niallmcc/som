# MIT License
#
# Copyright (c) 2022-2023 Niall McCarroll
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# base class for SVG objects, holding style information and handing rendering

from math import pi, cos, sin
from .webcolours import colours
from xml.dom.minidom import *

class SvgStyled(object):

    idcounter = 0

    def __init__(self,tag,tooltip=""):
        self.tag = tag
        self.style = {}
        self.attrs = {}
        self.tooltip = tooltip
        self.content = ''
        self.children = []

    def addChild(self,ele):
        self.children.append(ele)

    # add an SVG attribute
    def addAttr(self,name,value):
        if name == "fill" or name == "stroke":
            # SVG standard does not support alpha channel in fill/stroke
            # so intercept here and ad fill-opacity and stroke-opacity
            if len(value)>0 and value[0] == "#":
                alpha = 1
                if len(value) == 9: # "#RRGGBBAA"
                    a = int(value[7:9],16)
                    alpha = a/255
                    value=value[:7]
                elif len(value) == 5: # "#RBGA"
                    a = int(value[4:5],16)
                    alpha = a/15
                    value=value[:4]
                if alpha < 1:
                    if name == "fill":
                        self.attrs["fill-opacity"] = alpha
                    else:
                        self.attrs["stroke-opacity"] = alpha

        self.attrs[name] = value
        return self

    def getAttr(self,name):
        return self.attrs[name]

    # add multiple SVG attributes
    def addAttrs(self,attrs):
        if attrs:
            for k in attrs:
                self.addAttr(k,attrs[k])
        return self

    # set the XML content of the element
    def setContent(self,content):
        self.content = content
        return self

    # construct the style attribute
    def getStyleAttr(self):
        keys = self.style.keys()
        s = ''
        if len(keys):
            for k in keys:
                s += k + ":" + str(self.style[k])+";"
        return s

    # set the tooltp
    def setTooltip(self,tooltip):
        self.tooltip = tooltip

    def render(self,svgdoc,parent):
        doc = svgdoc.doc
        if self.tooltip:
            g = doc.createElement("g")
            title = doc.createElement("title")
            title.appendChild(doc.createTextNode(self.tooltip))
            g.appendChild(title)
            parent.appendChild(g)
            parent = g

        e = doc.createElement(self.tag)
        for name in self.attrs:
            e.setAttribute(name,str(self.attrs[name]))

        style = self.getStyleAttr()
        if style:
            e.setAttribute("style",style)

        parent.appendChild(e)

        if self.content != '':
            e.appendChild(doc.createTextNode(str(self.content)))

        for child in self.children:
            e.appendChild(child)
        return e

# represent a section of text as an SVG object
class Text(SvgStyled):

    def __init__(self,x,y,txt,tooltip="",font_height=12,text_attributes={},max_length=None):
        super().__init__("text",tooltip)
        self.x = x
        self.y = y
        self.txt = txt
        self.addAttr("x",x).addAttr("y",y).setContent(txt)
        self.addAttr("text-anchor", "middle")
        self.rotation = None
        self.font_height = font_height
        self.text_attributes = text_attributes
        self.vertical_center = False
        self.horizontal_center = True
        self.label_margin = 5
        self.max_length = max_length

    def setRotation(self,radians):
        self.rotation = 360*radians/(2*pi)
        self.addAttr("transform","rotate(%f,%f,%f)"%(self.rotation,self.x,self.y))
        return self

    def setVerticalCenter(self, center=True):
        self.vertical_center = center
        if center:
            self.addAttr("dominant-baseline", "middle")
        else:
            self.addAttr("dominant-baseline", "top")
        return self

    def setHorizontalCenter(self, center=True):
        self.horizontal_center = center
        if center:
            self.addAttr("text-anchor", "middle")
        else:
            self.addAttr("text-anchor", "start")
        return self

    def render(self, svgdoc, parent):

        if self.text_attributes:
            self.addAttrs(self.text_attributes)

        font_height = self.font_height

        self.addAttr("font-size", font_height)

        return super().render(svgdoc, parent)

# represent a circle as an SVG object
class Circle(SvgStyled):

    def __init__(self,x,y,r,fill="grey",tooltip="",stroke=None,stroke_width=None):
        super().__init__('circle',tooltip)
        self.addAttr("cx",x).addAttr("cy",y).addAttr("r",r)
        if fill:
            self.addAttr("fill",fill)
        if stroke:
            self.addAttr("stroke",stroke)
        if stroke_width != None:
            self.addAttr("stroke-width",stroke_width)

class Polygon(SvgStyled):

    def __init__(self,path,fill=None,stroke="black",stroke_width=1,tooltip="",innerpaths=[]):
        super().__init__("path",tooltip)
        s = self.buildPath(path)

        if innerpaths:
            self.addAttr("fill-rule","evenodd")
            for path in innerpaths:
                s += " "
                s += self.buildPath(path)

        self.addAttr("d",s)

        if fill:
            self.addAttr("fill",fill)
        else:
            self.addAttr("fill","none")
        if stroke and stroke_width:
            self.addAttr("stroke-width",stroke_width).addAttr("stroke",stroke)

    def buildPath(self,points):
        s = 'M'
        sep = ''
        for p in points:
            if len(p) == 1:
                s += " "+p[0]
                continue
            (x,y) = p
            s += sep
            sep = ' '
            s += str(x)+" "+str(y)
        s += 'Z'
        return s

class Rectangle(SvgStyled):

    def __init__(self,x,y,width,height,fill=None,stroke=None,stroke_width=None,rx=None, ry=None, tooltip=""):
        super().__init__("rect",tooltip)
        self.addAttr("x",x)
        self.addAttr("y",y)
        self.addAttr("width",width)
        self.addAttr("height",height)
        if fill:
            self.addAttr("fill",fill)
        else:
            self.addAttr("fill","none")
        if stroke:
            self.addAttr("stroke",stroke)
        if stroke_width:
            self.addAttr("stroke-width",stroke_width)
        if rx:
            self.addAttr("rx",rx)
        if ry:
            self.addAttr("ry",ry)


class Hexagon(Polygon):

    def __init__(self,x,y,dlength,fill,stroke,stroke_width):
        points = []

        r = 0
        for idx in range(0,6):
            py = y+dlength*cos(r)
            px = x+dlength*sin(r)
            points.append((px,py))
            r += pi/3

        self.hexpoints = points
        super().__init__(points,fill,stroke,stroke_width)





class Hue(object):
    webHues = {col["name"].lower(): "#" + col["hex"] for col in colours}

    def __init__(self, min_value=None, max_value=None, defaultHue="red", colors=["black", "white"]):
        self.min_value = min_value
        self.max_value = max_value
        self.default_hue = Hue.toHEX(defaultHue)
        self.rgbas = [self.parseHue(color) for color in colors]
        self.value_interval = (max_value - min_value) / (len(self.rgbas) - 1)

    @staticmethod
    def parseHue(col):
        if not isinstance(col, str):
            raise ValueError("Unable to parse hue from non-string (%s)" % (str(col)))
        if col and (len(col) != 7 or col[0] != "#"):
            if col.lower() in Hue.webHues:
                col = Hue.webHues[col.lower()]
        if not col or col[0] != "#" or (len(col) != 7 and len(col) != 9):
            raise ValueError("Unable to parse hue (%s)" % (col))
        r = int(col[1:3], 16)
        g = int(col[3:5], 16)
        b = int(col[5:7], 16)
        a = 255 if len(col) == 7 else int(col[7:9], 16)
        return (r, g, b, a)

    def computeHue(self, col1, col2, frac):
        r = col1[0] + int(frac * (col2[0] - col1[0]))
        g = col1[1] + int(frac * (col2[1] - col1[1]))
        b = col1[2] + int(frac * (col2[2] - col1[2]))
        a = col1[3] + int(frac * (col2[3] - col1[3]))
        return (r, g, b, a)

    @staticmethod
    def toHEX(hue):
        if hue is None:
            return None
        return Hue.rgb2hue(Hue.parseHue(hue))

    @staticmethod
    def rgb2hue(rgba):
        (r, g, b, a) = rgba
        return "#%02X%02X%02X" % (r, g, b)

    def getDefaultHue(self):
        return self.defaultHue

    @staticmethod
    def applyOpacity(hue, opacity):
        if opacity < 1.0:
            (r, g, b, a) = Hue.parseHue(hue)
            return "#%02X%02X%02X%02X" % (r, g, b, round(opacity * 255))
        else:
            return hue

    def getHue(self, val):
        if val < self.min_value:
            val = self.min_value
        if val > self.max_value:
            val = self.max_value
        idx = int((val - self.min_value) / self.value_interval)
        if idx > len(self.rgbas) - 2:
            idx = len(self.rgbas) - 2
        col1 = self.rgbas[idx]
        col2 = self.rgbas[idx + 1]
        frac = (val - self.min_value + idx * self.value_interval) / self.value_interval
        return self.computeHue(col1, col2, frac)


class SvgDoc(object):

    # construct a document with an owning Diagram plus a given width and height
    def __init__(self, width, height, units, viewbox_width, viewbox_height):
        self.objects = []

        self.width = width
        self.height = height
        self.units = units
        self.viewbox_width = viewbox_width
        self.viewbox_height = viewbox_height

        self.doc = None

    def getDoc(self):
        return self.doc

    # add an object to the document (obj inherits from svgstyled)
    def add(self, obj):
        self.objects.append(obj)
        return self

    def construct(self):
        self.doc = Document()
        self.root = self.doc.createElement("svg")
        self.root.setAttribute("xmlns", "http://www.w3.org/2000/svg")
        self.root.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink")
        self.defs = self.doc.createElement("defs")
        self.root.appendChild(self.defs)

        self.root.setAttribute("xmlns:svg", "http://www.w3.org/2000/svg")
        self.root.setAttribute("xmlns", "http://www.w3.org/2000/svg")
        self.root.setAttribute("width", "%s%s" % (str(self.width), str(self.units)))
        self.root.setAttribute("height", "%s%s" % (str(self.height), str(self.units)))
        self.root.setAttribute("viewBox", "%d %d %d %d" % (0, 0, self.viewbox_width, self.viewbox_height))
        self.root.setAttribute("preserveAspectRatio", "xMidYMin meet")
        self.root.setAttribute("version", "1.1")

        # add the objects
        for o in self.objects:
            o.render(self, self.root)

        self.doc.appendChild(self.root)
        return self.doc

    def render(self):
        doc = self.construct()
        xml = doc.toprettyxml(encoding="utf-8").decode("utf-8")
        return xml

