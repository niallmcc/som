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

import xarray as xr
import logging

import math

from som.plot.pysvg import SvgDoc, Rectangle, Hexagon, Text, Circle, Polygon, Hue


class SomPlot:

    SCALE = 100  # each SOM cell will be approximately this wide/high

    """
    Plot the SOM assignment in a dataset
    """

    def __init__(self, dataset, label_name="pattern_label", som_name="som_assignments",
                 cell_x_name="cell_centres_x", cell_y_name="cell_centres_y",
                 color_name="freq", colors=["yellow", "red"], color_value_min=None, color_value_max=None,
                 default_color="#A0A0A0"):

        self.ds = dataset
        self.label_name = label_name
        self.som_name = som_name
        self.cell_x_name = cell_x_name
        self.cell_y_name = cell_y_name
        self.grid_width = self.ds[som_name].attrs["grid_width"]
        self.grid_height = self.ds[som_name].attrs["grid_height"]
        self.layout = self.ds[som_name].attrs["layout"]
        self.num_cases = self.ds[som_name].data.shape[0]
        self.color_name = color_name
        self.colors = colors
        self.color_value_min = color_value_min
        self.color_value_max = color_value_max
        self.default_color = default_color

    def plot(self, path, csv_path=""):
        width = (self.grid_width + 3) * SomPlot.SCALE
        height = (self.grid_height + 1) * SomPlot.SCALE
        doc = SvgDoc(width, height, "px", width, height)
        centres_x = self.ds[self.cell_x_name]
        centres_y = self.ds[self.cell_y_name]

        indexes_by_position = {}
        som = self.ds[self.som_name]
        labels = self.ds[self.label_name] if self.label_name else None

        label_values = {}

        max_freq = 0
        for idx in range(self.num_cases):
            grid_x = int(som[idx, 0].data)
            grid_y = int(som[idx, 1].data)
            key = (grid_x, grid_y)
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
                    self.color_value_max = max_freq
            else:
                if self.color_value_min is None:
                    self.color_value_min = self.ds[self.color_name].min().data
                if self.color_value_max is None:
                    self.color_value_max = self.ds[self.color_name].max().data

            hue = Hue(self.color_value_min, self.color_value_max, defaultHue=self.default_color, colors=self.colors)
        else:
            hue = None

        cell_colors = {}
        cell_values = {}
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                key = (x, y)
                if hue is not None and key in indexes_by_position:
                    if self.color_name == "freq":
                        freq = len(indexes_by_position[key])
                        (r, g, b, a) = hue.getHue(freq)
                        cell_colors[key] = f"rgb({r},{g},{b})"
                        cell_values[key] = freq
                    else:
                        mean_value_sum = 0
                        for idx in indexes_by_position[key]:
                            label = str(labels[idx].data)
                            values = self.ds[self.color_name][idx].data.tolist()
                            mean_value = sum(values)/len(values)
                            mean_value_sum += mean_value
                            label_values[label] = (mean_value,values)

                        value = mean_value_sum / len(indexes_by_position[key])
                        (r, g, b, a) = hue.getHue(value)
                        cell_colors[key] = f"rgb({r},{g},{b})"
                        cell_values[key] = value
                else:
                    cell_colors[key] = self.default_color
                    cell_values[key] = None

        if self.layout == "square":
            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    cx = centres_x[x, y].data
                    cy = centres_y[x, y].data
                    key = (x, y)
                    cell = Rectangle((cx - 0.5) * SomPlot.SCALE, (cy - 0.5) * SomPlot.SCALE, SomPlot.SCALE, SomPlot.SCALE,
                                     fill=cell_colors[key], stroke="none", stroke_width=0)
                    cell_value = cell_values[key]
                    if cell_value is not None:
                        cell.setTooltip(str(cell_value))
                    doc.add(cell)

        elif self.layout == "hexagonal":
            radius = 0.5 / math.cos(math.pi / 6)
            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    cx = centres_x[x, y].data
                    cy = centres_y[x, y].data
                    key = (x, y)
                    cell = Hexagon(cx * SomPlot.SCALE, cy * SomPlot.SCALE, radius * SomPlot.SCALE, fill=cell_colors[key],
                                   stroke="none", stroke_width=0)
                    cell_value = cell_values[key]
                    if cell_value is not None:
                        cell.setTooltip(str(cell_value))
                    doc.add(cell)

        else:
            raise Exception("Invalid layout value: " + self.layout)

        for x in range(self.grid_width):
            for y in range(self.grid_height):
                cx = (centres_x[x, y].data - 0.2)*SomPlot.SCALE
                cy = centres_y[x, y].data * SomPlot.SCALE
                sy = cy - 0.3*SomPlot.SCALE
                key = (x, y)
                if key in indexes_by_position:
                    indexes = indexes_by_position[key]

                    for i in range(len(indexes)):
                        idx = indexes[i]
                        xloc = cx
                        yloc = sy
                        fill = "gray"
                        marker_value = None
                        if self.color_name and self.color_name != "freq":
                            marker_value = self.ds[self.color_name][idx].data.mean()
                            (r, g, b, a) = hue.getHue(marker_value)
                            fill = f"rgb({r},{g},{b})"
                        marker = Circle(xloc, yloc, 0.05 * SomPlot.SCALE, fill=fill, stroke="black", stroke_width=1)
                        if marker_value is not None:
                            marker.setTooltip(str(marker_value))
                        doc.add(marker)
                        if labels is not None:
                            label = labels[idx].data
                            doc.add(Text(xloc + 10, yloc, label, font_height=20).setHorizontalCenter(False))
                        if len(indexes) > 1:
                            sy += 0.6*SomPlot.SCALE / (len(indexes)-1)
        if hue:
            tx = (1.5 + self.grid_width) * SomPlot.SCALE
            ty = 100
            tw = SomPlot.SCALE * 0.5
            th = SomPlot.SCALE * 2
            p = 50

            for idx in range(p):
                value = self.color_value_max - (idx / p) * (self.color_value_max - self.color_value_min)
                (r, g, b, a) = hue.getHue(value)
                y = ty + (idx / p) * th
                x = tx
                w = tw
                h = 1 + (th / p)
                rgb = f"rgb({r},{g},{b})"
                doc.add(Rectangle(x, y, w, h, fill=rgb, stroke="none", stroke_width=0))
                if idx == 0:
                    doc.add(Polygon([(x, y), (x + w, y), (x + 0.5 * w, y - 0.5 * w)], fill=rgb, stroke="black",
                                    stroke_width=1))
                elif idx == p - 1:
                    doc.add(
                        Polygon([(x, y + h), (x + w, y + h), (x + 0.5 * w, y + h + 0.5 * w)], fill=rgb, stroke="black",
                                stroke_width=1))

            doc.add(Rectangle(tx,ty,tw,th,fill="none",stroke="black", stroke_width=1))

            doc.add(Text(tx + tw * 0.5, ty - 40, f"{self.color_value_max:0.2f}", font_height=20).setVerticalCenter())
            doc.add(
                Text(tx + tw * 0.5, ty + th + 40, f"{self.color_value_min:0.2f}", font_height=20).setVerticalCenter())

        with open(path, "w") as f:
            f.write(doc.render())
            logging.info("Written output plot to %s" % path)

        if csv_path and labels is not None and self.color_name and self.color_name != "freq":
            with open(csv_path,"w") as f:
                first = True
                for idx in range(self.num_cases):
                    label = str(labels[idx].data)
                    grid_x = int(som[idx, 0].data)
                    grid_y = int(som[idx, 1].data)
                    (mean_value,values) = label_values.get(label,(None,None))
                    if first:
                        value_headings = [f"{self.color_name}_{i}" for i in range(len(values))]
                        f.write(",".join(["label","som_x","som_y","mean_" + self.color_name]+value_headings))
                        first = False
                    values_s = ",".join(map(lambda v:f"{v}",values))
                    f.write(f"\n{label},{grid_x},{grid_y},{mean_value},{values_s}")
            logging.info("Written output CSV to %s" % csv_path)


def main():

    logging.basicConfig(level=logging.INFO)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path",
                        help="the path to an input xarray dataset (in netcdf4 format) containing the data to load")
    parser.add_argument("svg_plot_path", type=str,
                        help="plot the SOM assignments to a SVG file",
                        default="")
    parser.add_argument("--csv-path", type=str,
                        help="Record CSV to accompany plot",
                        default="")
    parser.add_argument("--som-variable",
                        help="the name of the variable containing th som assignments",
                        default="som_assignments")
    parser.add_argument("--svg-plot-color-variable", type=str,
                        help="the name of a variable to use to color the plotted cells, or 'freq'",
                        default="freq")
    parser.add_argument("--svg-plot-color-variable-min", type=float,
                        help="minimum value for the cell color variable",
                        default=None)
    parser.add_argument("--svg-plot-color-variable-max", type=float,
                        help="maximum value for the cell color variable",
                        default=None)
    parser.add_argument("--svg-plot-label-variable", type=str,
                       help="the name of a variable to use to plot cases on the map",
                       default="")
    parser.add_argument("--svg-plot-colors", type=str,
                        help="comma separated list of colors",
                        default="blue,red")
    parser.add_argument("--svg-plot-default-color", type=str,
                        help="color to use for empty cells",
                        default="#A0A0A0")

    args = parser.parse_args()
    logging.info("Reading input data from %s" % args.input_path)
    ds = xr.open_dataset(args.input_path)

    plt = SomPlot(ds,
                  label_name=args.svg_plot_label_variable,
                  som_name=args.som_variable,
                  cell_x_name="cell_centres_x",
                  cell_y_name="cell_centres_y",
                  color_name=args.svg_plot_color_variable,
                  colors=args.svg_plot_colors.split(","),
                  color_value_min=args.svg_plot_color_variable_min,
                  color_value_max=args.svg_plot_color_variable_max,
                  default_color=args.svg_plot_default_color)
    plt.plot(args.svg_plot_path, args.csv_path)



if __name__ == '__main__':
    main()