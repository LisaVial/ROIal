from PyQt5 import QtCore, QtWidgets
import cv2
import numpy as np


class RoiDetectionThread(QtCore.QThread):
    operation_changed = QtCore.pyqtSignal(str)
    progress_made = QtCore.pyqtSignal(float)
    data_updated = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    def __init__(self,  reader):
        super().__init__()
        self.reader = reader
        self.tiff_stack = self.reader.stack
        self.roi_mask = None

    def get_circular_rois_mask(self, img, kps):
        non_overlap = []
        overlap_indices = []
        h, w = img.shape[0], img.shape[1]
        mask = np.zeros((h, w), dtype=bool)
        for keypoint_index in range(len(kps)):
            if keypoint_index in overlap_indices:
                continue  # skip i
            else:
                non_overlap.append(kps[keypoint_index])
            for next_keypoint_index in range(keypoint_index + 1, len(kps)):
                if cv2.KeyPoint_overlap(kps[keypoint_index], kps[next_keypoint_index]) > 0.0:
                    overlap_indices.append(next_keypoint_index)

        # for non_overlap_index in range(len(non_overlap)):
        for non_overlap_index in range(len(non_overlap)):
            x_center, y_center = int(non_overlap[non_overlap_index].pt[0]), int(non_overlap[non_overlap_index].pt[1])
            radius = 10  # radius
            mask_mask = np.array([])
            for x_offset in range(-radius, radius):
                for y_offset in [0, radius / 2, 0, -(radius / 2), radius, radius / 2, 0, -(radius / 2), radius,
                                 radius / 2, 0,
                                 -(radius / 2), 0]:
                    if x_center + x_offset < w and y_center + y_offset < h:
                        px_idx = [(x_center + x_offset, y_center + y_offset)]
                        px_idx_tuple = np.empty(len(px_idx), dtype=object)
                        px_idx_tuple[:] = px_idx
                        mask_mask = np.append(mask_mask, px_idx)
                        mask_mask = np.asarray([(mask_mask[i], mask_mask[i + 1]) for i in range(0, len(mask_mask), 2)
                                                if i + 1 < len(mask_mask)])

            for pixel_index in mask_mask:
                mask[int(pixel_index[1]), int(pixel_index[0])] = True
        return mask

    def roi_mask_creation(self):
        surf = cv2.xfeatures2d.SURF_create(hessianThreshold=400, nOctaves=8)
        kps = []
        for i in range(len(self.tiff_stack[1])):
            img = self.tiff_stack[1][i]
            kp, des = surf.detectAndCompute(img, None)
            kps.append(kp)
            # probably somethin with thread initiation

            data = [img, kp]
            self.data_updated.emit(data)
            progress = round(((i + 1) / len(self.tiff_stack[1])) * 100.0, 2)
            self.progress_made.emit(progress)
        mask = self.get_circular_rois_mask(self, img, kps)
        return mask

    def run(self):
        self.operation_changed.emit("Creating ROI mask")
        self.roi_mask = self.roi_mask_creation()
        self.finished.emit()
