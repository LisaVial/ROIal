import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image
from IPython import embed


class TiffReader:
    def __init__(self, path):
        self.file_path = path
        ret, self.stack = self.open_tiff_stack()
        # self.stack = Image.open(path)
        self.num_of_imgs = len(self.stack)
        # embed()

    def open_tiff_stack(self):
        tiff_stack = cv2.imreadmulti(self.file_path, flags=(cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH))
        return tiff_stack
