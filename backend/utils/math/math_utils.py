import math
from numba import njit
import numpy as np
from rasterio.transform import xy
from pyproj import Transformer
from scipy import special

# 预先创建并缓存转换器
_transformer = None

RATE_SENSITIVITY_MAP = {
    '2.4kbps': -122,
    '9.6kbps': -116,
    '32kbps': -111,
    '64kbps': -108,
    '128kbps': -104,
    '256kbps': -101,
    '512kbps': -98,
    '1024kbps': -95,
    '2Mbps': -92,
    '4Mbps': -89,
    '8Mbps': -86,
    '16Mbps': -83,
    '34Mbps': -79,
    '50Mbps': -77,
    '78Mbps': -75,
    '100Mbps': -73,
    '155Mbps': -71,
}

# 气候类型, sigma_max(dB), k_sigma_max, sigma_min(dB), p_sigma, C_sigma, Dm(km)
LOSS_PAPAMS = {
    '大陆性亚热带': (7.2, 0.5, 2.7, 6.6, 1, 200),  # 亚热带大陆性气候
    '大陆性温带': (7.2, 0.5, 2.7, 6.6, 1, 200),  # 温带大陆性气候
    '海洋性温带陆地': (7.8, 0.375, 3.4, 20, 2, 280),  # 陆上温带海洋性气候
    '海洋': (7.8, 0.375, 3.2, 16, 1.7, 280),  # 海上温带海洋性气候
    '海洋性亚热带': (10.2, 0.33, 6.4, 8, 0.85, 300),  # 陆上亚热带海洋性气候
    '沙漠': (9, 0.45, 2.6, 9, 0.7, 225),  # 撒哈拉大沙漠
    '赤道': (6.3, 0.43, 2.3, 4.7, 0.45, 250),  # 赤道区
}

# @njit
# def nearest_visible(H, D):
#     """
#     Numba 编译的核心函数，要求 H 和 D 为 numpy 数组
#
#     输入：
#         H: 高程列表
#         D: 距离列表，单位米
#
#     输出：
#         S: 判定集合 S[i] = 1 视距, 0 非视距
#     """
#     k = len(H) - 1
#     S = np.zeros(len(H), dtype=np.uint8)
#     S[0] = 1  # 发射点默认可视
#
#     h0 = H[0]
#     d0 = D[0]
#
#     # 初始化第一个点的斜率
#     if D[1] == d0:
#         g_prev = -1e10
#     else:
#         g_prev = (H[1] - h0) / (D[1] - d0)
#
#     S[1] = 1
#     i = 2
#
#     while i <= k:
#         if D[i] == d0:
#             gi = -1e10
#         else:
#             gi = (H[i] - h0) / (D[i] - d0)
#
#         if gi >= g_prev:
#             S[i] = 1
#             g_prev = gi
#             i += 1
#         else:
#             S[i] = 0
#             i += 1
#
#             while i <= k:
#                 expected_hi = g_prev * (D[i] - d0) + h0
#                 if expected_hi > H[i]:
#                     S[i] = 0
#                     i += 1
#                 else:
#                     break
#
#     return S


@njit(cache=True)
def calculate_theta_pair(H, D):
    """
    计算发射点与接收点的仰角（单位：毫弧度）
    要求 H 和 D 为 numpy 数组

    :param H: 高程数组，起点为发射点，终点为接收点
    :param D: 距离数组，单位：米
    :return: (theta_t, theta_r) — 单位：毫弧度
    """
    h_tx = H[0]
    d_tx = D[0]
    max_slope_tx = -1e10
    for i in range(1, len(H)):
        dd = D[i] - d_tx
        if dd != 0:
            slope = (H[i] - h_tx) / dd
            if slope > max_slope_tx:
                max_slope_tx = slope
    theta_t = np.arctan(max_slope_tx) * 1000

    h_rx = H[-1]
    d_rx = D[-1]
    min_slope_rx = 1e10
    for i in range(len(H) - 1):
        dd = d_rx - D[i]
        if dd != 0:
            slope = (h_rx - H[i]) / dd
            if slope < min_slope_rx:
                min_slope_rx = slope
    theta_r = np.arctan(-min_slope_rx) * 1000

    return theta_t, theta_r


@njit(cache=True)
def calculate_theta_t(H, D):
    h_tx = H[0]
    d_tx = D[0]
    max_slope_tx = -1e10
    for i in range(1, H.shape[0]):
        dd = D[i] - d_tx
        if dd != 0:
            slope = (H[i] - h_tx) / dd
            if slope > max_slope_tx:
                max_slope_tx = slope
    theta_t = np.arctan(max_slope_tx) * 1000
    return theta_t


@njit(cache=True)
def calculate_theta_r(H, D):
    h_rx = H[-1]
    d_rx = D[-1]
    min_slope_rx = 1e10
    for i in range(H.shape[0] - 1):
        dd = d_rx - D[i]
        if dd != 0:
            slope = (h_rx - H[i]) / dd
            if slope < min_slope_rx:
                min_slope_rx = slope
    theta_r = np.arctan(-min_slope_rx) * 1000
    return theta_r


@njit
def calculate_barriers(H, D):
    """
    查找发射和接收屏障点（最高/最低斜率点）

    输入：
        H: numpy array，高程
        D: numpy array，距离（单位米）

    输出：
        (tx_d, tx_h), (rx_d, rx_h)
    """
    h_tx = H[0]
    d_tx = D[0]
    h_rx = H[-1]
    d_rx = D[-1]

    max_slope_tx = -1e10
    min_slope_rx = 1e10

    tx_d = 0.0
    tx_h = 0.0
    rx_d = 0.0
    rx_h = 0.0

    n = len(H)
    for i in range(1, n):
        dd_tx = D[i] - d_tx
        if dd_tx != 0:
            slope_tx = (H[i] - h_tx) / dd_tx
            if slope_tx > max_slope_tx:
                max_slope_tx = slope_tx
                tx_d = D[i]
                tx_h = H[i]

    for i in range(n - 1):  # 不含最后一个点
        dd_rx = d_rx - D[i]
        if dd_rx != 0:
            slope_rx = (h_rx - H[i]) / dd_rx
            if slope_rx < min_slope_rx:
                min_slope_rx = slope_rx
                rx_d = D[i]
                rx_h = H[i]

    return (tx_d, tx_h), (rx_d, rx_h)


@njit(cache=True)
def bresenham(x0: int, y0: int, x1: int, y1: int):
    max_points = abs(x1 - x0) + abs(y1 - y0) + 1
    path = np.empty((max_points, 2), dtype=np.int32)
    count = 0

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        path[count, 0] = x0
        path[count, 1] = y0
        count += 1

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return path[:count].copy()


def haversine(lon1, lat1, lon2, lat2):
    R = 6371000  # 米
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_azimuths(lat_a, lon_a, lat_b, lon_b):
    """
    计算两个点之间的相对方位角。

    参数:
    lat_a, lon_a: A点的经纬度，单位为弧度
    lat_b, lon_b: B点的经纬度，单位为弧度

    返回:
    tuple: (azimuth_ab, azimuth_ba)
           azimuth_ab: A点指向B点的方位角 (0-360度)
           azimuth_ba: B点指向A点的方位角 (0-360度)
    """
    delta_lon = lon_b - lon_a

    # 计算 A 点指向 B 点的方位角
    y = math.sin(delta_lon) * math.cos(lat_b)
    x = math.cos(lat_a) * math.sin(lat_b) - math.sin(lat_a) * math.cos(lat_b) * math.cos(delta_lon)

    # 使用 atan2 计算方位角，结果为弧度
    azimuth_ab_rad = math.atan2(y, x)

    # 转换为 0-360 度的范围
    azimuth_ab_deg = math.degrees(azimuth_ab_rad)
    azimuth_ab_deg = (azimuth_ab_deg + 360) % 360

    # 计算 B 点指向 A 点的方位角
    # 最简单的方法是利用前向方位角
    azimuth_ba_deg = (azimuth_ab_deg + 180) % 360

    return azimuth_ab_deg, azimuth_ba_deg


def find_recv_sensitivity(comm_rate):
    """
    根据通信速率获取接收灵敏度

    参数:
        comm_rate (str): 通信速率

    返回:
        int: 接收灵敏度（dBm）
    """
    return RATE_SENSITIVITY_MAP[comm_rate]


def get_transformer(tif_crs):
    global _transformer
    if _transformer is None:
        _transformer = Transformer.from_crs(tif_crs, "EPSG:3857", always_xy=True)
    return _transformer


@njit(cache=True)
def _fast_distances(xs_m, ys_m, size):
    """
    快速计算整数距离，使用预分配数组和整数运算
    """
    distances = np.zeros(size, dtype=np.int32)  # 改用整数类型
    for i in range(1, size):
        dx = xs_m[i] - xs_m[i - 1]
        dy = ys_m[i] - ys_m[i - 1]
        # 使用整数平方和开方，直接舍入到整数
        distances[i] = distances[i - 1] + int(np.sqrt(dx * dx + dy * dy))
    return distances


def calculate_distances(bresenham_points, transform, tif_crs):
    """
    快速计算路径距离，返回整数米作为单位

    :param bresenham_points: numpy.ndarray, shape=(N, 2)，像素坐标
    :param transform: rasterio.transform.Affine 仿射变换矩阵
    :param tif_crs: rasterio.crs.CRS 图像的坐标系
    :return: numpy.ndarray shape=(N,)，整数距离（米）
    """
    # 直接获取坐标值，避免复制
    xs, ys = xy(transform, bresenham_points[:, 1], bresenham_points[:, 0])
    n_points = len(xs)

    # 如果是地理坐标系，转换到米制
    if tif_crs.is_geographic:
        transformer = get_transformer(tif_crs)
        # 直接转换为 float32 类型，减少精度但提高速度
        xs_m, ys_m = transformer.transform(xs, ys)
        xs_m = np.array(xs_m, dtype=np.float32)
        ys_m = np.array(ys_m, dtype=np.float32)
    else:
        # 直接使用float32
        xs_m = np.array(xs, dtype=np.float32)
        ys_m = np.array(ys, dtype=np.float32)

    # 计算整数距离
    return _fast_distances(xs_m, ys_m, n_points)


@njit(cache=True)
def nearest_visible(H, D):
    k = H.shape[0] - 1
    S = np.ones(k + 1, dtype=np.int8)
    h0 = H[0]
    d0 = D[0]
    g_prev = (H[1] - h0) / (D[1] - d0)
    i = 1
    while i <= k:
        gi = (H[i] - h0) / (D[i] - d0)
        if gi >= g_prev:
            S[i] = 1
            g_prev = gi
            i += 1
        else:
            S[i] = 0
            i += 1
            while i <= k and (g_prev * (D[i] - d0) + h0) > H[i]:
                S[i] = 0
                i += 1
    return S


def calculate_reliability(d_km, area, M0):
    if area in LOSS_PAPAMS:
        sigma_max, k_sigma_max, sigma_min, p_sigma, C_sigma, Dm = LOSS_PAPAMS[area]
    else:
        sigma_max, k_sigma_max, sigma_min, p_sigma, C_sigma, Dm = LOSS_PAPAMS['海洋性温带陆地']
    if d_km <= Dm:
        sigma = sigma_max * (math.sin(math.radians(k_sigma_max * d_km)) ** 2)
    else:
        sigma = sigma_min + p_sigma * math.exp(-1e6 * C_sigma * (d_km ** 2))

    # M0 = 1.0
    residual_value_M_0 = M0 / sigma  # 归一化电平余量

    reliability = 0.5 * (1 + special.erf(residual_value_M_0 / math.sqrt(2))) * 100  # 传播可靠度

    return round(reliability, 2)
