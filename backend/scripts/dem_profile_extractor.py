from os import path
from math import radians, sin, cos, sqrt, atan2
import rasterio
from pyproj import Geod
from rasterio.transform import xy
from rasterio.windows import Window
from numba import njit, int32
import numpy as np
from scripts import utils


class DemProfileExtractor:
    # 类属性缓存，确保只加载一次
    _dataset = None
    _transform = None
    _res = None

    def __init__(self, dem_path=None):
        if DemProfileExtractor._dataset is None:
            if dem_path is None:
                base_dir = path.dirname(path.dirname(path.abspath(__file__)))  # 项目根目录
                dem_path = path.join(base_dir, 'scripts', 'ChinaDEM/China_DEM30.tif')
                # raise ValueError("DEM 文件未加载，且未提供路径。")
            self._load_dem(dem_path)

        self.dataset = DemProfileExtractor._dataset
        self.transform = DemProfileExtractor._transform
        self.res = DemProfileExtractor._res
        self.geod = Geod(ellps='WGS84')

    def _load_dem(self, path):
        DemProfileExtractor._dataset = rasterio.open(path)
        DemProfileExtractor._transform = DemProfileExtractor._dataset.transform
        DemProfileExtractor._res = DemProfileExtractor._dataset.res
        print('DEM 文件已加载')

    def extract_profile(self, xo, yo, xk, yk, elevation_array=None, base_row=None, base_col=None):
        row0, col0 = self.dataset.index(xo, yo)
        row1, col1 = self.dataset.index(xk, yk)
        pixel_path = utils.bresenham(col0, row0, col1, row1)

        cols = pixel_path[:, 0]
        rows = pixel_path[:, 1]

        L, H, D = [], [], []
        prev_lon, prev_lat = None, None
        total_dist = 0

        for i in range(len(rows)):
            r, c = rows[i], cols[i]

            # 经纬度转换
            lon, lat = xy(self.transform, r, c, offset='center')
            L.append((lon, lat))

            # elevation：使用缓存
            if elevation_array is not None:
                elev = elevation_array[r - base_row, c - base_col]
            else:
                elev = self.dataset.read(1, window=Window(c, r, 1, 1))[0, 0]

            H.append(max(elev, 0))

            if i == 0:
                D.append(0)
            else:
                _, _, dist = self.geod.inv(prev_lon, prev_lat, lon, lat)
                # dist = utils.haversine(prev_lon, prev_lat, lon, lat)
                total_dist += dist
                D.append(total_dist)

            prev_lon, prev_lat = lon, lat

        return L, H, D
    
    def prefetch_elevation(self, boundary_points):
        """
        从所有边界点确定 DEM 区域范围，读取并缓存 elevation 数组
        """
        rows, cols = zip(*[self.dataset.index(lon, lat) for lon, lat in boundary_points])
        rows = np.array(rows)
        cols = np.array(cols)

        min_row, max_row = rows.min(), rows.max()
        min_col, max_col = cols.min(), cols.max()

        window = Window(min_col, min_row, max_col - min_col + 1, max_row - min_row + 1)
        elevation_array = self.dataset.read(1, window=window)

        return elevation_array, min_row, min_col

    @classmethod
    def close(cls):
        """手动释放资源（可选）"""
        if cls._dataset:
            cls._dataset.close()
            cls._dataset = None
