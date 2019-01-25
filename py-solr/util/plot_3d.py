import matplotlib
#matplotlib.use('GTKAgg')    # Needs to be called before ANY reference to
                            # matplotlib objects are made.

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D

import numpy as np
import time


class Fig:

    @staticmethod
    def show(block=True):
        t_start = time.clock()
        plt.show(block)
        t_end = time.clock()
        print('Display time: %f [s]' % (t_end - t_start))

    def __init__(self, title=None, figsize=(16, 9), projection='3d'):
        self.fig = plt.figure(figsize=figsize)
        self.ax = self.fig.add_subplot(111, projection=projection)

        if title is not None:
            self.ax.set_title(title)

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.colors = None

    def create_colors(self, num_points):
        self.colors = iter(cm.rainbow(np.linspace(0, 1, num_points)))

    def next_color(self):
        return self.colors.next()

    def plot_mbb(self, rect, linecolor='red', linestyle="-"):
        """ Given pyplot axes, draws rectangle (rect) on it.
        """

        xlo = rect[0][0]
        ylo = rect[0][1]
        zlo = rect[0][2]
        xhi = rect[1][0]
        yhi = rect[1][1]
        zhi = rect[1][2]
        # x_ext = rect[3] - rect[0]
        # y_ext = rect[4] - rect[1]
        # z_ext = rect[5] - rect[2]

        self.ax.scatter(xlo, ylo, zs=zlo, color=linecolor, s=10)
        self.ax.scatter(xhi, yhi, zs=zhi, color=linecolor, s=10)

        self.ax.plot([xlo, xhi], [ylo, ylo], zs=[zlo, zlo], color=linecolor,
                     linestyle=linestyle)
        self.ax.plot([xlo, xlo], [ylo, yhi], zs=[zlo, zlo], color=linecolor,
                     linestyle=linestyle)
        self.ax.plot([xlo, xlo], [ylo, ylo], zs=[zlo, zhi], color=linecolor,
                     linestyle=linestyle)

        self.ax.plot([xhi, xlo], [yhi, yhi], zs=[zhi, zhi], color=linecolor,
                     linestyle=linestyle)
        self.ax.plot([xhi, xhi], [yhi, ylo], zs=[zhi, zhi], color=linecolor,
                     linestyle=linestyle)
        self.ax.plot([xhi, xhi], [yhi, yhi], zs=[zhi, zlo], color=linecolor,
                     linestyle=linestyle)

        self.ax.plot([xlo, xlo], [yhi, ylo], zs=[zhi, zhi], color=linecolor,
                     linestyle=linestyle)
        self.ax.plot([xhi, xlo], [yhi, yhi], zs=[zlo, zlo], color=linecolor,
                     linestyle=linestyle)
        self.ax.plot([xhi, xlo], [ylo, ylo], zs=[zhi, zhi], color=linecolor,
                     linestyle=linestyle)

        self.ax.plot([xlo, xlo], [yhi, yhi], zs=[zlo, zhi], color=linecolor,
                     linestyle=linestyle)
        self.ax.plot([xhi, xhi], [ylo, ylo], zs=[zlo, zhi], color=linecolor,
                     linestyle=linestyle)
        self.ax.plot([xhi, xhi], [ylo, yhi], zs=[zlo, zlo], color=linecolor,
                     linestyle=linestyle)

    def add_points(self, points, label=None, color='green', s=1):
        for p in points:
            # print("%f, %f, %f" % (p['geometry.coordinates_0___pdouble'],
            #                      p['geometry.coordinates_1___pdouble'],
            #                      p['geometry.coordinates_2___pdouble']))

            self.ax.scatter(p['geometry.coordinates_0___pdouble'],
                            p['geometry.coordinates_1___pdouble'],
                            zs=p['geometry.coordinates_2___pdouble'],
                            color=color, s=s)

        p = points[0]
        if label is not None:
            self.ax.scatter(p['geometry.coordinates_0___pdouble'],
                            p['geometry.coordinates_1___pdouble'],
                            zs=p['geometry.coordinates_2___pdouble'],
                            color=color,
                            s=s, label=label)
            self.ax.legend()
