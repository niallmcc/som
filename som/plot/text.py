# MIT License
#
# Copyright (c) 2022 Niall McCarroll
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

from math import pi


from .svgstyled import SvgStyled

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

    def setVerticalCenter(self,center=True):
        self.vertical_center = center
        if center:
            self.addAttr("dominant-baseline","middle")
        else:
            self.addAttr("dominant-baseline","top")
        return self

    def setHorizontalCenter(self,center=True):
        self.horizontal_center = center
        if center:
            self.addAttr("text-anchor","middle")
        else:
            self.addAttr("text-anchor","start")
        return self

    def render(self,svgdoc,parent):

        if self.text_attributes:
            self.addAttrs(self.text_attributes)

        font_height = self.font_height

        self.addAttr("font-size",font_height)

        return super().render(svgdoc, parent)
        
    