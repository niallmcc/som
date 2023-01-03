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

# base class for SVG objects, holding style information and handing rendering
class SvgStyled(object):

    idcounter = 0

    def __init__(self,tag,tooltip=""):
        self.tag = tag
        self.style = {}
        self.attrs = {}
        self.tooltip = tooltip
        self.content = ''
        self.handlers = {}
        self.children = []
        self.animations = []
        self.id = ""


    def setId(self,eid=None):
        if eid:
            self.id = eid
        else:
            svgstyled.idcounter += 1
            self.id = "s"+str(svgstyled.idcounter)
        return self.id

    def getId(self):
        if self.id == "":
            return self.setId()
        else:
            return self.id

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

    # add an animation
    def addAnimation(self,propertyName,fromValue,toValue,durationSecs):
        self.animations.append((propertyName,fromValue,toValue,durationSecs))

    def getAttr(self,name):
        return self.attrs[name]

    # add multiple SVG attributes
    def addAttrs(self,attrs):
        if attrs:
            for k in attrs:
                self.addAttr(k,attrs[k])
        return self

    # add a handler
    def addHandler(self,evt,fname):
        self.handlers[evt] = fname

    # get handler if defined
    def getHandler(self,evt):
        if evt in self.handlers:
            return self.handlers[evt]
        return None

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

        for evt in self.handlers:
            fname = self.handlers[evt]
            e.setAttribute("on"+evt,"return "+fname+"(evt);")

        style = self.getStyleAttr()
        if style:
            e.setAttribute("style",style)

        parent.appendChild(e)

        if self.content != '':
            e.appendChild(doc.createTextNode(str(self.content)))

        for child in self.children:
            e.appendChild(child)

        for animation in self.animations:
            (propertyName,fromValue,toValue,durationSecs) = animation
            a = doc.createElement("animate")
            a.setAttribute("attributeType","XML");
            a.setAttribute("attributeName",propertyName)
            a.setAttribute("from",str(fromValue))
            a.setAttribute("to",str(toValue))
            a.setAttribute("dur",str(durationSecs)+"s")
            a.setAttribute("repeatCount","indefinite")
            e.appendChild(a)

        if self.id:
            e.setAttribute("id",self.id)
        return e
