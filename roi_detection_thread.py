from PyQt5 import QtCore, QtWidgets
import cv2
import numpy as np
from IPython import embed


class RoiDetectionThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    data_updated = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    def __init__(self, reader):
        super().__init__()
        self.reader = reader
        self.tiff_stack = self.reader.stack
        self.roi_mask = None

    def get_roi_dict(self, validated_rois):
        h, w = self.tiff_stack[0].shape[0], self.tiff_stack[0].shape[1]
        roi_dict = dict()
        for keypoint_index in range(len(validated_rois)):
            if str(keypoint_index) in list(roi_dict.keys()):
                continue
            else:
                x_center, y_center = \
                    int(validated_rois[keypoint_index].pt[0]), int(validated_rois[keypoint_index].pt[1])
                radius = 10  # radius
                pixels = []
                for x_offset in range(-radius, radius):
                    for y_offset in range(-radius, radius):
                        if x_center + x_offset < w and y_center + y_offset < h:
                            px_idx = [(x_center + x_offset, y_center + y_offset)]
                            px_idx_tuple = np.empty(len(px_idx), dtype=object)
                            px_idx_tuple[:] = px_idx
                            pixels.extend(px_idx_tuple)
                roi_dict[str(keypoint_index)] = pixels

        return roi_dict

    def roi_gathering(self):
        surf = cv2.xfeatures2d.SURF_create(hessianThreshold=800, upright=True, extended=True)
        # detector = cv2.SimpleBlobDetector.create()
        kps = []
        for i in range(len(self.tiff_stack)):
            img = self.tiff_stack[i]
            img = img.astype('uint8')
            kp, des = surf.detectAndCompute(img, None)
            # kp = detector.detect(img)
            # embed()
            kps.extend(kp)
            # probably somethin with thread initiation

            data = [img, kp]
            self.data_updated.emit(data)
            progress = round(((i + 1) / len(self.tiff_stack)) * 100.0, 2)
            self.progress_made.emit(progress)
        print(len(kps))
        # roi_dict = self.get_circular_rois_mask(img, kps)
        return kps

    def validating_rois(self, roi_list):
        non_overlap = []
        overlap_indices = []
        for keypoint_index in range(len(roi_list)):
            for next_keypoint_index in range(keypoint_index + 1, len(roi_list)):
                if cv2.KeyPoint_overlap(roi_list[keypoint_index], roi_list[next_keypoint_index]) >= 0.025 and \
                        roi_list[keypoint_index].size >= 1:
                    overlap_indices.append(next_keypoint_index)
            if keypoint_index in overlap_indices:
                continue  # skip i
            else:
                non_overlap.append(roi_list[keypoint_index])
            data = [self.tiff_stack[0], non_overlap]
            self.data_updated.emit(data)
            progress = round(((keypoint_index + 1) / len(roi_list)) * 100.0, 2)
            self.progress_made.emit(progress)
        return non_overlap

    def run(self):
        self.operation_changed.emit("Gathering ROIs")
        roi_list = self.roi_gathering()
        self.operation_changed.emit("Validating ROIs")
        valid_rois = self.validating_rois(roi_list)
        self.operation_changed.emit("Create dictionary of validated ROIs")
        roi_dict = self.get_roi_dict(valid_rois)
        embed()
        self.finished.emit()
