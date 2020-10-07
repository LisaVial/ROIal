from PyQt5 import QtWidgets, QtCore
import os

from plot_widget import PlotWidget
from tiff_reader import TiffReader

import pyqtgraph as pg


class TiffFileView(QtWidgets.QWidget):
    def __init__(self, parent, tiff_file):
        super().__init__(parent)
        self.reader = TiffReader(tiff_file)
        self.tiff_file = tiff_file

        self.plot_creation_thread = None

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.imv = pg.ImageView(self)
        self.imv.show()

        # self.figure = self.plot_widget.figure

        self.slider = QtWidgets.QSlider(self)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        # max is the last index of the image list
        self.slider.setMaximum(self.reader.num_of_imgs - 1)
        main_layout.addWidget(self.imv)
        main_layout.addWidget(self.slider)
        # self.ax = self.figure.add_subplot(111)
        self.slider_moved(0)

        self.slider.valueChanged.connect(self.slider_moved)

    def slider_moved(self, val):
        self.show_tiff_preview(val)

    def show_tiff_preview(self, val):
        self.imv.setImage(self.reader.stack[1][val])
        # self.ax.clear()
        # self.ax.imshow(self.reader.stack[1][val])
        # self.ax.spines['right'].set_visible(False)
        # self.ax.spines['top'].set_visible(False)

    def can_be_closed(self):
        return self.plot_widget.close()

