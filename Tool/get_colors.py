import binascii
import os.path
import cv2
import numpy as np
import scipy
from PIL import Image, ImageFile


class GetColors:
    def __init__(self, path):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        self.path = path
        self.image = None
        self.image_w = 0
        self.image_h = 0
        self.color_w = 0
        self.color_h = 0
        self.NUM_CLUSTERS = 5
        self.open_file()
        self.set_infos()

    def open_file(self):
        if os.path.isfile(self.path):
            self.image = Image.open(self.path)
        else:
            raise "File doesn't exist!"

    def set_infos(self):
        self.image_w = self.image.size[0]
        self.image_h = self.image.size[1]
        self.color_w = self.image_w * 0.25 * 0.2
        self.color_h = self.color_w

    def resize_image(self):
        self.image = self.image.resize((300, 300))

    def get_colors(self):
        self.resize_image()
        ar = np.asarray(self.image)
        shape = ar.shape
        ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)
        codes, dist = scipy.cluster.vq.kmeans(ar, self.NUM_CLUSTERS)
        all_colors = codes
        vecs, dist = scipy.cluster.vq.vq(ar, codes)  # assign codes
        counts, bins = np.histogram(vecs, len(codes))  # count occurrences
        index_max = np.argmax(counts)  # find most frequent
        peak = codes[index_max]
        colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
        frequent_color = ",".join([str(i) for i in peak.tolist()])
        all_colors = [",".join([str(i) for i in color]) for color in all_colors]
        return frequent_color, all_colors[0], all_colors[1]

    def make_palette(self):
        all_colors, frequent = self.get_colors()
        current = 0
        image = cv2.imread(self.path, cv2.COLOR_BGR2RGB)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        color = tuple([float(i) for i in frequent.split(',')])
        start_y = (self.image_h * 0.5) - (self.color_h * 0.5)
        start_y = int(start_y)
        start_x = self.image_w - self.color_w
        start_x = int(start_x)
        end_y = (self.image_h * 0.5) + (self.color_h * 0.5)
        end_y = int(end_y)
        end_x = self.image_w
        end_x = int(end_x)
        start_point = (start_x, start_y)
        end_point = (end_x, end_y)
        image = cv2.rectangle(image, start_point, end_point, color, -1)
        for color in all_colors:
            start_y = self.image_h - self.color_h
            start_y = int(start_y)
            start_x = self.image_w - ((current + 1) * self.color_w)
            start_x = int(start_x)
            end_y = int(self.image_h)
            end_x = self.image_w - (current * self.color_w)
            end_x = int(end_x)
            start_point = (start_x, start_y)
            end_point = (end_x, end_y)
            color = tuple([float(i) for i in color.split(',')])
            thickness = -1
            image = cv2.rectangle(image, start_point, end_point, color, thickness)
            current += 1
        im = Image.fromarray(image)
        root = '/'.join([folder for folder in self.path.split('\\')[:-1]])
        root += '/palette.jpg'
        im.save(root)
        return root
