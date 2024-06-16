from fancy_logging import logger
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import style

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

        self.number_of_plots = 0

    def show_plots(self):
        """
        Show all currently plotted figures.
        """
        plt.show()
        self.number_of_plots = 0

    def delete_plots(self):
        """
        Delete all currently plotted figures without showing them.
        """
        plt.close('all')
        self.number_of_plots = 0

    def position_figure(self, position=None):
        """
        Position the current figure window on screen.

        :param position: Dictionary specifying 'left', 'top', 'width', and 'height' of the figure window.
        """
        if self.number_of_plots >= (self.num_plots_vertical * self.num_plots_horizontal):
            self.number_of_plots = 0

        line = (self.number_of_plots * self.plt_size_x) // self.screen_size_x
        pos_x = self.number_of_plots * self.plt_size_x - (line * self.screen_size_x)
        pos_y = line * self.plt_size_y

        manager = plt.get_current_fig_manager()

        if position:
            manager.window.wm_geometry(f"{int(position['width'] * self.screen_size_x)}x{int(position['height'] * self.screen_size_y)}+{int(position['left'])}+{int(position['top'])}")
        else:
            manager.window.wm_geometry(f"{int(self.plt_size_x)}x{int(self.plt_size_y)}+{int(pos_x)}+{int(pos_y)}")

        self.number_of_plots += 1

    def load_xy_as_line_plot(self, data, name, position=None, styles=None, text=None):
        """
        Load data and create a line plot.

        :param data: DataFrame containing the data to plot.
        :param name: Name of the plot.
        :param position: Dictionary specifying 'left', 'top', 'width', and 'height' of the figure window.
        :param styles: Dictionary specifying styles for each column.
        :param text: Additional text to display on the plot.
        """
        style.use('ggplot')
        plt.figure(name)

        x = data['x'].values

        for col in data.columns:
            if col != 'x':
                style_for_this_plot = {'linewidth': 2}
                type_for_this_plot = "line"

                if styles and col in styles:
                    style_for_this_plot.update(styles[col])
                    if 'type' in style_for_this_plot:
                        type_for_this_plot = style_for_this_plot.pop('type')

                if type_for_this_plot == 'line':
                    plt.plot(x, data[col].values, label=col, **style_for_this_plot)
                elif type_for_this_plot == 'scatter':
                    plt.scatter(x, data[col].values, label=col, **style_for_this_plot)
                else:
                    raise ValueError("Unsupported plot type")

        box = plt.subplot(111).get_position()
        plt.subplot(111).set_position([box.x0, box.y0, box.width * 0.8, box.height])

        if text:
            plt.text(23, box.height, text, fontsize=12, color='black', ha='left',
                    bbox=dict(facecolor='lightgrey', alpha=0.5, pad=5))

        plt.legend(loc='center right', bbox_to_anchor=(0, 0.5), fancybox=True, shadow=True,
                   ncol=2 if data.shape[1] > 25 else 1)
        plt.grid(True, color="k")
        plt.ylabel('y axis')
        plt.xlabel('x axis')
        plt.title(name)

        self.position_figure(position)

