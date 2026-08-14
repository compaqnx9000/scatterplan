import numpy as np
import rasterio
from rasterio.transform import from_origin


class CoverageTiffExporter:
    def __init__(self, resolution=0.00025, nodata_value=-9999):
        """
        初始化导出器
        :param resolution: 每像素大小（经纬度单位），默认约 30 米（0.00025°）
        :param nodata_value: 无效像素填充值
        """
        self.res_lon, self.res_lat = resolution
        self.nodata_value = nodata_value

    def _prepare_raster_data(self, coverage: dict):
        """
        准备栅格数据的通用处理部分

        :param coverage: dict[(lon, lat)] = value
        :return: coords, values, lons, lats, min_lon, max_lon, min_lat, max_lat, width, height
        """
        if not coverage:
            raise ValueError("coverage 数据为空")

        coords = np.array(list(coverage.keys()))
        values = np.array(list(coverage.values()))

        # 四舍五入到分辨率对齐
        lons = np.round(coords[:, 0] / self.res_lon) * self.res_lon
        lats = np.round(coords[:, 1] / self.res_lat) * self.res_lat

        min_lon, max_lon = lons.min(), lons.max()
        min_lat, max_lat = lats.min(), lats.max()

        width = int(np.ceil((max_lon - min_lon) / self.res_lon)) + 1
        height = int(np.ceil((max_lat - min_lat) / self.res_lat)) + 1

        return coords, values, lons, lats, min_lon, max_lon, min_lat, max_lat, width, height

    def _write_raster_to_file(self, raster, image_path, min_lon, max_lat):
        """
        将栅格数据写入文件

        :param raster: 栅格数据数组
        :param image_path: 输出文件路径
        :param min_lon: 最小经度
        :param max_lat: 最大纬度
        """
        transform = from_origin(min_lon, max_lat, self.res_lon, self.res_lat)

        with rasterio.open(
            image_path,
            'w',
            driver='GTiff',
            height=raster.shape[0],
            width=raster.shape[1],
            count=1,
            dtype=raster.dtype,
            crs='EPSG:4326',
            transform=transform,
            nodata=self.nodata_value
        ) as dst:
            dst.write(raster, 1)

    def export_rectangle_tif(self, coverage: dict, ranks: tuple, image_path: str):
        """
        将 coverage 数据中在指定矩形区域内的点导出为 GeoTIFF 文件

        :param coverage: dict[(lon, lat)] = value
        :param ranks: (width, height)
        :param image_path: 输出文件路径
        """
        coords, values, lons, lats, min_lon, max_lon, min_lat, max_lat, width, height = self._prepare_raster_data(coverage)
        
        # 使用传入的ranks参数覆盖自动计算的width和height
        width, height = ranks

        raster = np.full((height, width), self.nodata_value, dtype=np.float32)

        for (lon, lat), val in coverage.items():
            col = int((lon - min_lon) / self.res_lon)
            row = int((max_lat - lat) / self.res_lat)  # 注意纬度从上到下
            if 0 <= row < height and 0 <= col < width and val > 0:
                raster[row, col] = val

        self._write_raster_to_file(raster, image_path, min_lon, max_lat)

    def export_circle_tif(self, coverage: dict, image_path: str):
        """
        将 coverage 数据中在指定圆形区域（以米为单位）内的部分导出为 GeoTIFF 文件

        :param coverage: dict[(lon, lat)] = value
        :param image_path: 输出文件路径
        """
        coords, values, lons, lats, min_lon, max_lon, min_lat, max_lat, width, height = self._prepare_raster_data(coverage)
        
        print(f'圆形区域内最大值: {np.max(values)}，中值: {np.median(values)}')

        raster = np.full((height, width), self.nodata_value, dtype=np.float32)

        for (lon, lat), val in coverage.items():
            col = int((lon - min_lon) / self.res_lon)
            row = int((max_lat - lat) / self.res_lat)  # 注意纬度从上到下
            if 0 <= col < width and 0 <= row < height and val > 0:
                raster[row, col] = val

        self._write_raster_to_file(raster, image_path, min_lon, max_lat)
