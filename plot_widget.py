import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class PlotWidget(QWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.plot_thread = None

        self.figure = Figure()
        self.figure.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, hspace=0.3, wspace=0.3)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        main_layout = QWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)

    def clear_figure(self):
        self.figure.clear()

    def refresh_canvas(self):
        self.canvas.draw()

