from os import path
from time import time
import math
import numpy as np
from numba import njit
from scripts.dem_profile_extractor import DemProfileExtractor
from scripts.los_loss_calculator import LosLossCalculator
from scripts.nlos_loss_calculator import NLosLossCalculator
from scripts import utils


class ClimateLossCalculator:
    def __init__(self, tx_lon, tx_lat, rx_lon, rx_lat, tx_gain, rx_gain, freq_mhz, diversity_order):
        self.tx_coord = (tx_lon, tx_lat)
        self.rx_coord = (rx_lon, rx_lat)
        self.diversity_order_loss = (diversity_order - 1) * 3
        self.losCalculator = LosLossCalculator(freq_mhz)
        self.nLosCalculator = NLosLossCalculator(tx_gain, rx_gain, freq_mhz)

        self.theta_scatter = 0
        self.area = None

    def _compute_path_loss(self, S, H, D):
        """
        计算剖面路径的通信链路损耗值 loss[i]（视距段使用自由空间传播模型）
        
        输入：
            S: 视距判定列表 [s0, s1, ..., sk]，1 为视距，0 为非视距

        输出：
            losses: 路径损耗值列表 [l0, l1, ..., lk]，单位 dB
        """

        losses = []
        # L(fs) = 20log₁₀(d)+20log₁₀(f)+32.45
        for i in range(len(S)):
            d_km = float(D[i] / 1000)  # 转换为 km
            if S[i] == 1:
                if d_km == 0:
                    l_i = 0  # 避免 log(0) 错误，起点损耗视为 0
                else:
                    # l_i = 20 * np.log10(d_km) + 20 * np.log10(self.freq) + 32.45
                    l_i = self.losCalculator.calculate(d_km) - self.diversity_order_loss
                losses.append(l_i)
            else:
                # 非视距：
                theta_t, theta_r = utils.calculate_theta_pair(H[:i + 1], D[:i + 1])

                l_i, self.area, self.theta_scatter = self.nLosCalculator.calculate(
                    self.tx_coord,
                    self.rx_coord,
                    d_km,
                    theta_t,
                    theta_r
                )
                losses.append(l_i - self.diversity_order_loss)

        return losses

    def _compute_scatterer_point(self, L, H, D, theta_t, theta_r):
        tx_point = (D[0], H[0])
        rx_point = (D[-1], H[-1])

        # 斜率
        k_t = math.tan(theta_t / 1000.0)
        k_r = math.tan(-theta_r / 1000.0)

        if k_t == k_r:
            # 平行：取两点中点作为散射点
            x = (tx_point[0] + rx_point[0]) / 2
            y = (tx_point[1] + rx_point[1]) / 2
        else:
            # 点斜式求截距
            b1 = tx_point[1] - k_t * tx_point[0]
            b2 = rx_point[1] - k_r * rx_point[0]

            # 直接代公式求交点
            x = (b2 - b1) / (k_t - k_r)
            y = k_t * x + b1

        scatterer_point = (x, y)

        scatterer_lonlat = L[-1]  # 默认返回终点

        # 在距离序列中找到中点所在区间
        for i in range(len(D) - 1):
            if D[i] <= x <= D[i + 1]:
                ratio = (x - D[i]) / (D[i + 1] - D[i])
                lon1, lat1 = L[i]
                lon2, lat2 = L[i + 1]
                scatter_lon = lon1 + ratio * (lon2 - lon1)
                scatter_lat = lat1 + ratio * (lat2 - lat1)
                scatterer_lonlat = (scatter_lon, scatter_lat)

        # print(scatterer_point, scatterer_lonlat)
        return scatterer_point, scatterer_lonlat

    @staticmethod
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

    def calculate_loss(self):
        # ==================================================================
        # 算法1-1:      散射通信链路剖面提取算法
        # 输入:         高程数据集 DEM(x,y)
        #               发射站点坐标(x0,y0)
        #               接收站点坐标(xk,yk)
        # 输出:         剖面坐标点数据集L [(x0, y0),…, (xi,yi),…, (xk, yk)]
        #               剖面高程数据集H[h0,…, hk]
        #               剖面距离数据集D[d0,…, dk]
        # ==================================================================
        extractor = DemProfileExtractor()
        L, self.H, self.D = extractor.extract_profile(*self.rx_coord, *self.tx_coord)
        print("剖面点数:", len(L))
        print(f'第一个点:{float(L[0][0])},{float(L[0][1])}, 高程:{self.H[0]}, 距离:{self.D[0]}')
        print(f'最后一个点:{float(L[-1][0])},{float(L[-1][1])}, 高程:{self.H[-1]}, 距离:{self.D[-1]}')
        np_h_arr = np.array(self.H, dtype=np.float64)
        np_d_arr = np.array(self.D, dtype=np.float64)

        # ==================================================================
        # 算法1-2:      散射通信链路视距通信判定算法
        # 输入:         剖面高程数据集H[h0,…, hk]
        #               剖面距离数据集D[d0,…, dk]
        # 输出:         剖面视距通信判定集 S[s1,…, sk]
        # ==================================================================
        S = utils.nearest_visible(np_h_arr, np_d_arr)
        print("点数:", len(S))
        # print("S:", S)

        # ==================================================================
        # 计算发射和接收仰角
        # ==================================================================
        self.theta_t, self.theta_r = utils.calculate_theta_pair(np_h_arr, np_d_arr)
        print(f'发射仰角：{self.theta_t}，接收仰角：{self.theta_r}')

        self.theta_scatter = self.nLosCalculator._calculate_scatter_angle(self.D[-1] / 1000, self.theta_t, self.theta_r)

        if not self.area:
            zone = self.nLosCalculator._climate_zone_loader.get_climate_zone(*self.tx_coord)
            _, _, _, self.area = self.nLosCalculator._climate_zone_loader.get_climate_params(zone)

        # ==================================================================
        # 算法1-3:      散射通信链路传输损耗值算法
        # 输入:         剖面视距通信判定集 S[s1,…, sk]
        #               剖面高程数据集H[h0,…, hk]
        #               剖面距离数据集D[d0,…, dk]
        # 输出:         散射通信链路传输损耗值集loss[l1,…,lk]
        # ==================================================================
        loss = self._compute_path_loss(S, np_h_arr, np_d_arr)
        # print("loss:", loss)

        # ==================================================================
        # 计算散射体
        # ==================================================================
        scatterer_point, scatterer_lonlat = self._compute_scatterer_point(L, self.H, self.D, self.theta_t, self.theta_r)
        print(f'散射体坐标{scatterer_point}')

        # 计算障碍点
        tx_barrier, rx_barrier = utils.calculate_barriers(np_h_arr, np_d_arr)

        return loss, scatterer_point, tx_barrier, rx_barrier, scatterer_lonlat
