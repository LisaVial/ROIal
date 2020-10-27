from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np
import cv2
from roi_detection_thread import RoiDetectionThread


class RoiDialog(QtWidgets.QDialog):
    def __init__(self, parent, reader):
        super().__init__(parent)

        self.reader = reader
        self.roi_dict = None

        title = 'Creating a ROI mask'

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowTitleHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        self.width = 800
        self.height = 600
        self.resize(self.width, self.height)

        self.roi_detection_thread = None

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.setWindowTitle(title)

        user_interactions_layout = QtWidgets.QVBoxLayout(self)
        user_interactions_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

        self.save_roi_mask_box = QtWidgets.QCheckBox('Save ROIs')
        self.label_save_roi_mask_box = QtWidgets.QLabel('Don\'t save ROIs')
        self.save_roi_mask_box.stateChanged.connect(self.save_roi_mask_box_clicked)
        user_interactions_layout.addWidget(self.save_roi_mask_box)
        user_interactions_layout.addWidget(self.label_save_roi_mask_box)

        self.start_roi_mask_creation_button = QtWidgets.QPushButton(self)
        # self.start_roi_mask_creation_button.setFixedSize(self.width, 25)
        self.start_roi_mask_creation_button.setText('Create ROI mask')
        self.start_roi_mask_creation_button.clicked.connect(self.initialize_roi_mask_creation)
        user_interactions_layout.addWidget(self.start_roi_mask_creation_button)

        self.operation_label = QtWidgets.QLabel(self)
        self.operation_label.setText('Nothing happens so far')
        user_interactions_layout.addWidget(self.operation_label)

        self.progress_label = QtWidgets.QLabel(self)
        user_interactions_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        # self.progress_bar.setFixedSize(self.width, 25)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        user_interactions_layout.addWidget(self.progress_bar)
        main_layout.addLayout(user_interactions_layout)

        pg.setConfigOption('foreground', 'w')
        self.imv = pg.ImageView(self)
        self.imv.setMinimumSize(600, 800)
        self.imv.ui.histogram.hide()
        self.imv.ui.roiBtn.hide()
        self.imv.ui.menuBtn.hide()
        self.imv.show()
        main_layout.addWidget(self.imv)

        # self.timer = pg.QtCore.QTimer(self)
        # self.timer.timeout.connect(self.on_timer)
        self.img = None
        self.kp = None


    def save_roi_mask_box_clicked(self):
        self.label_save_roi_mask_box.setText('Saving ROI mask to numpy array at the end')

    def initialize_roi_mask_creation(self):
        if self.roi_dict is None:
            self.progress_bar.setValue(0)
            self.progress_label.setText('')
            self.operation_label.setText('creating ROI mask')
            self.start_roi_mask_creation_button.setEnabled(False)
            self.roi_detection_thread = RoiDetectionThread(self.reader)
            self.roi_detection_thread.progress_made.connect(self.on_progress_made)
            self.roi_detection_thread.operation_changed.connect(self.on_operation_changed)
            self.roi_detection_thread.data_updated.connect(self.on_data_updated)
            self.roi_detection_thread.finished.connect(self.on_filter_thread_finished)
            debug_mode = False  # set to 'True' in order to debug plot creation with embed
            if debug_mode:
                # synchronous plotting (runs in main thread and thus allows debugging)
                self.roi_detection_thread.run()
            else:
                # asynchronous plotting (default):
                self.roi_detection_thread.start()  # start will start thread (and run),
                # but main thread will continue immediately

            # self.timer.start(2000)  # time in [ms]

    @QtCore.pyqtSlot(str)
    def on_operation_changed(self, operation):
        self.progress_bar.setValue(0)
        self.operation_label.setText(operation)

    @QtCore.pyqtSlot(float)
    def on_progress_made(self, progress):
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(str(progress) + "%")

    def on_data_updated(self, data):
        self.img = data[0]
        self.kp = data[1]
        img_kp = cv2.drawKeypoints(image=self.img, outImage=self.img, keypoints=self.kp,
                                   flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS, color=(255, 0, 0))
        self.imv.setImage(np.rot90(img_kp))

    # @QtCore.pyqtSlot()
    # def on_timer(self):
    #     img_kp = cv2.drawKeypoints(image=self.img, outImage=self.img, keypoints=self.kp,
    #                                flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS, color=(255, 0, 0))
    #     self.imv.setImage(img_kp)

    def on_filter_thread_finished(self):
        self.progress_label.setText("Finished :)")
        # if self.roi_detection_thread.roi_dict:
        #     self.roi_dict = self.roi_detection_thread.roi_dict
        self.roi_detection_thread = None
        self.start_roi_mask_creation_button.setEnabled(True)
        if self.save_roi_mask_box.isChecked():
            filename = self.reader.file_path[:-4] + '.npy'
            with open(filename, 'wb') as f:
                np.save(f, self.roi_dict)

