import os
import subprocess
import sqlite3
from django.conf import settings

def fast_import_shp_to_spatialite(shp_filepath, table_name="road_network", target_epsg="4326"):
    """
    使用 ogr2ogr 将 Shapefile 高速导入 SpatiaLite 数据库 (支持 Windows 便携环境)
    """
    # 动态获取你的项目数据库路径
    db_path = settings.DATABASES['default']['NAME']
    
    # 指向我们刚建立的便携 bin 目录下的 ogr2ogr.exe
    ogr2ogr_cmd = os.path.join(settings.BASE_DIR, 'bin', 'ogr2ogr.exe')
    
    # 显式覆盖环境变量，防止 ogr2ogr 调用 Python venv 里的 osgeo 的 proj.db (会引起版本冲突)
    env = os.environ.copy()
    bin_dir = os.path.join(settings.BASE_DIR, 'bin')
    env["PROJ_LIB"] = bin_dir
    env["PROJ_DATA"] = bin_dir
    # 检查表是否存在，以此决定是否使用 -append
    table_exists = False
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if cursor.fetchone():
            table_exists = True
        conn.close()

    # 构建命令
    cmd = [
        ogr2ogr_cmd,
        "-f", "SQLite",           # 输出格式
        "-dsco", "SPATIALITE=YES",# 如果是新建DB，则创建SpatiaLite结构
        "-lco", "SPATIALITE=YES", # 强制按SpatiaLite规则建表
        "-update",                # 如果数据库存在则更新
    ]
    
    if table_exists:
        cmd.append("-append")     # 若表存在则追加数据
        
    cmd.extend([
        "-nln", table_name,       # 指定导入后的表名
        "-lco", "ENCODING=UTF-8", # 字段属性中文字符编码
        "-s_srs", f"EPSG:{target_epsg}", # 假设源投影（可应对没有prj的shp文件）
        "-t_srs", f"EPSG:{target_epsg}", # 统一投影
        db_path,
        shp_filepath
    ])

    try:
        print(f"开始导入 {shp_filepath} 到表 {table_name} ...")
        # 捕获输出，这里会阻塞直到 ogr2ogr 跑完。
        # 针对 5GB 的数据，这步在实际业务中应当放在 Process/Celery 异步队列中
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env, encoding='utf-8', errors='replace')
        print("导入成功！")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print("导入失败！错误信息：\n", e.stderr)
        return False, e.stderr
