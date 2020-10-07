import sys
import os
import ctypes
import PyQt5.QtWidgets as QtWidgets

from main_window import MainWindow

if os.name == 'nt':
    my_app_id = u'lv.ROIal.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

sys._excepthook = sys.excepthook


def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

sys.excepthook = my_exception_hook

application = QtWidgets.QApplication(sys.argv)
mainWindow = MainWindow('ROIal')
mainWindow.show()

application.setActiveWindow(mainWindow)
sys.exit(application.exec())