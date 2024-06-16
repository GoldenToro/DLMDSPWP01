import random

from fancy_logging import logger

from bokeh.plotting import figure, show, output_file, save
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.annotations import Title

import pandas as pd

def random_color():
    """
    Generate a random color hex code.

    :return: A random color in hex format.
    """
    r = lambda: random.randint(0, 255)
    return f'#{r():02X}{r():02X}{r():02X}'

FULL_SCREEN = {
    'left': 0,
    'top': 0,
    'width': 1,
    'height': 1
}

class PlotManager:
    """
    Class to manage plotting of figures with specific positioning on screen.

    :param screen_size_x: Width of the screen in pixels.
    :param screen_size_y: Height of the screen in pixels.
    :param num_plots_vertical: Number of plots vertically.
    :param num_plots_horizontal: Number of plots horizontally.
    """

    def __init__(self, screen_size_x=3440, screen_size_y=1365, num_plots_vertical=2, num_plots_horizontal=4):
        self.screen_size_x = screen_size_x
        self.screen_size_y = screen_size_y
        self.num_plots_vertical = num_plots_vertical
        self.num_plots_horizontal = num_plots_horizontal

        self.plt_size_x = screen_size_x / num_plots_horizontal
        self.plt_size_y = screen_size_y / num_plots_vertical

        self.plots = []

    def show_plots(self):
        """
        Show all currently plotted figures.
        """
        grid = gridplot(self.plots, ncols=self.num_plots_horizontal)
        show(grid)
        self.plots = []

    def delete_plots(self):
        """
        Delete all currently plotted figures without showing them.
        """
        self.plots = []

    def position_figure(self, p):
        """
        Position the current figure window on screen.

        :param p: Bokeh figure object.
        """
        # Bokeh does not have a direct equivalent to position figures on the screen,
        # but we can manage the layout using gridplot or other layout functions.
        self.plots.append(p)

    def load_xy_as_line_plot(self, data, name, position=None, styles=None, text=None):
        """
        Load data and create a line plot.

        :param data: DataFrame containing the data to plot.
        :param name: Name of the plot.
        :param position: Dictionary specifying 'left', 'top', 'width', and 'height' of the figure window.
        :param styles: Dictionary specifying styles for each column.
        :param text: Additional text to display on the plot.
        """
        p = figure(title=name, width=int(self.plt_size_x), height=int(self.plt_size_y))

        x = data['x'].values
        source = ColumnDataSource(data)

        for col in data.columns:
            if col != 'x':
                style_for_this_plot = {'color': random_color()}
                type_for_this_plot = "line"

                if styles and col in styles:
                    style_for_this_plot.update(styles[col])
                    if 'type' in style_for_this_plot:
                        type_for_this_plot = style_for_this_plot.pop('type')

                if type_for_this_plot == 'line':
                    p.line(x, data[col].values, legend_label=col, **style_for_this_plot)
                elif type_for_this_plot == 'scatter':
                    p.scatter(x, data[col].values, legend_label=col, **style_for_this_plot)
                else:
                    raise ValueError("Unsupported plot type")

        if text:
            p.add_layout(Title(text=text, text_font_size="12pt"), 'above')

        p.add_tools(HoverTool(tooltips=[("x", "@x"), ("y", "@y")]))

        p.legend.location = "top_left"
        p.grid.grid_line_alpha = 0.3
        p.xaxis.axis_label = 'x axis'
        p.yaxis.axis_label = 'y axis'

        self.position_figure(p)
