import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import style

def show_plots():
    plt.show()

def load_xy_as_line_plot(data, name):

    # set plot style
    style.use('ggplot')

    plt.figure(name)
    x = data['x'].values
    for i in range(1,data.shape[1]):
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


