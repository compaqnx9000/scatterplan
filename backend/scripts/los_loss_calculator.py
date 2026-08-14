import math


class LosLossCalculator:
    """
    视距链路损耗计算工具类
    """

    def __init__(self, frequency_mhz):
        """
        :param frequency_mhz: 频率（单位 MHz）
        """
        self.frequency_mhz = frequency_mhz

    def calculate(self, distance_km):
        """
        计算可视域（LOS）路径损耗（Free Space Path Loss）
        FSPL(dB) = 32.45 + 20*log10(d_km) + 20*log10(f_MHz)
        
        :param distance_km: 距离（单位 km）
        :return: 损耗（dB）
        """
        fspl = 32.45 + 20 * math.log10(distance_km) + 20 * math.log10(self.frequency_mhz)
        return fspl

# if __name__ == "__main__":
#     calc = LossCalculator(frequency_mhz=2400)  # 2.4 GHz
#     dist_km = 5  # 5公里
#     print(f"LOS损耗: {calc.calculate(dist_km):.2f} dB")
