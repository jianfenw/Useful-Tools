import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import copy

# |y_data| is an list of tuple (data, color).
def scatter_group_curve_plot(
        x_data,
        y_data_list,
        x_label="",
        y_label="",
        title="",
        yscale_log=False):
    # Create the plot object
    _, ax = plt.subplots()
    # Plot the data, set the size (s), color and transparency (alpha)
    ax.scatter([0], [0], s=10, marker='o', color='b', alpha=0.75)

    for y_data, y_color in y_data_list:
        ax.scatter(x_data, y_data, s=10, marker='x', color=y_color, alpha=0.75)
        ax.plot(x_data, y_data, lw=1.0, color=y_color, alpha=1)

    if yscale_log == True:
        ax.set_yscale('log')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.grid(True)
    plt.show()
