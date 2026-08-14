# import math
from os import path
import time

import numpy as np
import rasterio
# from rasterio.transform import rowcol, xy
from rasterio.windows import from_bounds
from pyproj import Geod
# from pyproj import Transformer, CRS
# from shapely.geometry import Point, box
# import geopandas as gpd
from django.conf import settings

from utils.math import math_utils as utils
from scripts.models.calculate_loss import calculate_area_loss


class CoveragePlanner2:
    def __init__(self, tx_lon, tx_lat, min_lon, min_lat, max_lon, max_lat, freq_mhz, climate_num=None):
        """
        CoveragePlanner 初始化
        :param min_lon: 区域左下角经度
        :param min_lat: 区域左下角纬度
        :param max_lon: 区域右上角经度
        :param max_lat: 区域右上角纬度
        :param freq_mhz: 通信频率（MHz）
        """
        self.freq = freq_mhz
        self.min_lon, self.min_lat = min_lon, min_lat
        self.max_lon, self.max_lat = max_lon, max_lat
        self.boundary_pts = []

        self._read_dem()
        self._read_climate_zone()

        self.tx_row = int((self.max_lat - tx_lat) / -self.area_transform[4])
        self.tx_col = int((tx_lon - self.min_lon) / self.area_transform[0])

        if climate_num is not None:
            self.climate_num = climate_num
        else:
            self.climate_num = None
            self.tx_zone = self._compute_climate_offset(self.tx_row, self.tx_col)
            print(f'发射气候编号 {self.tx_zone}')

        self.loss_arr = np.zeros((self.area_rows, self.area_cols), dtype=np.uint16)
    
    def _read_dem(self):
        """
        读取数字高程模型数据，并裁剪出对应区域的高程矩阵。
        """
        # tif_path = path.join(BASE_DIR, 'scripts', 'ChinaDEM/China_DEM30.tif')
        tif_path = settings.DEM_PATH

        if not path.exists(tif_path):
            print(tif_path + " 文件不存在")
            return

        with rasterio.open(tif_path) as dataset:
            # self.tif_transform = dataset.transform  # 仿射变换矩阵
            self.tif_crs = dataset.crs  # 投影信息
            # self.tif_width = dataset.width  # 栅格宽度
            # self.tif_height = dataset.height  # 栅格高度
            self.tif_bands = dataset.count  # 波段数
            self.nodata_value = dataset.nodata

            # 计算窗口（根据地理坐标获取对应的像素窗口）
            window = from_bounds(self.min_lon, self.min_lat, self.max_lon, self.max_lat, transform=dataset.transform)
            window = window.round_offsets().round_lengths()  # 确保是整数像素区域

            # 读取单波段数据
            self.area_dem_data = dataset.read(
                1,
                window=window,
                boundless=True,
                fill_value=0
            )
            if self.nodata_value is not None:
                # print(f'nodata {self.nodata_value}')
                self.area_dem_data = np.where(self.area_dem_data == self.nodata_value, 0, self.area_dem_data)

            # 获取窗口的像素起始点和仿射变换
            self.area_transform = dataset.window_transform(window)

        self.area_rows, self.area_cols = self.area_dem_data.shape
        # 获取一格代表的实际距离
        self.distance_ceil = min(self.area_transform[0], -self.area_transform[4]) * 111000

    def _read_climate_zone(self):
        """
        读取气候区数据，并裁剪出对应区域的气候区矩阵。
        气候区数据文件 TropoClim.txt 来自 ITU-R P.681-14 附录 1
        89.75N -179.75W 起始点，0.5度分辨率，共 360 行 720 列
        """
        # file_path = "D:/code/scattering/data/TropoClim.txt"
        file_path = path.join(settings.WORKING_DIR, 'data', 'TropoClim.txt')
        data = np.loadtxt(file_path, dtype=np.uint8)

        lat_start = 89.75  # 起始纬度（北纬，度）
        lon_start = -179.75  # 起始经度（西经，度）
        resolution = 0.5  # 数据分辨率（度）

        # 计算经纬度索引
        lat_idx_start = int((lat_start - self.min_lat) / resolution)
        lat_idx_end = int((lat_start - self.max_lat) / resolution)
        lon_idx_start = int((self.min_lon - lon_start) / resolution)
        lon_idx_end = int((self.max_lon - lon_start) / resolution)

        # 通过索引裁剪相应的区域
        self.climate_zone = data[lat_idx_end:lat_idx_start + 1, lon_idx_start:lon_idx_end + 1]
        self.climate_rows, self.climate_cols = self.climate_zone.shape

    def _compute_climate_offset(self, area_row, area_col):
        """
        根据区域内的行列索引，计算对应的气候区类型。
        :param area_row: 区域内的行索引
        :param area_col: 区域内的列索引
        :return: 气候区类型（整数）
        """
        # 计算比例映射
        zone_row_idx = round((area_row + 1) / self.area_rows * self.climate_rows) - 1  # 映射到气候区的行索引
        zone_col_idx = round((area_col + 1) / self.area_cols * self.climate_cols) - 1  # 映射到气候区的列索引
        return self.climate_zone[zone_row_idx, zone_col_idx]

    @staticmethod
    def sample_rectangle(rows, cols):
        """
        采样矩形边界的像元坐标。
        :param rows: 区域行数
        :param cols: 区域列数
        :return: list[(row, col)]
        """
        boundary_pts = []
        for col in range(cols):
            boundary_pts.append((0, col))  # 上边界
            boundary_pts.append((rows - 1, col))  # 下边界

        for row in range(rows):
            boundary_pts.append((row, 0))  # 左边界
            boundary_pts.append((row, cols - 1))  # 右边界

        return boundary_pts

    def _compute_profile_loss(self, boundary_row, boundary_col):
        """
        计算单条链路的路径剖面及信号损耗
        :param boundary_row: 边界点的行索引
        :param boundary_col: 边界点的列索引
        """
        # 散射通信链路剖面提取
        point_line = utils.bresenham(self.tx_row, self.tx_col, boundary_row, boundary_col)
        x_coords, y_coords = point_line[:, 0], point_line[:, 1]

        # 距离
        distances = utils.calculate_distances(point_line, self.area_transform, self.tif_crs)

        # 批量获取高度值
        height = self.area_dem_data[x_coords, y_coords]

        # 判断视距
        flag = utils.nearest_visible(height, distances)

        # 气候区
        if self.climate_num is not None:
            climate_num = self.climate_num
        else:
            rx_zone = self._compute_climate_offset(boundary_row, boundary_col)
            climate_num = min(self.tx_zone, rx_zone)

        losses = calculate_area_loss(distances, height, flag, self.freq, climate_num)

        self.loss_arr[x_coords, y_coords] = losses

    def plan_rectangle_coverage(self, task_id, progress_callback):
        print(f'矩形区域共 {self.area_rows} 行，{self.area_cols} 列像素点')

        process = 0
        process_all = self.area_rows + self.area_cols
        last_send_time = 0
        for i in range(self.area_cols):
            self._compute_profile_loss(0, i)  # 上边界
            self._compute_profile_loss(self.area_rows - 1, i)  # 下边界

            # 更新进度
            process += 1
            current_time = time.time()
            if current_time - last_send_time > 0.5:
                progress_callback(task_id, 'coverage progress', 0.99 * process / process_all)
                last_send_time = current_time

        for i in range(self.area_rows):
            self._compute_profile_loss(i, self.area_cols - 1)  # 右边界
            self._compute_profile_loss(i, 0)  # 左边界

            # 更新进度
            process += 1
            current_time = time.time()
            if current_time - last_send_time > 0.5 or process == process_all:
                progress_callback(task_id, 'coverage progress', 0.99 * process / process_all)
                last_send_time = current_time

    def plan_circle_coverage(self, center_lon, center_lat, radius_m, task_id, progress_callback):
        geod = Geod(ellps="WGS84")

        # 圆周长度
        circumference = 2 * np.pi * radius_m
        # 保底至少8条射线
        num_rays = max(8, round(circumference / self.distance_ceil))
        angle_step = 360 / num_rays
        print(f"圆周共 {num_rays} 点")

        last_send_time = 0
        for i in range(num_rays):
            azimuth = i * angle_step
            end_lon, end_lat, _ = geod.fwd(center_lon, center_lat, azimuth, radius_m)

            # 将经纬度转换为图像像素坐标
            dx = int((end_lon - self.min_lon) / self.area_transform[0])
            dy = int((self.max_lat - end_lat) / -self.area_transform[4])

            # 限制在图像边界内
            dx = max(0, min(dx, self.area_cols - 1))
            dy = max(0, min(dy, self.area_rows - 1))

            self._compute_profile_loss(dy, dx)

            current_time = time.time()
            # 更新进度
            if current_time - last_send_time > 0.5 or i == num_rays - 1:
                progress_callback(task_id, 'coverage progress', 0.99 * (i + 1) / num_rays)
                last_send_time = current_time

    def write_tiff(self, tif_path):
        # print(f'最大损耗: {np.max(self.loss_arr)} dB，平均损耗: {np.mean(self.loss_arr):.2f} dB')
        with rasterio.open(
                tif_path, 'w',
                driver='GTiff',  # 输出格式
                count=1,  # 波段数
                dtype=self.loss_arr.dtype,  # 数据类型
                crs=self.tif_crs,  # 投影坐标系
                transform=self.area_transform,  # 仿射变换矩阵
                width=self.area_cols,  # 栅格的宽度
                height=self.area_rows,  # 栅格的高度
                nodata=0,  # 设置 NoData 值
        ) as dataset:
            # 写入损耗数据
            dataset.write(self.loss_arr, 1)

    def get_loss_arr(self):
        return self.loss_arr
