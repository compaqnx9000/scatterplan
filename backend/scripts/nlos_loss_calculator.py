import math
# import numpy as np
from scipy import special
from scripts.climate_zone_loader import ClimateZoneLoader
from scripts.utils import calculate_reliability


class NLosLossCalculator:
    """
    非视距链路损耗计算工具类
    """

    # _instance = None
    # _climate_zone_loader = None
    #
    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #         cls._instance._init_once(*args, **kwargs)
    #     return cls._instance
    #
    # def _init_once(self, filepath):
    #     self._climate_zone_loader = ClimateZoneLoader(filepath)
    def __init__(self, Gt, Gr, freq_mhz):
        self._climate_zone_loader = ClimateZoneLoader()
        self.Gt = Gt
        self.Gr = Gr
        self.freq_mhz = freq_mhz

    def calculate(self, coord_t, coord_r, distance_km, theta_t, theta_r):
        """
        计算非可视域（NLOS）路径损耗
        简单模型：NLOS 损耗 = LOS 损耗 + 额外损耗
        
        :param distance_km: 距离（单位 km）
        :param freq_mhz: 非可视域额外衰减
        :return: 损耗（dB）
        """

        # 1 ~ 7个步骤

        # ==========================================================================
        # 步骤1: 所示的气候分布图（TropoClim.txt），确定链路共同作用区域所处的气候类型
        # ==========================================================================
        # lon1, lat1 = 125.941033, 41.216892
        # lon2, lat2 = 125.1869558, 40.09225039
        zone_t = self._climate_zone_loader.get_climate_zone(*coord_t)
        zone_r = self._climate_zone_loader.get_climate_zone(*coord_r)
        # print(f"地点（纬度 {coord_t[1]}°，经度 {coord_t[0]}°）的气候区编号为：{zone_t}")
        # print(f"地点（纬度 {coord_r[1]}°，经度 {coord_r[0]}°）的气候区编号为：{zone_r}")

        # ==========================================================================
        # 步骤2: 根据所处气候类型，从表 2中获取用于该气候的气象参数M和大气结构参数 γ（伽马）
        # ==========================================================================
        if zone_t == 0:
            climate_zone = zone_r
        elif zone_r == 0:
            climate_zone = zone_t
        else:
            climate_zone = min(zone_t, zone_r)
        M, gamma, Y90_equation, area = self._climate_zone_loader.get_climate_params(climate_zone)

        # ==========================================================================
        # 步骤3: 计算散射角（即角距离）
        # ==========================================================================
        # d  # 路径长度，单位 km
        # theta_t  # 发射端地平线角度（单位 mrad）
        # theta_r  # 接收端地平线角度（单位 mrad）
        theta_scattering = self._calculate_scatter_angle(distance_km, theta_t, theta_r)
        # print(f"散射角 theta_scattering = {theta_scattering:.3f} mrad")

        # ==========================================================================
        # 步骤4: 估算传播损耗对共同作用区域高度的依赖关系LN
        #           theta_scattering  # 散射角（毫弧度）
        #           d  # 路径长度（km）
        #           gamma  # 大气结构参数 γ（来自 Step 2）
        # ==========================================================================
        Ln, h = self._estimate_Ln(theta_scattering, distance_km, gamma)
        # print(f"高度相关的传输损耗 LN = {Ln:.2f} dB")

        # ==========================================================================
        # 步骤5: 对于非 50% 的时间不超概率（q），根据以下公式估算换算因子 Y(q)
        #            Y(q) = C(q) Y(90) dB
        # ==========================================================================
        q = 50  # 时间百分比（%）暂定为50
        # q = calculate_reliability(distance_km, area, 1.0)
        Yq = self._estimate_Yq(Y90_equation, distance_km, q, h)

        # ==========================================================================
        # 步骤6: 根据以下公式估算天线口径与传播介质之间的耦合损耗Lc
        #           Lc = 0.07 exp [0.055(Gt + Gr)] dB
        #           其中Gt和Gr是天线增益
        # ==========================================================================
        Lc = self._estimate_Lc()
        # print(f"天线口径耦合损耗 Lc = {Lc:.2f} dB")

        # ==========================================================================
        # 步骤7: 根据下式估算在q%时间百分比内不超过的年平均传输损耗
        #           L(q) = M + 30 log f + 10 log d + 30 log theta_scattering + LN + Lc – Gt – Gr – Y(q) dB
        # ==========================================================================
        Lq = self._estimate_transmission_loss(M, distance_km, theta_scattering, Ln, Lc, Yq)
        # print(f"传输损耗 L(q) = {Lq:.2f} dB")

        return Lq, area, theta_scattering

    # @staticmethod
    # def _load_climate_grid(filepath):
    #     """
    #     读取 TropoClim.txt 文件内容并解析为二维 numpy 数组（气候区网格）
    #     参数:
    #         filepath: TropoClim.txt 文件的完整路径
    #     返回:
    #         numpy.ndarray 类型的二维数组，表示气候区编号网格
    #     """
    #     with open(filepath, "r") as f:
    #         data_lines = f.readlines()
    #
    #     data = []
    #     for line in data_lines:
    #         # 将每一行按空格拆分为整数
    #         values = list(map(int, line.strip().split()))
    #         data.append(values)
    #
    #     return np.array(data)

    # def _get_climate_zone_from_file(self, lat, lon, filepath):
    #     """
    #     输入经纬度，从 TropoClim.txt 文件中查找对应的气候区编号
    #     参数:
    #         lat: 纬度（°），范围约在 -90 到 90 之间，北纬为正，南纬为负
    #         lon: 经度（°），范围约在 -180 到 180 之间，东经为正，西经为负
    #         filepath: TropoClim.txt 文件路径，默认是当前目录
    #     返回:
    #         整数型气候区编号（例如：1 到 6 之间的值）
    #     """
    #
    #     # TropoClim.txt 网格参数（来自ITU说明）
    #     lat_start = 89.75  # 起始纬度（最北点）
    #     lat_step = 0.5  # 纬度间距（每行之间）
    #     lat_count = 360  # 总行数（纬度方向）
    #
    #     lon_start = -179.75  # 起始经度（最西点）
    #     lon_step = 0.5  # 经度间距（每列之间）
    #     lon_count = 720  # 总列数（经度方向）
    #
    #     # 加载气候区网格数据为二维数组
    #     climate_grid = self._load_climate_grid(filepath)
    #
    #     # 根据纬度计算所在行索引（从北往南）
    #     lat_idx = int(round((lat_start - lat) / lat_step))
    #     lat_idx = max(0, min(lat_idx, lat_count - 1))  # 防止索引越界
    #
    #     # 根据经度计算所在列索引（从西往东）
    #     lon_idx = int(round((lon - lon_start) / lon_step))
    #     lon_idx = max(0, min(lon_idx, lon_count - 1))  # 防止索引越界
    #
    #     # 返回对应的气候区编号
    #     return climate_grid[lat_idx][lon_idx]

    @staticmethod
    def _calculate_scatter_angle(d_km, theta_t_mrad, theta_r_mrad, k=4 / 3, a_km=6370):
        """
        计算 troposcatter 散射角 theta（单位：毫弧度，mrad）

        参数说明：
        - d_km: 发射点和接收点之间的大圆距离（单位：公里）
        - theta_t_mrad: 发射端天线的地平线角度（单位：毫弧度）
        - theta_r_mrad: 接收端天线的地平线角度（单位：毫弧度）
        - k: 地球有效折射率因子，默认为 4/3
        - a_km: 地球半径，单位：公里，默认为 6370 km

        返回：
        - theta_total_mrad: 计算得到的总散射角 theta，单位：毫弧度（mrad）
        """

        # 计算地球曲率项 thetae，单位为 mrad（毫弧度）
        theta_e_mrad = (d_km * 1000) / (k * a_km)

        # 总散射角 theta = thetae + thetat + thetar（单位：mrad）
        theta_total_mrad = theta_e_mrad + theta_t_mrad + theta_r_mrad

        return theta_total_mrad

    @staticmethod
    def _estimate_Ln(theta_mrad, d_km, gamma, k=4 / 3, a_km=6370):
        """
        估算由散射体高度引起的传输损耗 LN（单位：dB）

        参数说明：
        - theta_mrad: 总散射角 theta，单位为 mrad（毫弧度）
        - d_km: 发射点到接收点的路径距离，单位 km
        - gamma: 大气结构参数 γ（单位 km⁻¹）
        - k: 地球有效折射率因子，默认为 4/3
        - a_km: 地球半径，单位 km，默认为 6370 km

        返回：
        - LN: 高度相关的传输损耗值，单位 dB
        - h: 单位 km
        """

        # 步骤 1：计算 H（单位：km）
        H = (1e-3 * theta_mrad * d_km) / 4

        # 步骤 2：计算 h（单位：km）
        h = (1e-6 * (theta_mrad ** 2) * k * a_km) / 8

        # 步骤 3：计算 LN（单位：dB）
        LN = 20 * math.log10(5 + gamma * H) + 4.34 * gamma * h

        return LN, h

    def _estimate_Yq(self, Y90_equation, distance_km, q, h):
        """
        估算转换因子 Y(q)

        Y(q) = C(q) Y(90) dB

        参数说明：
        - Y90_equation: Y90参数，由表格2得出
        - freq_mhz: 频率
        - distance_km: 发射点和接收点之间的距离（单位：公里）
        - q: 时间百分比（%）
        - h: 单位 km

        返回值：
        - Yq: 估算转换因子（单位：dB）
        """
        # 根据气候区选择Y(90)计算公式（ITU-R P.617-3公式7-11）
        if Y90_equation == 7:
            # 公式7: Y90 = -2.2 - [8.1 - 2.3e-4·min(f,4000)]·exp(-0.137h)
            Y90 = -2.2 - (8.1 - 2.3e-4 * min(self.freq_mhz, 4000)) * math.exp(-0.137 * h)
        elif Y90_equation == 8:
            # 公式8: Y90 = -9.5 - 3·exp(-0.137h)
            Y90 = -9.5 - 3 * math.exp(-0.137 * h)
        elif Y90_equation == 9:
            # 公式9: 分段函数
            if distance_km < 100:
                Y90 = -8.2
            elif 100 <= distance_km < 1000:
                # 公式9b: Y90 = 1.006e-8·d_s^3 - 2.569e-5·d_s^2 + 0.02242·d_s - 10.2
                Y90 = 1.006e-8 * distance_km ** 3 - 2.569e-5 * distance_km ** 2 + 0.02242 * distance_km - 10.2
            else:
                Y90 = -3.4
        elif Y90_equation == 10:
            # 公式10: 分段函数
            if distance_km < 100:
                Y90 = -10.845
            elif 100 <= distance_km < 465:
                # 公式10b: Y90 = -4.5e-7·d_s^3 + 4.45e-4·d_s^2 - 0.122·d_s - 2.645
                Y90 = -4.5e-7 * distance_km ** 3 + 4.45e-4 * distance_km ** 2 - 0.122 * distance_km - 2.645
            else:
                Y90 = -8.4
        elif Y90_equation == 11:
            # 公式11: 分段函数
            if distance_km < 100:
                Y90 = -11.5
            elif 100 <= distance_km < 465:
                # 公式11b: Y90 = -8.519e-8·d_s^3 + 7.444e-5·d_s^2 + 4.18e-4·d_s - 12.1
                Y90 = -8.519e-8 * distance_km ** 3 + 7.444e-5 * distance_km ** 2 + 4.18e-4 * distance_km - 12.1
            else:
                Y90 = -4.0

        # 时间百分比系数C(q)（表3）
        # if q == 50:
        #     Cq = 0
        # elif q == 90:
        #     Cq = 1
        # elif q == 99:
        #     Cq = 1.82
        # elif q == 99.9:
        #     Cq = 2.41
        # else:  # 99.99
        #     Cq = 2.90
        if 50 <= q < 90:
            Cq = 0
        elif 90 <= q < 99:
            Cq = 1
        elif 99 <= q < 99.9:
            Cq = 1.82
        elif 99.9 <= q < 99.99:
            Cq = 2.41
        else:  # q >= 99.99
            Cq = 2.90

        # 公式6: Y(q) = C(q)·Y(90)
        Yq = Cq * Y90  # 单位：dB

        return Yq

    def _estimate_Lc(self):
        """
        计算天线口径耦合损耗 Lc（单位：dB）

        Gt — 发射天线增益（单位 dB）
        Gr — 接收天线增益（单位 dB）

        使用公式 (13):
        Lc = 0.07 * exp[ 0.055 * (Gt + Gr) ]
        """
        exponent = 0.055 * (self.Gt + self.Gr)  # 计算指数部分
        Lc = 0.07 * math.exp(exponent)  # 套用公式计算 Lc
        return Lc  # 返回 dB 值

    def _estimate_transmission_loss(
            self,
            M,  # 气象参数（单位：dB）
            d_km,  # 路径长度 d（单位 km）
            theta_mrad,  # 散射角 theta（单位 mrad）
            Ln,  # 高度相关传输损耗 Ln（单位 dB）
            Lc,  # 天线耦合损耗 Lc（单位 dB）
            Y_q_dB  # 损耗转换因子 Y(q)（单位 dB）
    ):
        """
        根据公式 (14) 计算某时间百分比 q 下不被超过的平均年传输损耗 L(q)

        L(q) = M + 30 * log10(f) + 10 * log10(d) + 30 * log10(theta)
            + Ln + Lc - Gt - Gr - Y(q)

        返回值：
        - Lq: 传输损耗（单位：dB）
        """
        term1 = M
        term2 = 30 * math.log10(self.freq_mhz)
        term3 = 10 * math.log10(d_km)
        term4 = 30 * math.log10(theta_mrad)

        Lq = term1 + term2 + term3 + term4 + Ln + Lc - self.Gt - self.Gr - Y_q_dB

        return Lq


# if __name__ == "__main__":
# calc = NLossCalculator(frequency_mhz=2400)  # 2.4 GHz
# dist_km = 5  # 5公里
# print(f"NLOS损耗: {calc.calculate_nlos_loss(dist_km, nlos_penalty_db=25):.2f} dB")
