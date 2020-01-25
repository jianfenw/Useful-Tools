import numpy as np
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt


def f(x):
    return x**2 + 1


def f_fit(x, y_fit):
    a, b, c = y_fit.tolist()
    return a * x**2 + b * x + c


def line_fit_main(x, y, title, x_label, y_label):
    _, ax = plt.subplots()

    y_fit = np.polyfit(x, y, 2)
    y_show = np.poly1d(y_fit)
    y1 = f_fit(x, y_fit)

    ax.scatter(x, y, c='g')
    ax.plot(x, y1, 'b--')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend()
    plt.grid(True)


def bar_plot(title):
    _, ax = plt.subplots()

    objects = ('Python', 'C++', 'Java', 'Perl', 'Scala', 'Lisp')
    y_pos = np.asarray([1,3,6,8,10, 12])
    performance = [10,8,6,4,2,1]

    ax.bar(y_pos, performance, align='center', alpha=0.5)
    ax.set_xticks(y_pos, objects)
    ax.set_ylabel('Usage')
    ax.set_title(title)
    plt.grid(True)


if __name__ == '__main__':
    """
    # 2g
    x_2g = np.asarray(
        [1.804, 3.541, 3.704, 3.58, 3.932, 4.885, 6.52, 8.146, 10, 11.71])
    y_2g = np.asarray([i for i in range(1, 11)])

    # 3g
    x_3g = np.asarray(
        [2.771, 4.366, 4.604, 4.794, 4.961, 5.592, 6.623, 7.99, 9.357, 11.27])
    y_3g = np.asarray([i for i in range(1, 11)])

    # 4g
    x_4g = np.asarray(
        [3.39, 4.601, 5.318, 6.299, 7.602, 8.768, 9.66, 9.825, 11.13, 12.49])
    y_4g = np.asarray([i for i in range(1, 11)])

    x_label = 'Count of requests'
    y_label = 'Peak queueing delay level'
    figure_title_2g = 'Mapping from the request count to the peak queueing delay (2G)'
    line_fit_main(x_2g, y_2g, figure_title_2g, x_label, y_label)

    figure_title_3g = 'Mapping from the request count to the peak queueing delay (3G)'
    line_fit_main(x_3g, y_3g, figure_title_3g, x_label, y_label)

    figure_title_4g = 'Mapping from the request count to the peak queueing delay (4G)'
    line_fit_main(x_4g, y_4g, figure_title_4g, x_label, y_label)
    """

    bar_plot('Programming language usage')
    
    plt.show()
