import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import style

number_of_plots = 0

# Change the following variables for your monitor
SCREEN_SIZE_X = 3440
# Minus the Size of Windows Taskbar
SCREEN_SIZE_Y = 1440 - 75
# Change the following variables to change the number of plots shown on your screen
NUMBER_OF_PLOTS_SHOWN_VERTICAL = 2
NUMBER_OF_PLOTS_SHOWN_HORIZONTAL = 5


# Calculate Size of plots shown
PLT_SIZE_X = SCREEN_SIZE_X / NUMBER_OF_PLOTS_SHOWN_HORIZONTAL
PLT_SIZE_Y = SCREEN_SIZE_Y / NUMBER_OF_PLOTS_SHOWN_VERTICAL

FULL_SCREEN = {
    'left': 0,
    'top': 0,
    'width': 1,
    'height': 1
}

def show_plots():
    global number_of_plots

    plt.show()

    number_of_plots = 0


def position_figure(position=None):
    global number_of_plots


    line = (number_of_plots * PLT_SIZE_X) // SCREEN_SIZE_X

    pos_x = number_of_plots * PLT_SIZE_X - (line * SCREEN_SIZE_X)
    pos_y = line * PLT_SIZE_Y

    manager = plt.get_current_fig_manager()

    if position:
        manager.window.wm_geometry(f"{int(position['width'] * SCREEN_SIZE_X)}x{int(position['height'] * SCREEN_SIZE_Y)}+{int(position['left'])}+{int(position['top'])}")
    else:
        manager.window.wm_geometry(f"{int(PLT_SIZE_X)}x{int(PLT_SIZE_Y)}+{int(pos_x)}+{int(pos_y)}")

    number_of_plots += 1


def load_xy_as_line_plot(data, name, position = None):
    # set plot style
    style.use('ggplot')

    plt.figure(name)
    x = data['x'].values
    for i in range(1, data.shape[1]):
        function_name = f'y{i}'
        plt.plot(x, data[function_name].values, label=function_name, linewidth=2)

    box = plt.subplot(111).get_position()
    plt.subplot(111).set_position([box.x0, box.y0, box.width * 0.8, box.height])

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5),
               fancybox=True, shadow=True, ncol=2)
    plt.grid(True, color="k")
    plt.ylabel('y axis')
    plt.xlabel('x axis')
    plt.title(name)

    position_figure(position)
