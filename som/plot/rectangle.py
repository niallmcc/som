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

from .svgstyled import SvgStyled

# represent a rectangle as an SVG object
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
