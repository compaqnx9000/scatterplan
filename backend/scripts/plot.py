# -*- coding:utf-8 -*-
import math
from os import path
# import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import zoom
from numba import jit
# from osgeo import gdal

# gdal.UseExceptions()

BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))  # 项目根目录
# 气候区参数表（根据ITU-R P.617-3表2定义）
CLIMATE_PARAMS = np.array([
    (26.00, 0.27, 8, '海洋'),
    (39.60, 0.33, 9, '赤道'),
    (29.73, 0.27, 7, '大陆性亚热带'),  # 沙漠
    (19.30, 0.32, 10, '海洋性亚热带'),
    (38.50, 0.27, 11, '大陆性温带'),
    (29.73, 0.27, 7, '海洋性温带'),
    (33.20, 0.27, 7, '极地'),
], dtype=[('M', np.float64), ('gamma', np.float64), ('Y90_equation', np.int32), ('climate_type', 'U20')])


@jit(nopython=True)
def single_road_count(dist, height, flag, freq, zone):
    M = CLIMATE_PARAMS[zone]['M']
    gamma = CLIMATE_PARAMS[zone]['gamma']

    length = dist.shape[0]
    dist_ceil = dist[1]

    path_loss = np.zeros(length)
    scatter_cube_X = np.zeros(length)
    scatter_cube_H1 = np.zeros(length)
    scatter_cube_H2 = np.zeros(length)

    # 发射端参数计算
    height_op = height[::-1] - height[-1]
    dist_op = dist[::-1]
    slope_tran_list = height_op / dist
    slope_tran_list[0] = 0
    slope_tran = np.max(slope_tran_list)
    if slope_tran < 0:
        slope_tran = 0
    scatter_tran = np.arctan(slope_tran)
    slope_tran = slope_tran * -1
    bias_tran = height[-1] - slope_tran * dist_op[0]

    sub_len = min(length, 300)
    # 接收端参数计算
    slope_re = np.zeros(length)
    sub_dist = dist[0:sub_len]

    for i in range(0, length - sub_len):
        sub_height = height[i:i + sub_len]
        sub_height = sub_height - sub_height[0]  # 规划起始点为原点简化计算
        asd = sub_height / sub_dist
        asd[0] = 0
        slope_re[i] = np.max(asd)
        if slope_re[i] < 0:
            slope_re[i] = 0

    for j in range(length - sub_len, length - 1):
        # for j in range(296, length - 1):
        sub_height = height[j:j + sub_len]
        sub_height = sub_height - sub_height[0]
        sub_dist = dist[0:length - j]
        asd = sub_height / sub_dist
        asd[0] = 0
        slope_re[j] = np.max(asd)
        if slope_re[j] < 0:
            slope_re[j] = 0

    slope_re = slope_re + 0.00001
    scatter_re = np.arctan(slope_re)
    scatter = scatter_re + scatter_tran
    scatter = np.radians(scatter)

    # 链路所有单点计算
    for k in range(length - 1):
        if flag[k]:
            # path_loss[k] = 100
            if dist_op[k] == 0:
                path_loss[k] = 0
            else:
                path_loss[k] = 32.45 + 20 * math.log10(dist_op[k]) + 20 * math.log10(freq)

        else:
            scatter_cube_X[k] = (
                bias_tran + k * dist_ceil * slope_tran - height[k]
            ) / (slope_re[k] - slope_tran)

            scatter_cube_H2[k] = (
                scatter_cube_X[k] * slope_re[k] + height[k]
            ) * 0.001  # - height[k]  # 高度转换为 km  # 修改

            scatter_cube_H1[k] = get_distance_from_point_to_line(
                scatter_cube_X[k], scatter_cube_H2[k],
                dist[0], height[0],
                dist[-1], height[-1]
            ) * 0.001  # 修改

            path_loss[k] = (
                M +
                30 * np.log10(freq) +
                10 * np.log10(dist_op[k]) +
                30 * np.log10(1000 * scatter[k]) +
                20 * np.log10(5 + gamma * scatter_cube_H1[k]) + 4.343 * gamma * scatter_cube_H2[k]  # Ln
            )  # 修改

    path_loss[length - 1] = 0

    return path_loss


@jit(nopython=True)
def point_to_line_sight(height):
    height = height - height[0]
    length = height.shape[0] - 1
    i = np.int32(1)
    flag = np.zeros((length,), dtype=np.bool_)
    flag[0] = True
    flag[1] = True
    slope_p = height[1]

    while i < length:
        slope_i = height[i] / i
        if slope_i > slope_p:
            slope_p = slope_i
            flag[i] = True
        i += 1

    return flag


@jit(nopython=True)
def get_distance_from_point_to_line(point_X, point_Y, x1, y1, x2, y2):
    # 计算直线的三个参数
    A = y2 - y1
    B = x1 - x2
    C = (y1 - y2) * x1 + (x2 - x1) * y1
    # 根据点到直线的距离公式计算距离
    distance = np.abs(A * point_X + B * point_Y + C) / (np.sqrt(A ** 2 + B ** 2))
    return distance


# def write_tiff(im_data, im_width, im_height, im_bands, im_geotrans, im_proj, path):
#     if 'int8' in im_data.dtype.name:
#         datatype = gdal.GDT_Byte
#     elif 'int16' in im_data.dtype.name:
#         datatype = gdal.GDT_UInt16
#     elif 'int32' in im_data.dtype.name:
#         datatype = gdal.GDT_UInt32
#     else:
#         datatype = gdal.GDT_Float32
#
#     if len(im_data.shape) == 3:
#         im_bands, im_height, im_width = im_data.shape
#     elif len(im_data.shape) == 2:
#         im_data = np.array([im_data])
#     else:
#         im_bands, (im_height, im_width) = 1, im_data.shape
#
#     # 创建文件
#     driver = gdal.GetDriverByName("GTiff")
#     dataset = driver.Create(path, im_width, im_height, im_bands, datatype)
#
#     if dataset is not None:
#         dataset.SetGeoTransform(im_geotrans)
#         dataset.SetProjection(im_proj)
#
#         for i in range(im_bands):
#             band = dataset.GetRasterBand(i + 1)
#             band.WriteArray(im_data[i])
#             band.SetNoDataValue(0)  # 设置 NoData 值
#
#     del dataset


# def read_tif(min_lng, min_lat, max_lng, max_lat):
#     # tif_path = "D:/code/scattering/scripts/ChinaDEM/China_DEM30.tif"
#     tif_path = path.join(BASE_DIR, 'scripts', 'ChinaDEM/China_DEM30.tif')
#
#     dataset = gdal.Open(tif_path)
#     if dataset is None:
#         print(tif_path + "文件无法打开")
#         return
#
#     im_width = dataset.RasterXSize  # 栅格矩阵的列数
#     im_height = dataset.RasterYSize  # 栅格矩阵的行数
#     im_bands = dataset.RasterCount  # 波段数
#     im_geotrans = dataset.GetGeoTransform()  # 获取仿射矩阵信息
#
#     # 计算经纬度对应的栅格索引
#     int_min_lng = int((min_lng - im_geotrans[0]) / im_geotrans[1])
#     int_max_lng = int((max_lng - im_geotrans[0]) / im_geotrans[1])
#     int_min_lat = int((max_lat - im_geotrans[3]) / im_geotrans[5])  # 注意纬度是反向的
#     int_max_lat = int((min_lat - im_geotrans[3]) / im_geotrans[5])
#
#     # 确保索引在有效范围内
#     int_min_lng = max(0, int_min_lng)
#     int_max_lng = min(im_width, int_max_lng)
#     int_min_lat = max(0, int_min_lat)
#     int_max_lat = min(im_height, int_max_lat)
#
#     # 读取指定范围的数据
#     im_data = dataset.ReadAsArray(int_min_lng, int_min_lat, int_max_lng - int_min_lng, int_max_lat - int_min_lat)
#
#     im_proj = dataset.GetProjection()  # 获取投影信息
#     del dataset  # 关闭对象，文件dataset
#     return im_proj, im_geotrans, im_data, int_max_lat - int_min_lat, int_max_lng - int_min_lng, im_bands


def read_climate_zone(min_lng, min_lat, max_lng, max_lat, row, col):
    # file_path = "D:/code/scattering/scripts/TropoClim.txt"
    file_path = path.join(BASE_DIR, 'scripts', 'TropoClim.txt')
    data = np.loadtxt(file_path, dtype=np.uint8)

    lat_start = 89.75  # 起始纬度（北纬，度）
    lon_start = -179.75  # 起始经度（西经，度）
    resolution = 0.5  # 数据分辨率（度）

    # 计算经纬度索引
    lat_idx_start = int((lat_start - min_lat) / resolution)
    lat_idx_end = int((lat_start - max_lat) / resolution)
    lon_idx_start = int((min_lng - lon_start) / resolution)
    lon_idx_end = int((max_lng - lon_start) / resolution)

    # 通过索引裁剪相应的区域
    cropped_data = data[lat_idx_end:lat_idx_start + 1, lon_idx_start:lon_idx_end + 1]

    # 使用 zoom 函数来进行插值重采样
    # cropped_data = zoom(cropped_data, (row / cropped_data.shape[0], col / cropped_data.shape[1]))
    return cropped_data
