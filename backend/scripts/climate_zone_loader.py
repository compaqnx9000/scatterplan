import os
import numpy as np


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


class ClimateZoneLoader:
    """
    加载和处理TropoClim.txt气候区数据类
    """
    _data = None

    def __init__(self, file_path=None):
        """
        初始化气候区数据

        :param file_path: TropoClim.txt文件路径
        :raises FileNotFoundError: 当文件不存在时抛出
        """
        if ClimateZoneLoader._data is None:
            if file_path is None:
                # raise ValueError("气候区文件未加载，且未提供路径。")
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录
                file_path = os.path.join(base_dir, 'scripts', 'TropoClim.txt')
            self._load_file(file_path)

        self.data = ClimateZoneLoader._data

        # 数据参数（根据ITU-R P.617-3标准定义）
        self.lat_start = 89.75  # 起始纬度（北纬，度）
        self.lon_start = -179.75  # 起始经度（西经，度）
        self.resolution = 0.5  # 数据分辨率（度）

        # 计算数据尺寸
        self.rows = self.data.shape[0]  # 行数（纬度方向）
        self.cols = self.data.shape[1]  # 列数（经度方向）

        # 计算纬度范围（从北到南）
        self.lat_end = self.lat_start - (self.rows - 1) * self.resolution

        # 计算经度范围（从西到东）
        self.lon_end = self.lon_start + (self.cols - 1) * self.resolution

    def _load_file(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"气候区文件不存在: {path}")

        # 读取气候区数据（整数数组）
        # self.data = np.loadtxt(path, dtype=np.int32)
        ClimateZoneLoader._data = np.loadtxt(path, dtype=np.int32)

        # 输出加载信息
        print(f"气候区数据加载成功: {path}")
        # print(f"范围: 纬度 {self.lat_end:.2f}N - {self.lat_start:.2f}N, 经度 {self.lon_start:.2f}E - {self.lon_end:.2f}E")
        # print(f"分辨率: {self.resolution}度")
        # print(f"大小: {self.rows}行 × {self.cols}列")

    def get_climate_zone(self, lon, lat):
        """
        获取指定经纬度位置的气候区代码

        :param lon: 经度（单位：度）
        :param lat: 纬度（单位：度）
        :return: 气候区代码（0-6，根据ITU-R P.617-3定义）
        """
        # 计算行索引（纬度从北到南递减）
        # 公式：行索引 = (起始纬度 - 目标纬度) / 分辨率
        row = int((self.lat_start - lat) / self.resolution)

        # 计算列索引（经度从西到东递增）
        # 公式：列索引 = (目标经度 - 起始经度) / 分辨率
        col = int((lon - self.lon_start) / self.resolution)

        # 检查索引是否在有效范围内
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.data[row, col]
        else:
            # 超出边界返回默认值（6：极地）
            return 6

    @staticmethod
    def is_land(climate_zone):
        """
        判断气候区是否为陆地

        :param climate_zone: 气候区代码
        :return: True（陆地）或False（海洋）
        """
        # 海洋气候区代码为0，其他为陆地
        return climate_zone != 0

    @staticmethod
    def get_climate_params(climate_zone):
        """
        获取指定气候区的参数（F和γ）

        :param climate_zone: 气候区代码（0-8）
        :return: (F, γ) 参数元组，单位分别为dB和km⁻¹
        """
        # 处理特殊映射情况
        if climate_zone == 0:  # 海洋
            return CLIMATE_PARAMS[0]
        elif climate_zone in CLIMATE_PARAMS:
            return CLIMATE_PARAMS[climate_zone]
        else:
            # 默认返回极地参数
            return CLIMATE_PARAMS[6]
