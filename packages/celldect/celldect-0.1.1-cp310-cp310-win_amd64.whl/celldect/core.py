import base64
from base64 import b64encode
import os
import cv2
import numpy as np
import json
import concurrent.futures
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN

import pandas as pd
import csv
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from scipy.ndimage import median_filter
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy.ndimage import label, generate_binary_structure, maximum_filter
from sklearn.mixture import GaussianMixture
#from pyzbar.pyzbar import decode
import tempfile
import shutil


def watershed_image(input_path, output_path):
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_path):
            return f"输入文件 {input_path} 不存在"

        # 读取图像，使用IMREAD_GRAYSCALE参数以灰度模式读取
        binary = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if binary is None:
            return f"无法读取图像 {input_path}"

        # 使用Otsu's thresholding进行二值化
        #_, binary = cv2.threshold(binary, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 计算二值图像中每个像素点到最近背景点的距离
        distance = cv2.distanceTransform(binary, cv2.DIST_L2, 5)

        # 使用自定义的局部最大值检测
        max_mask = (distance == maximum_filter(distance, size=18)) & (binary > 0)
        markers, _ = label(max_mask, structure=generate_binary_structure(2, 2))

        # 使用watershed函数进行分水岭分割
        labels = watershed(-distance, markers, mask=binary)

        # 使用NumPy的广播机制来寻找边界像素
        #offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        #offsets = [(-1, 0), (-1, -1), (0, -1), (-1, 1)]
        offsets = [(-1, 0), (-1, -1), (0, -1), (-1, 1),(1, 1),(1, -1)]
        is_border = np.zeros_like(binary, dtype=bool)
        for offset in offsets:
            is_border |= (labels != np.roll(labels, shift=offset, axis=(0, 1))) & (labels > 0) & (
                np.roll(labels, shift=offset, axis=(0, 1)) > 0)

        # 对于边界像素，将其值设为0
        binary[is_border] = 0

        # 保存处理后的图像
        cv2.imwrite(output_path, binary)

        return "OK"

    except Exception as e:
        return f"发生未知错误: {e}"
