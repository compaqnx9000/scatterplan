import numpy as np
import rasterio
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def convert_tif_to_image(
        input_tif_path: str,
        output_image_path: str,
        colors: list[str] = None,
        min_val: float = 100,
        max_val: float = 300
):
    """
    将tif影像转为彩色图像（如PNG/JPG），按值区间映射颜色。

    参数:
        input_tif_path (str): 输入的.tif文件路径
        output_image_path (str): 输出图像路径（.png或.jpg）
        colors (list[str]): 7种颜色代码（hex格式 '#RRGGBB'），默认从蓝到红
        min_val (float): 最小值阈值，低于该值的按此值处理
        max_val (float): 最大值阈值，高于该值的按此值处理
    """

    # 默认颜色：蓝 → 红的 7 段渐变（hex 格式）
    if colors is None:
        colors = [
            '#0000FF',  # 蓝
            '#00FFFF',  # 青
            '#00FF00',  # 绿
            '#FFFF00',  # 黄
            '#FFA500',  # 橙
            '#FF4500',  # 暗橙
            '#FF0000',  # 红
        ]

    if len(colors) != 7:
        raise ValueError("必须提供7种颜色（hex格式），用于分段渐变。")

    # 读取tif文件
    with rasterio.open(input_tif_path) as src:
        data = src.read(1).astype(np.float32)
        nodata = src.nodata

    span = float(max_val) - float(min_val)
    if span <= 0:
        span = 1.0

    # 剪裁数据到[min_val, max_val]
    data_clipped = np.clip(data, min_val, max_val)

    # 归一化到[0,1]
    norm_data = (data_clipped - min_val) / span
    norm_data = np.clip(norm_data, 0.0, 1.0).astype(np.float32)

    # 创建自定义 colormap
    cmap = LinearSegmentedColormap.from_list("custom_colormap", colors, N=256)

    # 映射为RGBA颜色
    # rgba = cmap(norm_data)
    rgba_8bit = cmap(norm_data, bytes=True)

    # 处理无数据值，将其设为透明
    if nodata is not None:
        # 将nodata值的位置的alpha通道设为0（完全透明）
        rgba_8bit[data == nodata, 3] = 0
    else:
        # 如果没有明确的nodata值，将默认的nodata_value设为透明
        rgba_8bit[data == -9999, 3] = 0

    # # 转为RGB并缩放为8位
    # rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
    # 转为RGBA并缩放为8位
    # rgba_8bit = (rgba * 255).astype(np.uint8)

    # 保存图像
    # image_dir = path.join(settings.MEDIA_ROOT)
    # makedirs(image_dir, exist_ok=True)
    # image_path = path.join(image_dir, './rectangle_area_coverage.png')
    # Image.fromarray(rgb).save(output_image_path)
    Image.fromarray(rgba_8bit).save(output_image_path)


# if __name__ == '__main__':
#     convert_tif_to_image(
#         input_tif_path='../media/areacoverage/rectangle_area_test1-200×300_20250928_153259.tif',
#         output_image_path='../media/areacoverage/rectangle_area_test1-200×300_20250928_153259.png',
#     )
