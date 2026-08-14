# from os import path
from django.apps import AppConfig


class WslinkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wslink'

    # def ready(self):
    #     from scripts.dem_profile_extractor import DemProfileExtractor  # 注意不要放在顶层，防止 import 循环
    #     from scripts.climate_zone_loader import ClimateZoneLoader
    #
    #     # 构造绝对路径（项目根目录/scripts/your_dem.tif）
    #     base_dir = path.dirname(path.dirname(path.abspath(__file__)))  # 项目根目录
    #     tif_path = path.join(base_dir, 'scripts', 'ChinaDEM/China_DEM30.tif')
    #     clim_path = path.join(base_dir, 'scripts', 'TropoClim.txt')
    #
    #     # 只加载一次（类属性缓存）
    #     DemProfileExtractor(tif_path)
    #     ClimateZoneLoader(clim_path)
