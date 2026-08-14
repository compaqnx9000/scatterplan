import numpy as np
import math
from os import path
from time import time
from pyproj import Geod
from rasterio.transform import rowcol, xy
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from scripts.dem_profile_extractor import DemProfileExtractor
from scripts.los_loss_calculator import LosLossCalculator
from scripts.nlos_loss_calculator import NLosLossCalculator


class CoveragePlanner:
    def __init__(self, freq_mhz):
        """
        CoveragePlanner 初始化：
        - freq_mhz：通信频率（MHz）
        """
        self.extractor = DemProfileExtractor()
        self.losCalculator = LosLossCalculator(freq_mhz)
        self.nLosCalculator = NLosLossCalculator(Gt=0, Gr=0, freq_mhz=freq_mhz)

    # @staticmethod
    # def sample_rectangle(corner1, corner2, res_lon, res_lat):
    #     """
    #     根据实际分辨率，按像素边界均匀采样矩形边界上的点。
    #     :param corner1: 左下角坐标 (lon1, lat1)
    #     :param corner2: 右上角坐标 (lon2, lat2)
    #     :param res_lon: 经度分辨率（单位：度）
    #     :param res_lat: 纬度分辨率（单位：度）
    #     """
    #     lon1, lat1 = corner1
    #     lon2, lat2 = corner2
    #
    #     # 生成边界上的采样点（与像素边界一致）
    #     lons = np.arange(lon1, lon2 + res_lon, res_lon)
    #     lats = np.arange(lat1, lat2 + res_lat, res_lat)
    #     print(f'{len(lons)}个经度点，{len(lats)}个纬度点')
    #
    #     pts = []
    #     # 下边
    #     pts += list(zip(lons, [lat1] * len(lons)))
    #     # 上边
    #     pts += list(zip(lons, [lat2] * len(lons)))
    #     # 左边（排除角点）
    #     pts += list(zip([lon1] * len(lats), lats))[1:-1]
    #     # 右边（排除角点）
    #     pts += list(zip([lon2] * len(lats), lats))[1:-1]
    #
    #     return pts, (len(lons), len(lats))
    def sample_rectangle(self, lon1, lat1, lon2, lat2):
        """
        给定两个地理坐标点，采样对应矩形区域的边界坐标点。

        :param lon1: 左下角或右上角经度
        :param lat1: 左下角或右上角纬度
        :param lon2: 另一个对角点经度
        :param lat2: 另一个对角点纬度
        :return: [(lon, lat), ...] 边界坐标点列表
        """
        transform = self.extractor.transform

        # 将经纬度转换为行列索引（注意 lat 值大的行号小）
        row1, col1 = rowcol(transform, lon1, lat1)
        row2, col2 = rowcol(transform, lon2, lat2)

        # 获取行列范围，确保 row_start < row_stop，col_start < col_stop
        row_start = min(row1, row2)
        row_stop = max(row1, row2)
        col_start = min(col1, col2)
        col_stop = max(col1, col2)

        rows = row_stop - row_start + 1
        cols = col_stop - col_start + 1
        print(f'{cols}个经度点，{rows}个纬度点')

        coords = []

        # 采样下边界（row_start）
        for c in range(col_start, col_stop + 1):
            x, y = xy(transform, row_start, c)
            coords.append((x, y))

        # 采样上边界（row_stop）
        for c in range(col_start, col_stop + 1):
            x, y = xy(transform, row_stop, c)
            coords.append((x, y))

        # 左边界（不含角点）
        for r in range(row_start + 1, row_stop):
            x, y = xy(transform, r, col_start)
            coords.append((x, y))

        # 右边界（不含角点）
        for r in range(row_start + 1, row_stop):
            x, y = xy(transform, r, col_stop)
            coords.append((x, y))

        return coords, (cols, rows)

    def sample_circle(self, center, radius_m):
        """
        基于行列索引和仿射变换，采样圆形边界的像元坐标，并返回对应的地理坐标。

        :param center: 圆心坐标 (lon, lat)
        :param radius_m: 半径（米）
        :return: list[(lon, lat)]
        """
        lon, lat = center
        res = self.extractor.res
        res_deg = min(res[0], res[1])

        geod = Geod(ellps="WGS84")

        # 圆周长
        circumference = 2 * math.pi * radius_m

        # 估算角度分辨率对应的距离（大概）
        approx_resolution_m = res_deg * 111000  # 1度 ≈ 111km

        # 边界点数量：确保边界点之间的间距接近 tif 分辨率
        num_points = max(16, int(circumference / approx_resolution_m))

        # 构造圆的边界点
        angles = [i * 360 / num_points for i in range(num_points)]

        lons, lats, _ = geod.fwd(
            [lon] * num_points, [lat] * num_points,  # 起点（重复）
            angles,  # 方位角（每个点）
            [radius_m] * num_points  # 每个点的距离
        )

        # min_lon, max_lon = min(lons), max(lons)
        # min_lat, max_lat = min(lats), max(lats)

        return list(zip(lons, lats))

    @staticmethod
    def _nearest_visible(H, D):
        """
        判断视距与非视距通信区
        计算发射坡度角

        输入：
            H: 高程列表 [h0, h1, ..., hk]
            D: 距离列表 [d0=0, d1, ..., dk]，单位米

        输出：
            S: 判定集合 S[i] = 1 视距, 0 非视距
        """
        k = len(H) - 1  # 点数 - 1
        S = [1]  # 第一个点是发射点，默认可视
        i = 1

        # 发射点
        h0 = H[0]
        d0 = D[0]

        # 获取发射点到第 i 点的斜率
        def get_slope(i):
            return (H[i] - h0) / (D[i] - d0)

        # 发射点到第一个点的斜率
        g_prev = get_slope(1)

        while i <= k:
            gi = get_slope(i)
            if gi >= g_prev:
                S.append(1)
                g_prev = gi
                i += 1
            else:
                S.append(0)
                i += 1

                # 拟合直线 f，从发射点到当前第 i 点
                def f(x):
                    # 线性插值：斜率 * (x 距离差) + h0
                    return g_prev * (D[x] - d0) + h0

                while i <= k and f(i) > H[i]:
                    S.append(0)
                    i += 1

        return S

    # @staticmethod
    # def _calculate_theta_t(H, D):
    #     """
    #     计算发射坡度角 theta_t（毫弧度）
    #
    #     输入：
    #         H: 高程列表 [h0, h1, ..., hk]，起点为发射点，终点为接收点
    #         D: 距离列表 [d0=0, d1, ..., dk]，单位为米，对应于 H
    #
    #     输出：
    #         theta_t：发射点相对链路其他点的最大仰角（单位：毫弧度）
    #     """
    #     h_tx = H[0]
    #     d_tx = D[0]
    #
    #     max_slope = float('-inf')
    #
    #     for i in range(1, len(H)):
    #         h_i = H[i]
    #         d_i = D[i]
    #
    #         if d_i == d_tx:
    #             continue  # 避免除以0
    #
    #         slope = (h_i - h_tx) / (d_i - d_tx)
    #         if slope > max_slope:
    #             max_slope = slope
    #
    #     # 转换为与 X 轴正方向的夹角（弧度）
    #     theta_t = math.atan(max_slope)
    #
    #     return theta_t * 1000  # 转换为毫弧度
    #
    # @staticmethod
    # def _calculate_theta_r(H, D):
    #     """
    #     计算接收坡度角
    #
    #     输入：
    #         H: 高程列表 [h0, h1, ..., hk]
    #         D: 距离列表 [d0=0, d1, ..., dk]，单位米
    #
    #     输出：
    #         接收坡度角（毫弧度）
    #     """
    #     k = len(H) - 1  # 总点数 - 1
    #     h_rx = H[-1]  # 接收点高度
    #     d_rx = D[-1]  # 接收点距离
    #
    #     min_slope = float('inf')
    #
    #     # 从前往后遍历每个中间点，计算其与接收点的斜率
    #     for i in range(k):
    #         h_i = H[i]
    #         d_i = D[i]
    #
    #         if d_rx == d_i:
    #             continue  # 避免除以0
    #
    #         slope = (h_rx - h_i) / (d_rx - d_i)
    #
    #         # 若该点与接收点连线在当前最大坡度以上，则更新
    #         if slope < min_slope:
    #             min_slope = slope
    #
    #     theta_r = -math.atan(min_slope)
    #
    #     # 返回斜率对应的仰角，单位：mrad
    #     return theta_r * 1000

    @staticmethod
    def calculate_theta_pair(H, D):
        """
        使用 NumPy 向量化同时计算发射点与接收点的仰角（单位：毫弧度）

        :param H: 高程数组，起点为发射点，终点为接收点
        :param D: 距离数组，单位：米
        :return: (theta_t, theta_r) — 单位：毫弧度
        """
        H = np.asarray(H, dtype=np.float64)
        D = np.asarray(D, dtype=np.float64)

        # ========== 发射仰角 ==========
        h_tx = H[0]
        d_tx = D[0]

        delta_h_tx = H[1:] - h_tx
        delta_d_tx = D[1:] - d_tx
        with np.errstate(divide='ignore', invalid='ignore'):
            slopes_tx = np.where(delta_d_tx != 0, delta_h_tx / delta_d_tx, -np.inf)

        theta_t = math.atan(np.max(slopes_tx)) * 1000

        # ========== 接收仰角 ==========
        h_rx = H[-1]
        d_rx = D[-1]

        delta_h_rx = h_rx - H[:-1]
        delta_d_rx = d_rx - D[:-1]
        with np.errstate(divide='ignore', invalid='ignore'):
            slopes_rx = np.where(delta_d_rx != 0, delta_h_rx / delta_d_rx, np.inf)

        theta_r = math.atan(-np.min(slopes_rx)) * 1000

        return theta_t, theta_r

    def compute_profile_loss(self, tx_lonlat, boundary_lonlat, elevation_array, base_row, base_col):
        """
        单条路径剖面提取与损耗计算：
        - 调用 extractor 提取路径剖面：返回链路点 L、海拔 H、距离 D
        - 使用自由空间模型或散射模型计算每个点损耗
        """
        # 散射通信链路剖面提取
        print(f'time1  {time()}')
        # L, H, D = self.extractor.extract_profile(*tx_lonlat, *boundary_lonlat)
        L, H, D = self.extractor.extract_profile(
            *tx_lonlat,
            *boundary_lonlat,
            elevation_array=elevation_array,
            base_row=base_row,
            base_col=base_col
        )

        # 视距
        print(f'time2  {time()}')
        S = self._nearest_visible(H, D)

        losses = []
        # print(f'time3  {time()}')
        # L(fs) = 20log₁₀(d)+20log₁₀(f)+32.45
        for i in range(len(S)):
            d_km = D[i] / 1000  # 转换为 km
            if S[i] == 1:
                if d_km == 0:
                    l_i = 0  # 起点损耗视为 0
                else:
                    # l_i = 20 * np.log10(d_km) + 20 * np.log10(self.freq) + 32.45
                    l_i = self.losCalculator.calculate(d_km)
                losses.append(l_i)
            else:
                # 非视距：
                # print(f'time4  {time()}')
                theta_t, theta_r = self.calculate_theta_pair(H[:i + 1], D[:i + 1])
                # theta_t = self._calculate_theta_t(H[:i + 1], D[:i + 1])
                # theta_r = self._calculate_theta_r(H[:i + 1], D[:i + 1])

                # print(f'time5  {time()}')
                l_i, _, _ = self.nLosCalculator.calculate(
                    tx_lonlat,
                    boundary_lonlat,
                    d_km,
                    theta_t,
                    theta_r
                )
                # print(f'time6  {time()}')
                losses.append(l_i)

        return L, losses

    def get_resolution(self):
        res_lon, res_lat = self.extractor.res
        res_lat = abs(res_lat)  # res_lat 通常是负数，取绝对值
        return (res_lon, res_lat)

    def plan_coverage(self, tx_lonlat, boundary_pts, progress_callback=None):
        """
        区域覆盖计算（适用于矩形和圆形区域）：
        - tx_lonlat：发射站经纬度
        - boundary_pts：边界点列表
        返回 coverage 字典 { boundary_point: loss_list }
        """
        jobs = [(tx_lonlat, bp) for bp in boundary_pts]

        total_jobs = len(jobs)
        completed = 0
        coverage = {}

        def worker(args):
            return self.compute_profile_loss(*args)

        with ThreadPoolExecutor() as executor:
            future_to_point = {executor.submit(worker, job): job[1] for job in jobs}

            for future in as_completed(future_to_point):
                coord = future_to_point[future]
                try:
                    L, losses = future.result()
                    for coord, loss in zip(L, losses):
                        coverage[coord] = loss
                except Exception as e:
                    print(f"[线程错误] 计算点 {coord} 出错: {e}")

                # 更新进度
                completed += 1
                if progress_callback:
                    progress_callback(0.9999 * completed / total_jobs)

        return coverage


def compute_profile_loss_standalone(tx_lon, tx_lat, rx_lon, rx_lat, freq, elevation_array, base_row, base_col):
    """
    独立的计算函数，可在多进程中执行
    必须是顶级函数且不依赖无法pickle的对象
    """
    planner = CoveragePlanner(freq)
    return planner.compute_profile_loss((tx_lon, tx_lat), (rx_lon, rx_lat), elevation_array, base_row, base_col)
