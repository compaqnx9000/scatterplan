from os import path
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.transform import rowcol, xy
from sklearn.cluster import DBSCAN
# from sklearn.metrics import pairwise_distances
from collections import defaultdict
from django.conf import settings


class ClusteringAnalysis:
    def __init__(self, tif_path, min_lon, min_lat, max_lon, max_lat, loss_threshold, eps_m, min_samples, p=50):
        """
        初始化站点规划器

        参数：
            tif_path (str): GeoTIFF 文件路径
            loss_threshold (int): 阈值，单位 dB
            eps_m (int): DBSCAN 的邻域半径（单位：米）
            min_samples (int): DBSCAN 中的最小样本数
            p (int): 保留字段
        """
        self.min_lon, self.min_lat = min_lon, min_lat
        self.max_lon, self.max_lat = max_lon, max_lat
        self.loss_threshold = int(loss_threshold)  # 单位：dB
        self.eps = round(float(eps_m) / 6371000.0, 6)  # 单位米转弧度
        self.min_samples = int(min_samples)  # 单位：个
        self.p = int(p)  # 未使用，可用于后续可靠性指标

        self.coords = None  # 符合阈值的经纬度点
        self.loss_values = None  # 对应的损耗值
        self.cluster_area_data = None

        # 读取 GeoTIFF 数据
        self._read_tiff(tif_path)

    def _read_tiff(self, tif_path):
        abs_path = path.join(settings.MEDIA_ROOT, tif_path[7:])

        if not path.exists(abs_path):
            raise FileNotFoundError(f"GeoTIFF 文件不存在: {abs_path}")

        with rasterio.open(abs_path) as dataset:
            # self.tif_transform = dataset.transform  # 仿射变换矩阵
            # self.tif_crs = dataset.crs  # 投影信息
            # self.tif_width = dataset.width  # 栅格宽度
            # self.tif_height = dataset.height  # 栅格高度
            # self.tif_bands = dataset.count  # 波段数
            self.nodata = dataset.nodata  # 无数据值

            # 计算窗口（根据地理坐标获取对应的像素窗口）
            window = from_bounds(
                self.min_lon, self.min_lat, self.max_lon, self.max_lat,
                transform=dataset.transform
            ).round_offsets().round_lengths()  # 确保是整数像素区域

            # 读取单波段数据
            self.cluster_area_data = dataset.read(1, window=window)
            # 获取窗口的像素起始点和仿射变换
            self.area_transform = dataset.window_transform(window)

    def _filter_data(self):
        """
        从 GeoTIFF 中提取满足 loss 阈值的有效像素点，并转换为经纬度坐标
        使用 NumPy 向量化操作以提高效率
        """
        # 创建掩膜：过滤出符合条件的像素（即小于等于阈值，且不为无效值）
        mask = (self.cluster_area_data <= self.loss_threshold) & (self.cluster_area_data != self.nodata)
        rows, cols = np.where(mask)

        # 将行列索引转换为经纬度（矢量化处理）
        lons, lats = xy(self.area_transform, rows, cols)

        # 组合为 Nx2 的经纬度数组
        self.coords = np.column_stack((lons, lats))
        # 保存对应的损耗值
        self.loss_values = self.cluster_area_data[rows, cols]

    def cut_cicle(self, center_lon, center_lat, radius_m):
        """裁剪圆形区域内的点 将area_transform转为圆形矩阵"""
        # 如果数据还未过滤，则先提取符合阈值的点
        if self.coords is None:
            self._filter_data()

        # 计算每个点到中心的球面距离（使用 haversine 公式）
        # 将经纬度转换为弧度
        lat1 = np.radians(center_lat)
        lon1 = np.radians(center_lon)
        lat2 = np.radians(self.coords[:, 1])
        lon2 = np.radians(self.coords[:, 0])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        distance_m = 6371000.0 * c  # 地球半径，单位：米

        # 筛选在圆形区域内的点（距离小于等于半径）
        mask = distance_m <= radius_m
        self.coords = self.coords[mask]
        self.loss_values = self.loss_values[mask]

    def get_elevation(self, lon, lat):
        row, col = rowcol(self.area_transform, lon, lat)
        total_rows, total_cols = self.cluster_area_data.shape
        if 0 <= row < total_rows and 0 <= col < total_cols:
            return float(self.cluster_area_data[row, col])
        else:
            return 0  # 可根据需求设默认值

    def cluster(self):
        """执行 DBSCAN 聚类，计算中心点和高程"""
        if self.coords is None:
            self._filter_data()

        # 经纬度 -> 弧度
        coords_rad = np.radians(self.coords)

        if coords_rad.shape[0] == 0:
            return []

        # DBSCAN 聚类
        db = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric='haversine')
        labels = db.fit_predict(coords_rad)

        # 聚类统计
        clusters = defaultdict(list)
        loss_clusters = defaultdict(list)

        for i, label in enumerate(labels):
            if label != -1:
                clusters[label].append(self.coords[i])
                loss_clusters[label].append(self.loss_values[i])

        cluster_stats = []
        for label, pts in clusters.items():
            pts = np.array(pts)
            center = pts.mean(axis=0)  # 平均经纬度
            # 经纬度保留小数点6位
            center = np.round(center, 6)
            elevation = self.get_elevation(center[0], center[1])

            losses = np.array(loss_clusters[label])
            min_loss_idx = np.argmin(losses)  # 找到最低损耗值的索引
            min_loss_point = np.round(pts[min_loss_idx], 6)
            min_loss_value = round(float(losses[min_loss_idx]), 2)
            min_loss_evl = self.get_elevation(min_loss_point[0], min_loss_point[1])

            cluster_stats.append({
                "cluster": label,
                "num_points": len(pts),
                "center": center.tolist(),  # 转为 list，方便 JSON 序列化
                "elevation": round(elevation, 2),
                "min_loss_point": min_loss_point.tolist(),  # 最低损耗点坐标
                "min_loss_value": min_loss_value,           # 最低损耗值
                "min_loss_evl": min_loss_evl,
            })

        return cluster_stats

    def reset_area_data(self, area_data):
        self.cluster_area_data = area_data
