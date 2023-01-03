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

import math

from som.plot.svgdoc import SvgDoc
from som.plot.rectangle import Rectangle
from som.plot.hexagon import Hexagon
from som.plot.text import Text
from som.plot.circle import Circle
from som.plot.hue import Hue

class Plot:

    SCALE=100

    """
    Plot the SOM assignment in a dataset
    """
    def __init__(self, dataset, label_name="pattern_label", som_name="som_assignment",
                 cell_x_name="cell_centres_x", cell_y_name="cell_centres_y",
                 color_name="freq", colors=["yellow","red"], color_value_min=None, color_value_max=None,
                 default_color="#A0A0A0"):

        self.ds = dataset
        self.label_name = label_name
        self.som_name = som_name
        self.cell_x_name = cell_x_name
        self.cell_y_name = cell_y_name
        self.grid_width = self.ds[som_name].attrs["grid_width"]
        self.grid_height = self.ds[som_name].attrs["grid_height"]
        self.layout = self.ds[som_name].attrs["layout"]
        self.num_cases = self.ds[label_name].data.shape[0]
        self.color_name = color_name
        self.colors  = colors
        self.color_value_min = color_value_min
        self.color_value_max = color_value_max
        self.default_color = default_color


    def plot(self, path):
        width = (self.grid_width+3)*Plot.SCALE
        height = (self.grid_height+1)*Plot.SCALE
        doc = SvgDoc(width,height,"px",width,height)
        centres_x = self.ds[self.cell_x_name]
        centres_y = self.ds[self.cell_y_name]

        indexes_by_position = {}
        som = self.ds[self.som_name]
        labels = self.ds[self.label_name] if self.label_name else None

        max_freq = 0
        for idx in range(self.num_cases):
            grid_x = int(som[idx,0].data)
            grid_y = int(som[idx,1].data)
            key = (grid_x,grid_y)
            if key not in indexes_by_position:
                indexes_by_position[key] = []
            indexes_by_position[key].append(idx)
            if len(indexes_by_position[key]) > max_freq:
                max_freq = len(indexes_by_position[key])

        if self.color_name:
            if self.color_name == "freq":
                # colour by frequencies
                if self.color_value_min is None:
                    self.color_value_min = 0
                if self.color_value_max is None:
                    self.color_value_max = 0
            else:
                if self.color_value_min is None:
                    self.color_value_min = self.ds[self.color_name].min().data
                if self.color_value_max is None:
                    self.color_value_max = self.ds[self.color_name].max().data

            hue = Hue(self.color_value_min, self.color_value_max, defaultHue=self.default_color, colors=self.colors)
        else:
            hue = None

        cell_colors = {}
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                key = (x,y)
                if hue is not None and key in indexes_by_position:
                    if self.color_name=="freq":
                        (r,g,b,a) = hue.getHue(len(indexes_by_position[key]))
                        cell_colors[key] = f"rgb({r},{g},{b})"
                    else:
                        value_sum = 0
                        for idx in indexes_by_position[key]:
                            value_sum += self.ds[self.color_name][idx].data
                        value = value_sum / len(indexes_by_position[key])
                        (r, g, b, a) = hue.getHue(value)
                        cell_colors[key] = f"rgb({r},{g},{b})"
                else:
                    cell_colors[key] = self.default_color

        if self.layout == "square":
            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    cx = centres_x[x,y].data
                    cy = centres_y[x,y].data
                    key = (x,y)
                    cell = Rectangle((cx-0.5)*Plot.SCALE,(cy-0.5)*Plot.SCALE,Plot.SCALE,Plot.SCALE,fill=cell_colors[key],stroke="rgb(0,0,0)",stroke_width=0)
                    doc.add(cell)

        elif self.layout == "hexagonal":
            radius = 0.5/math.cos(math.pi/6)
            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    cx = centres_x[x,y].data
                    cy = centres_y[x,y].data
                    key = (x, y)
                    cell = Hexagon(cx*Plot.SCALE,cy*Plot.SCALE,radius*Plot.SCALE,fill=cell_colors[key],stroke="rgb(0,0,0)",stroke_width=0)
                    doc.add(cell)

        else:
            raise Exception("Invalid layout value: "+self.layout)

        for x in range(self.grid_width):
            for y in range(self.grid_height):
                cx = centres_x[x, y].data
                cy = centres_y[x, y].data
                key = (x,y)
                if key in indexes_by_position:
                    indexes= indexes_by_position[key]
                    radius = 0.3*Plot.SCALE
                    for i in range(len(indexes)):
                        idx = indexes[i]
                        angle = 2 * math.pi * i / len(indexes)
                        xloc = cx * Plot.SCALE + radius *math.cos(angle)
                        yloc = cy * Plot.SCALE + radius *math.sin(angle)
                        fill = "gray"
                        if self.color_name and self.color_name != "freq":
                            (r,g,b,a) = hue.getHue(self.ds[self.color_name][idx].data)
                            fill=f"rgb({r},{g},{b})"
                        doc.add(Circle(xloc, yloc, 0.05 * Plot.SCALE, fill=fill,stroke="black",stroke_width=1))
                        if labels is not None:
                            label = labels[idx].data
                            xloc = cx * Plot.SCALE + radius*1.2 * math.cos(angle)
                            yloc = cy * Plot.SCALE + radius*1.2 * math.sin(angle)
                            doc.add(Text(xloc,yloc,label).setHorizontalCenter(False).setRotation(angle))

        if hue:
            tx = (1.5+self.grid_width)*Plot.SCALE
            ty = 100
            tw = Plot.SCALE*0.5
            th = Plot.SCALE*2
            p = 50
            for idx in range(p):
                value = self.color_value_max - (idx/p)*(self.color_value_max-self.color_value_min)
                (r,g,b,a) = hue.getHue(value)
                y = ty + (idx/p)*th
                x = tx
                w = tw
                h = 1 + (th / p)
                rgb = f"rgb({r},{g},{b})"
                doc.add(Rectangle(x, y, w, h, fill=rgb, stroke="none", stroke_width=0))
            doc.add(Rectangle(tx,ty,tw,th,fill="none",stroke="black", stroke_width=1))
            doc.add(Text(tx+tw*0.5,ty-40,f"{self.color_value_max:0.2f}",font_height=20).setVerticalCenter())
            doc.add(Text(tx+tw*0.5,ty + th + 40, f"{self.color_value_min:0.2f}",font_height=20).setVerticalCenter())

        with open(path,"w") as f:
            f.write(doc.render())

