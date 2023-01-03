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

from xml.dom.minidom import *


class SvgDoc(object):

    # construct a document with an owning Diagram plus a given width and height
    def __init__(self,width,height,units,viewbox_width,viewbox_height):

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
    def add(self,obj):
        self.objects.append(obj)
        return self

    def construct(self):
        self.doc = Document()
        self.root = self.doc.createElement("svg")
        self.root.setAttribute("xmlns","http://www.w3.org/2000/svg")
        self.root.setAttribute("xmlns:xlink","http://www.w3.org/1999/xlink")
        self.defs = self.doc.createElement("defs")
        self.root.appendChild(self.defs)


        self.root.setAttribute("xmlns:svg","http://www.w3.org/2000/svg")
        self.root.setAttribute("xmlns","http://www.w3.org/2000/svg")
        self.root.setAttribute("width","%s%s"%(str(self.width),str(self.units)))
        self.root.setAttribute("height", "%s%s" % (str(self.height),str(self.units)))
        self.root.setAttribute("viewBox", "%d %d %d %d"%(0,0,self.viewbox_width,self.viewbox_height))
        self.root.setAttribute("preserveAspectRatio","xMidYMin meet")
        self.root.setAttribute("version", "1.1")

        # add the objects
        for o in self.objects:
            o.render(self,self.root)

        self.doc.appendChild(self.root)
        return self.doc
        
    def render(self):
        doc = self.construct()
        xml = doc.toprettyxml(encoding="utf-8").decode("utf-8")
        return xml

