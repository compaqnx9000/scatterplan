from os import path

import numpy as np
import rasterio
from rasterio.transform import xy
from rasterio.windows import Window
from pyproj import Geod
from django.conf import settings

from utils.math import math_utils as utils
from scripts.models import calculate_loss

# 气候区参数表（根据ITU-R P.617-3表2定义）
CLIMATE_PARAMS = {
    0: (26.00, 0.27, 8, '海洋'),
    1: (39.60, 0.33, 9, '赤道'),
    2: (29.73, 0.27, 7, '大陆性亚热带'),
    3: (19.30, 0.32, 10, '海洋性亚热带'),
    4: (38.50, 0.27, 11, '沙漠'),
    5: (29.73, 0.27, 7, '大陆性温带'),
    6: (33.20, 0.27, 7, '海洋性温带陆地'),
}


class ClimateLossCalculator2:
    def __init__(self, climate_num):
        self.coords = None
        self.climate_num = climate_num


        self._read_climate_file()

    def _read_climate_file(self):
        tropo_clim_path = path.join(settings.WORKING_DIR, 'data', 'TropoClim.txt')
        if not path.exists(tropo_clim_path):
            raise FileNotFoundError(f"{tropo_clim_path} 不存在")

        self.climate_data = np.loadtxt(tropo_clim_path, dtype=np.int8)

        # 计算数据尺寸
        # rows, cols = self.climate_data.shape  # 行数（纬度方向）列数（经度方向）

    def extract_profile(self, xo, yo, xk, yk, progress_callback=None):
        """提取两点间剖面信息（经纬度、高程、距离）"""
        def _progress(value):
            if progress_callback:
                progress_callback(value)

        tif_path = settings.DEM_PATH
        if not path.exists(tif_path):
            raise FileNotFoundError(f"{tif_path} 不存在")

        _progress(0.08)
        with rasterio.open(tif_path) as dataset:
            transform = dataset.transform
            nodata_value = dataset.nodata

            # 坐标转换为行列号
            row0, col0 = dataset.index(xo, yo)
            row1, col1 = dataset.index(xk, yk)
            _progress(0.18)

            # 使用布雷森汉姆算法生成像素路径
            pixel_path = utils.bresenham(col0, row0, col1, row1)
            cols, rows = pixel_path[:, 0], pixel_path[:, 1]
            _progress(0.32)

            # 批量读取高程值
            row_min, row_max = rows.min(), rows.max()
            col_min, col_max = cols.min(), cols.max()
            window = Window(col_min, row_min, col_max - col_min + 1, row_max - row_min + 1)
            dem_data = dataset.read(
                1,
                window=window,
                boundless=True,
                fill_value=0
            )
            _progress(0.62)

            # 批量计算经纬度
            xs, ys = xy(transform, rows, cols, offset="center")
            _progress(0.78)

        # 从子窗口中提取对应像素高程
        elevs = dem_data[rows - row_min, cols - col_min]
        if nodata_value is not None:
            # print(f'nodata {nodata_value}')
            elevs = np.where(elevs == nodata_value, 0, elevs)
        # print(f'总数 {len(elevs)}')
        elevs = np.maximum(elevs, 0)  # 负值设为 0
        xs, ys = np.array(xs), np.array(ys)

        # 计算沿线距离
        geod = Geod(ellps='WGS84')
        fwd_az, back_az, dist = geod.inv(xs[:-1], ys[:-1], xs[1:], ys[1:])
        distances = np.concatenate(([0], np.cumsum(dist)))
        _progress(0.92)

        # 起点→终点方位角、终点→起点方位角、总距离(m)
        azimuth_fwd, azimuth_back, total_distance = geod.inv(xo, yo, xk, yk)
        # 规范化为 0-360 度
        azimuth_fwd = (azimuth_fwd + 360.0) % 360.0
        azimuth_back = (azimuth_back + 360.0) % 360.0

        # 返回结果：经纬度、高程、距离
        self.coords = np.column_stack((xs, ys))
        elevs = elevs.astype(np.int16)
        distances = distances.astype(np.float32)
        _progress(1.0)

        return azimuth_fwd, azimuth_back, elevs, distances

    def _get_climate_num(self, lon, lat):
        """
        获取指定经纬度位置的气候区代码

        :param lon: 经度（单位：度）
        :param lat: 纬度（单位：度）
        :return: 气候区代码（0-6，根据ITU-R P.617-3定义）
        """

        # 数据参数（根据ITU-R P.617-3标准定义）
        lat_start = 89.75  # 起始纬度（北纬，度）
        lon_start = -179.75  # 起始经度（西经，度）
        resolution = 0.5  # 数据分辨率（度）

        # 计算行索引（纬度从北到南递减）
        # 公式：行索引 = (起始纬度 - 目标纬度) / 分辨率
        row = int((lat_start - lat) / resolution)

        # 计算列索引（经度从西到东递增）
        # 公式：列索引 = (目标经度 - 起始经度) / 分辨率
        col = int((lon - lon_start) / resolution)

        # 检查索引是否在有效范围内
        # if 0 <= row < rows and 0 <= col < cols:
        #     return self.climate_data[row, col]
        # else:
        #     # 超出边界返回默认值
        #     return 0
        return self.climate_data[row, col]

    def compute_barriers_and_scatterer(self, elevs, distances, theta_t, theta_r):
        """
        计算剖面中的障碍点（最大斜率）及散射点（若给定发射/接收角）

        参数：
            theta_t : float | None
                发射端仰角（毫弧度）
            theta_r : float | None
                接收端俯角（毫弧度）
        返回：
            tx_barrier : (d, h)
            rx_barrier : (d, h)
            scatterer_point : (d, h) or None
            scatterer_lonlat : (lon, lat) or None
        """

        coords = np.asarray(self.coords)
        elevs = np.asarray(elevs)
        dists = np.asarray(distances)

        # --- 发射端障碍 ---
        d_tx, h_tx = dists[0], elevs[0]
        slopes_tx = (elevs[1:] - h_tx) / (dists[1:] - d_tx)
        max_idx_tx = np.argmax(slopes_tx)
        tx_barrier = (dists[max_idx_tx + 1], elevs[max_idx_tx + 1])

        # --- 接收端障碍 ---
        d_rx, h_rx = dists[-1], elevs[-1]
        slopes_rx = (h_rx - elevs[:-1]) / (d_rx - dists[:-1])
        min_idx_rx = np.argmin(slopes_rx)
        rx_barrier = (dists[min_idx_rx], elevs[min_idx_rx])

        # --- 散射点计算 ---
        # 两端点
        k_t = np.tan(theta_t / 1000.0)
        k_r = np.tan(-theta_r / 1000.0)

        # 若两条射线几乎平行，取中点
        if abs(k_t - k_r) < 1e-9:
            x = (d_tx + d_rx) / 2
            y = (h_tx + h_rx) / 2
        else:
            b1 = h_tx - k_t * d_tx
            b2 = h_rx - k_r * d_rx
            x = (b2 - b1) / (k_t - k_r)
            y = k_t * x + b1

        scatterer_point = (x, y)

        # 在线性距离序列中插值经纬度
        if dists[0] <= x <= dists[-1]:
            i = np.searchsorted(dists, x) - 1
            i = np.clip(i, 0, len(dists) - 2)
            ratio = (x - dists[i]) / (dists[i + 1] - dists[i])
            lon = coords[i, 0] + ratio * (coords[i + 1, 0] - coords[i, 0])
            lat = coords[i, 1] + ratio * (coords[i + 1, 1] - coords[i, 1])
            scatterer_lonlat = (lon, lat)
        else:
            scatterer_lonlat = coords[-1]  # 超出范围则返回终点

        # print(f"散射体坐标: {scatterer_point}")
        return tx_barrier, rx_barrier, scatterer_point, scatterer_lonlat

    def calculate_path_loss(self, freq, tx_gain, rx_gain, elevs, distances, diversity_order):
        diversity_order_loss = (diversity_order - 1) * 3

        S = utils.nearest_visible(elevs, distances)
        print(f"点数: {len(S)}")

        d_km = max(distances[-1] / 1000.0, 1e-6)

        if self.climate_num is None:
            climate_num = self._get_climate_num(self.coords[0, 0], self.coords[0, 1])
        else:
            climate_num = int(self.climate_num)

        # 获取气候参数
        M, gamma, _, climate_area = CLIMATE_PARAMS[climate_num]

        # 计算散射角
        theta_t, theta_r = utils.calculate_theta_pair(elevs, distances)
        theta_scatter = calculate_loss.calculate_scatter_angle(d_km, theta_t, theta_r)

        if S[-1]:
            loss = 20 * np.log10(d_km) + 20 * np.log10(freq) + 32.45 - diversity_order_loss
        else:
            # 散射体损耗 Ln
            Ln, _ = calculate_loss.estimate_Ln(theta_scatter, d_km, gamma)

            # 天线口径耦合损耗 Lc
            exponent = 0.055 * (tx_gain + rx_gain)
            Lc = 0.07 * np.exp(exponent)
            # print(f'lc {Lc}')

            # 综合损耗公式
            loss = (
                M
                + 30 * np.log10(freq)
                + 10 * np.log10(d_km)
                + 30 * np.log10(max(theta_scatter, 1e-6))
                + Ln
                + Lc
                # - tx_gain
                # - rx_gain
                - diversity_order_loss
            )

        return loss, climate_area, theta_t, theta_r, theta_scatter
