import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import os.path


class DataListView(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.selected_folder_label = QtWidgets.QLabel("")
        self.current_folder = ""

        self.selected_folder_button = QtWidgets.QPushButton("...")
        self.selected_folder_button.setFixedSize(24, 24)
        self.selected_folder_button.pressed.connect(self.on_select_folder_button_pressed)

        self.file_list = QtWidgets.QListWidget(self)

        main_layout = QtWidgets.QVBoxLayout(self)
        folder_path_layout = QtWidgets.QHBoxLayout()
        folder_path_layout.addWidget(self.selected_folder_label)
        folder_path_layout.addWidget(self.selected_folder_button)
        main_layout.addLayout(folder_path_layout)
        main_layout.addWidget(self.file_list)

    @QtCore.pyqtSlot()
    def on_select_folder_button_pressed(self):
        selected_folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Please choose a directory")
        if len(selected_folder) > 0:
            self.set_current_folder(selected_folder)

    def set_current_folder(self, folder):
        self.current_folder = folder
        self.selected_folder_label.setText(folder)
        self.file_list.clear()
        data_files = self.get_data()
        for file in data_files:
            self.file_list.addItem(file)

    def get_data(self):
        found_files = []
        for root, sub_folders, files in os.walk(self.current_folder):
            for file in files:
                absolute_path = os.path.join(root, file)
                relative_path = os.path.relpath(absolute_path, self.current_folder)
                if file.endswith('.tif'):
                    found_files.append(relative_path)
        return found_files