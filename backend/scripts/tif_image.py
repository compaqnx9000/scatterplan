import rasterio
from rasterio.transform import from_origin
import numpy as np
import os

os.environ["PROJ_LIB"] = r"D:\code\scattering\venv\lib\site-packages\pyproj\proj_dir\share\proj"

# 创建 500x500 的 float32 数组，模拟 DEM 或 NDVI 数据
data = np.random.rand(500, 500).astype(np.float32) * 100  # 可改为其他值范围
nodata_val = -3.4028235e+38  # float32 最小值（NoData）

# 设置地理变换（左上角坐标，经度范围从 100 开始，纬度从 30 开始）
pixel_size = 0.0008333333  # 相当于 ~90 米
transform = from_origin(
    west=100.0,      # 左上角经度
    north=30.0,      # 左上角纬度
    xsize=pixel_size,
    ysize=pixel_size
)

# 写入GeoTIFF
# with rasterio.open(
#     'output.tif',
#     "w",
#     driver="GTiff",
#     height=data.shape[0],
#     width=data.shape[1],
#     count=1,  # 单波段
#     dtype='float32',
#     crs="EPSG:4326",
#     transform=transform,
#     nodata=nodata_val,
#     tiled=True,
#     blockxsize=128,
#     blockysize=128,
#     compress="lzw",
#     interleave="band"
# ) as dst:
#     dst.write(data, 1)
#     print(dst.profile)
with rasterio.open('./ChinaDEM/ChinaDEM.tif') as dst:
    print(dst.profile)
    dst.close()
