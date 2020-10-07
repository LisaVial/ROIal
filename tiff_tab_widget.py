import os.path
from PyQt5 import QtCore, QtWidgets

from tiff_file_view import TiffFileView


class TiffTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.setTabsClosable(True)
        self.setMovable(True)
        self.setTabBarAutoHide(False)

        self.tabCloseRequested.connect(self.on_tab_close_requested)

        self.tiff_file_widget_map = dict()

    def show_tiff_file_view(self, tiff_file):
        if tiff_file not in self.tiff_file_widget_map.keys():
            tiff_file_view = TiffFileView(self, tiff_file)
            relative_root, file_name = os.path.split(tiff_file)
            if file_name.endswith('.tif'):
                file_name = file_name[:-4]
            self.addTab(tiff_file_view, file_name)
            self.tiff_file_widget_map[tiff_file] = tiff_file_view
        self.setCurrentWidget(self.tiff_file_widget_map[tiff_file])

    @QtCore.pyqtSlot(int)
    def on_tab_close_requested(self, index):
        tiff_file_view = self.widget(index)
        if tiff_file_view.can_be_closed():
            self.tiff_file_widget_map.pop(tiff_file_view.tiff_file, None)
            self.removeTab(index)
            tiff_file_view.close()
