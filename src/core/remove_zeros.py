import cv2
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt


import cv2
import numpy as np
from PIL import Image
import os

class SeamCarver:
    def __init__(self, pil_image):
        self.pil_image = pil_image.convert("RGB")

    def get_seam_carving_cuts(self, ksize=3, num_of_zeros = 5):
        
        img = np.array(self.pil_image)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
        energy = np.abs(sobel_x) + np.abs(sobel_y)

        # Find zero-energy rows and columns
        zero_rows = np.where(np.all(energy == 0, axis=1))[0]
        zero_cols = np.where(np.all(energy == 0, axis=0))[0]

        # Remove rows if more than  num_of_zeros are zero
        img_array = np.array(img)
        if len(zero_rows) > num_of_zeros:
            energy = np.delete(energy, zero_rows, axis=0)
            img_array = np.delete(img_array, zero_rows, axis=0)

        # Remove columns if more than 5 are zero
        if len(zero_cols) > num_of_zeros:
            energy = np.delete(energy, zero_cols, axis=1)
            img_array = np.delete(img_array, zero_cols, axis=1)

        cleaned_image = Image.fromarray(img_array)

        return cleaned_image

        
        
        