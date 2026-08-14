from django.db import models
# from django.contrib.gis.db import models as gis_models
from users.models import CustomUser


# 单链路
class SingleLink(models.Model):
    name = models.CharField(max_length=100)  # 链路名称
    tx_lon = models.FloatField()  # 发射点经度
    tx_lat = models.FloatField()  # 发射点纬度
    tx_height = models.FloatField()  # 发射点高度
    tx_terrain_height = models.FloatField()  # 发射点地形高度
    rx_lon = models.FloatField()  # 接收点经度
    rx_lat = models.FloatField()  # 接收点纬度
    rx_height = models.FloatField()  # 接收点高度
    rx_terrain_height = models.FloatField()  # 接收点地形高度
    tx_gain = models.IntegerField()  # 发射天线增益
    rx_gain = models.IntegerField()  # 接收天线增益
    freq = models.IntegerField()  # 频率
    diversity_order = models.IntegerField()  # 分集重数
    trans_power = models.IntegerField()  # 发射功率
    comm_rate = models.CharField(max_length=20)  # 通信速率
    tx_station_name = models.CharField(max_length=100)  # 发射站点名称
    rx_station_name = models.CharField(max_length=100)  # 接收站点名称

    distance_km = models.FloatField()  # 距离(km)
    median_loss = models.FloatField()  # 损耗中值
    final_loss = models.FloatField()  # 最终损耗
    tx_theta = models.FloatField()  # 发射点仰角
    rx_theta = models.FloatField()  # 接收点仰角
    theta_scatter = models.FloatField()  # 散射角
    area = models.CharField(max_length=100)  # 链路所在区域
    max_height = models.FloatField()  # 链路最高高度
    tx_barrier_distance = models.FloatField()  # 发射点障碍物距离
    tx_barrier_height = models.FloatField()  # 发射点障碍物高度差
    rx_barrier_distance = models.FloatField()  # 接收点障碍物距离
    rx_barrier_height = models.FloatField()  # 接收点障碍物高度差
    scatterer_lon = models.FloatField()  # 散射点经度
    scatterer_lat = models.FloatField()  # 散射点纬度
    scatterer_height = models.FloatField()  # 散射点高度
    tx_azimuth = models.FloatField()  # 发射点方位角
    rx_azimuth = models.FloatField()  # 接收点方位角
    residual_value = models.FloatField()  # 衰落余值
    reliability = models.FloatField()  # 可靠性
    recv_power = models.FloatField()  # 接收功率
    image_path = models.CharField(max_length=100)  # # 图像路径（png/jpg)
    calculation_duration = models.CharField(max_length=20)  # 计算时长

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # 用户外键
    # description = models.TextField(blank=True, null=True)  # 描述
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间


# 区域覆盖模型
class AreaCoverage(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)  # 区域名称
    tx_station_name = models.CharField(max_length=100)  # 发射站点名称
    tx_longitude = models.FloatField()  # 发射点经度
    tx_latitude = models.FloatField()  # 发射点纬度
    frequency = models.IntegerField()  # 频率
    tx_gain = models.IntegerField()  # 发射天线增益
    rx_gain = models.IntegerField()  # 接收天线增益
    diversity_order = models.IntegerField()  # 分集重数
    trans_power = models.IntegerField()  # 发射功率
    comm_rate = models.CharField(max_length=20)  # 通信速率
    coverage_type = models.CharField(max_length=20)  # 覆盖区域类型
    rectangle_min_longitude = models.FloatField(blank=True, null=True)  # 矩形最小经度
    rectangle_max_longitude = models.FloatField(blank=True, null=True)  # 矩形最大经度
    rectangle_min_latitude = models.FloatField(blank=True, null=True)  # 矩形最小纬度
    rectangle_max_latitude = models.FloatField(blank=True, null=True)  # 矩形最大纬度
    circle_center_longitude = models.FloatField(blank=True, null=True)  # 圆心经度
    circle_center_latitude = models.FloatField(blank=True, null=True)  # 圆心纬度
    circle_radius = models.FloatField(blank=True, null=True)  # 圆半径(m)
    image_colors = models.CharField(max_length=100)  # 图像颜色数组
    image_min = models.FloatField()  # 图像最小值
    image_max = models.FloatField()  # 图像最大值
    subrange_type = models.CharField(max_length=20, blank=True, null=True)  # 子区域类型
    subrange_rectangle_min_longitude = models.FloatField(blank=True, null=True)  # 子区域矩形最小经度
    subrange_rectangle_max_longitude = models.FloatField(blank=True, null=True)  # 子区域矩形最大经度
    subrange_rectangle_min_latitude = models.FloatField(blank=True, null=True)  # 子区域矩形最小纬度
    subrange_rectangle_max_latitude = models.FloatField(blank=True, null=True)  # 子区域矩形最大纬度
    subrange_circle_center_longitude = models.FloatField(blank=True, null=True)  # 子区域圆心经度
    subrange_circle_center_latitude = models.FloatField(blank=True, null=True)  # 子区域圆心纬度
    subrange_circle_radius = models.FloatField(blank=True, null=True)  # 子区域圆半径(m)

    prohibited_area_type = models.CharField(max_length=20, blank=True, null=True)  # 禁止区域类型
    prohibited_min_longitude = models.FloatField(blank=True, null=True)  # 禁止区域矩形最小经度
    prohibited_max_longitude = models.FloatField(blank=True, null=True)  # 禁止区域矩形最大经度
    prohibited_min_latitude = models.FloatField(blank=True, null=True)  # 禁止区域矩形最小纬度
    prohibited_max_latitude = models.FloatField(blank=True, null=True)  # 禁止区域矩形最大纬度
    prohibited_center_longitude = models.FloatField(blank=True, null=True)  # 禁止区域圆心经度
    prohibited_center_latitude = models.FloatField(blank=True, null=True)  # 禁止区域圆心纬度
    prohibited_radius = models.FloatField(blank=True, null=True)  # 禁止区域圆半径(m)

    tif_path = models.CharField(max_length=100)  # tif文件路径
    image_path = models.CharField(max_length=100)  # 图像文件路径（png/jpg)
    calculation_duration = models.CharField(max_length=20)  # 计算时长
    calculation_area = models.CharField(max_length=100)  # 区域面积（平方公里）
    cluster_duration = models.CharField(max_length=20, blank=True, null=True)  # 聚类计算时长

    # rate = models.CharField(max_length=20, blank=True, null=True)  # 平均速率
    loss_threshold = models.CharField(max_length=20, blank=True, null=True)  # 损耗阈值
    eps_cells = models.CharField(max_length=20, blank=True, null=True)  # 邻域距离阈值（单位格）
    min_samples = models.IntegerField(blank=True, null=True)  # 邻域样本个数阈值
    p = models.IntegerField(blank=True, null=True)  # 单位格时间占比（%）
    limit_road_distance = models.IntegerField(blank=True, null=True)  # 道路距离限制（单位米）
    # number = models.CharField(blank=True, null=True)  # 站点编号
    # rx_center_longitude = models.FloatField(blank=True, null=True)  # 接收点经度
    # rx_center_latitude = models.FloatField(blank=True, null=True)  # 接收点纬度
    # to_road_name = models.CharField(max_length=100, blank=True, null=True)  # 最近公路名称
    # to_road_slope = models.FloatField(blank=True, null=True)  # 到最近公路坡度
    # to_road_distance = models.FloatField(blank=True, null=True)  # 距最近公路距离

    excel_path = models.CharField(max_length=100, blank=True, null=True)  # 站点导出的excel文件路径

    relay_longitude = models.FloatField(blank=True, null=True)  # 中继点经度
    relay_latitude = models.FloatField(blank=True, null=True)  # 中继点纬度
    relay_to_road_name = models.CharField(max_length=100, blank=True, null=True)  # 中继点最近道路名称
    relay_to_road_slope = models.FloatField(blank=True, null=True)  # 中继点最近道路坡度
    relay_to_road_distance = models.FloatField(blank=True, null=True)  # 中继点最近道路距离

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # 用户外键
    # description = models.TextField(blank=True, null=True)  # 描述
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间

    def __str__(self):
        return self.name


class Stations(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)  # 站点名称
    number = models.CharField(max_length=100, blank=True, null=True)  # 站点编号
    center_longitude = models.FloatField()  # 中心点经度
    center_latitude = models.FloatField()  # 中心点纬度
    count = models.IntegerField()  # 站点内点个数
    to_road_name = models.CharField(max_length=100, )  # 最近道路名称
    to_road_slope = models.FloatField()  # 到最近道路坡度
    to_road_distance = models.FloatField()  # 距最近道路距离

    area = models.ForeignKey(AreaCoverage, on_delete=models.CASCADE)  # 区域外键
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
