import math
import time
import os
from datetime import datetime
import json
import traceback

import numpy as np
from django.db import connection, transaction
from django.conf import settings
from rest_framework.exceptions import ValidationError
from celery import shared_task, current_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django_redis import get_redis_connection

from scripts.elevation_plotter import ElevationPlotter
from scripts.climate_loss_calculator2 import ClimateLossCalculator2
from scripts.coverage_planner2 import CoveragePlanner2
from scripts.tif2png import convert_tif_to_image
from scripts.clustering_analysis import ClusteringAnalysis
from scripts import utils
from projects.serializers import SingleLinkSerializer, AreaCoverageSerializer, StationsSerializer
from projects.models import SingleLink, AreaCoverage, Stations
from projects.services import (
    resolve_project,
    ProjectResolveError,
    safe_filename,
    upsert_area_coverage,
    upsert_single_link,
)


def get_media_url(relative_path):
    """生成完整的媒体文件URL（通过Nginx访问）"""
    # 移除路径开头的斜杠
    relative_path = relative_path.lstrip('/')
    # 移除开头的media/，因为NGINX_MEDIA_URL已经包含了
    if relative_path.startswith('media/'):
        relative_path = relative_path[6:]  # 移除 'media/'
    # 拼接完整URL，确保nginx_media_url以/结尾，relative_path不以/开头
    nginx_media_url = settings.NGINX_MEDIA_URL.rstrip('/')
    return f"{nginx_media_url}/{relative_path}"


class TaskCancelledException(Exception):
    """用于控制任务中止流程的自定义异常"""
    pass


def _redis():
    return get_redis_connection("business")


def _as_str(val):
    if val is None:
        return None
    if isinstance(val, bytes):
        return val.decode()
    return str(val)


def mark_task_exited(task_id):
    if not task_id:
        return
    redis_conn = _redis()
    key = f"task:{task_id}"
    raw = redis_conn.get(key)
    payload = {"task_id": str(task_id), "status": "exited", "start_time": time.time()}
    if raw:
        try:
            payload = json.loads(raw)
            payload["status"] = "exited"
        except (TypeError, json.JSONDecodeError):
            pass
    redis_conn.setex(key, 3600, json.dumps(payload))


def stop_user_tasks(user_id):
    """把该用户名下所有覆盖/链路任务标为已退出，并清空当前活动任务。"""
    redis_conn = _redis()
    ids = set()
    members = redis_conn.smembers(f"user:{user_id}:task_ids") or []
    for member in members:
        ids.add(_as_str(member))
    active = _as_str(redis_conn.get(f"user:{user_id}:active_task"))
    if active:
        ids.add(active)
    for tid in ids:
        mark_task_exited(tid)
    redis_conn.delete(f"user:{user_id}:active_task")
    redis_conn.delete(f"user:{user_id}:task_ids")
    pending = [tid for tid in ids if tid]
    if pending:
        try:
            from celery import current_app
            # threads 池无法 terminate 正在跑的线程，只撤销尚未开始的排队任务
            current_app.control.revoke(pending, terminate=False)
        except Exception as exc:
            print(f"[stop_user_tasks] revoke 失败: {exc}")
    return pending


def register_running_task(user_id, task_id, extra=None, stop_previous=True):
    if stop_previous:
        stop_user_tasks(user_id)
    redis_conn = _redis()
    payload = {
        "task_id": str(task_id),
        "user_id": user_id,
        "status": "running",
        "start_time": time.time(),
    }
    if extra:
        payload.update(extra)
    redis_conn.setex(f"task:{task_id}", 3600, json.dumps(payload))
    redis_conn.setex(f"user:{user_id}:active_task", 3600, str(task_id))
    redis_conn.sadd(f"user:{user_id}:task_ids", str(task_id))
    redis_conn.expire(f"user:{user_id}:task_ids", 3600)


def send_ws_message(channel_name, task_id, msg_type, content):
    """统一发送WebSocket消息"""
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.send)(
        channel_name,
        {
            "task_id": task_id,
            "type": "send_task_message",
            "message": {
                "type": msg_type,
                "task_id": task_id,
                **content
            },
        },
    )


def check_cancellation(redis_task_key):
    """检查任务是否被取消，如果取消则抛出异常中断流程"""
    redis_conn = _redis()
    task_data_raw = redis_conn.get(redis_task_key)
    if not task_data_raw:
        raise TaskCancelledException("任务异常")

    task_data = json.loads(task_data_raw)
    if task_data.get("status") != "running":
        raise TaskCancelledException("任务已被用户中止")

    user_id = task_data.get("user_id")
    task_id = task_data.get("task_id")
    if user_id is None:
        return
    active = _as_str(redis_conn.get(f"user:{user_id}:active_task"))
    if not active or active != str(task_id):
        raise TaskCancelledException("任务已被用户中止")


def report_progress(channel_name, task_id, type_str: str, progress: float):
    """
        CoveragePlanner的回调函数
        报告进度的辅助方法
        将进度作为 JSON 发送到前端
    """
    redis_task_key = f"task:{task_id}"
    check_cancellation(redis_task_key)

    send_ws_message(channel_name, task_id, type_str, {'progress': round(progress * 100, 2)})


@shared_task(name='tasks.calculation_singlelink')
def calculation_singlelink(user_id: int, channel_name: str, data: dict):
    task_id = current_task.request.id

    try:
        start_time = time.time()
        redis_conn = get_redis_connection("business")
        redis_task_key = f"task:{task_id}"
        if not redis_conn.get(redis_task_key):
            redis_conn.setex(redis_task_key, 3600, json.dumps({
                "task_id": task_id,
                "task_type": "singlelink",
                "user_id": user_id,
                "status": "running",
                "start_time": time.time()
            }))
        report_progress(channel_name, task_id, 'singlelink progress', 0.03)

        # 参数提取
        tx_lon = float(data['tx_lon'])
        tx_lat = float(data['tx_lat'])
        rx_lon = float(data['rx_lon'])
        rx_lat = float(data['rx_lat'])
        tx_gain = int(data['tx_gain'])  # 发射增益(dB)
        rx_gain = int(data['rx_gain'])  # 接收增益(dB)
        freq = int(data['freq'])  # 频率(MHz)
        diversity_order = int(data['diversity_order'])  # 分集重数
        trans_power = int(data['trans_power'])  # 发射功率(W)
        comm_rate = data['comm_rate']  # 通信速率
        if data.get('climate_num'):  # 气候区编号
            climate_num = int(data.get('climate_num'))
        else:
            climate_num = None

        calculator = ClimateLossCalculator2(climate_num)

        def extract_progress(value):
            report_progress(channel_name, task_id, 'singlelink progress', 0.05 + 0.7 * float(value))

        # 起点→终点方位角(°)、终点→起点方位角(°)、高程数组[m]、距离数组[m]
        tx_azimuth, rx_azimuth, elevs, distances = calculator.extract_profile(
            tx_lon, tx_lat, rx_lon, rx_lat, progress_callback=extract_progress
        )
        report_progress(channel_name, task_id, 'singlelink progress', 0.78)
        total_dist = distances[-1]
        total_dist_km = total_dist / 1000

        # 损耗、气候区名称、发射仰角、接收仰角、散射角--单位(mrad)
        median_loss, climate_area, theta_t_mrad, theta_r_mrad, theta_scatter_mrad = calculator.calculate_path_loss(
            freq,
            tx_gain,
            rx_gain,
            elevs,
            distances,
            diversity_order
        )
        final_loss = median_loss
        print(f'损耗值 {final_loss:.3f}')
        report_progress(channel_name, task_id, 'singlelink progress', 0.86)
        # print(f'222-{time.time() - start_time:.3f}秒')

        theta_t = theta_t_mrad * (180 / (np.pi * 1000))  # 发射仰角(°)
        theta_r = theta_r_mrad * (180 / (np.pi * 1000))  # 接收仰角(°)
        theta_scatter = theta_scatter_mrad * (180 / (np.pi * 1000))  # 散射角(°)

        # 发射障碍点坐标、接收障碍点坐标、散射点坐标、散射点经纬度
        tx_barrier, rx_barrier, scatterer_point, scatterer_lonlat = calculator.compute_barriers_and_scatterer(
            elevs,
            distances,
            theta_t_mrad,
            theta_r_mrad
        )
        # print(f'发射障碍点: {tx_barrier}  接收障碍点: {rx_barrier} 距离: {distance_m}')

        tx_height, rx_height, max_height = elevs[0], elevs[-1], np.max(elevs)
        min_height = int(np.min(elevs))

        sample_count = min(280, len(distances))
        sample_idx = np.unique(np.round(np.linspace(0, len(distances) - 1, sample_count)).astype(int))
        profile_samples = [
            [round(float(distances[i] / 1000), 3), int(elevs[i])]
            for i in sample_idx
        ]

        recv_sensitivity = utils.find_recv_sensitivity(comm_rate)  # 接收灵敏度(dBm)
        trans_power_dBm = 10 * np.log10(trans_power * 1000)  # 发射功率（dBm）
        # 接收功率(dBm) = 发射功率(dBm) - 损耗(dB) + 发射增益(dB) + 接收增益(dB)
        # recv_power = np.power(10, recv_power_dBm / 10)  # 接收功率（mW）
        recv_power = trans_power_dBm - final_loss + tx_gain + rx_gain
        # 信号衰落余值(dBm) = 接收功率(dBm) - 接收灵敏度(dBm) - 5
        residual_value = recv_power - recv_sensitivity - 5

        # 传播可靠度
        reliability = utils.calculate_reliability(total_dist_km, climate_area, residual_value)
        print(f'接收功率: {recv_power:.3f} dBm 信号衰落余值: {residual_value:.3f} dB, 传播可靠度: {reliability}%')

        elapsed = time.time() - start_time
        calculation_duration = f'{int(elapsed // 60)}分{elapsed % 60:.2f}秒'
        print(f"单链路计算结束，距离： {total_dist_km:.3f} km，用时： {calculation_duration}")

        save_data = {
            'name': data['name'],
            'tx_station_name': data['tx_station_name'],
            'rx_station_name': data['rx_station_name'],
            'tx_lon': tx_lon,
            'tx_lat': tx_lat,
            'tx_height': tx_height,
            'tx_terrain_height': data['tx_height'],
            'rx_lon': rx_lon,
            'rx_lat': rx_lat,
            'rx_height': rx_height,
            'rx_terrain_height': data['rx_height'],
            'tx_gain': tx_gain,
            'rx_gain': rx_gain,
            'freq': freq,
            'diversity_order': diversity_order,
            'trans_power': trans_power,
            'distance_km': total_dist_km,
            'median_loss': final_loss,
            'final_loss': final_loss,
            'tx_theta': theta_t,
            'rx_theta': theta_r,
            'theta_scatter': theta_scatter,
            'area': climate_area,
            'max_height': max_height,
            'tx_barrier_distance': tx_barrier[0] / 1000,
            'tx_barrier_height': float(abs(tx_barrier[1] - tx_height)),
            'rx_barrier_distance': (total_dist_km - rx_barrier[0]) / 1000,
            'rx_barrier_height': float(abs(rx_barrier[1] - rx_height)),
            'scatterer_lon': float(scatterer_lonlat[0]),
            'scatterer_lat': float(scatterer_lonlat[1]),
            'scatterer_height': float(scatterer_point[1]),
            'tx_azimuth': tx_azimuth,
            'rx_azimuth': rx_azimuth,
            'residual_value': residual_value,
            'reliability': reliability,
            'recv_power': recv_power,
            'comm_rate': comm_rate,
            # 'image_path': get_media_url(f'singlelink/{image_name}'),
            'calculation_duration': calculation_duration,
            'user': user_id,
        }
        try:
            project = resolve_project(user_id, data)
        except ProjectResolveError as e:
            send_ws_message(channel_name, task_id, 'error', {
                "message": e.message
            })
            return

        link_name = (data.get('link_name') or '').strip() or '主链路'
        save_data['name'] = link_name
        existing_link = SingleLink.objects.filter(project=project, name=link_name).first()
        if existing_link and existing_link.image_path:
            image_name = existing_link.image_path.split('/')[-1]
        else:
            image_name = f"{safe_filename(project.name)}_{safe_filename(link_name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            save_data['image_path'] = get_media_url(f'singlelink/{image_name}')

        instance = upsert_single_link(project, user_id, link_name, save_data)
        print(f'单链路数据保存成功 id: {instance.id}')

        image_dir = os.path.join(settings.MEDIA_ROOT, 'singlelink')
        os.makedirs(image_dir, exist_ok=True)
        image_path = os.path.join(image_dir, image_name)

        plotter = ElevationPlotter()
        report_progress(channel_name, task_id, 'singlelink progress', 0.93)
        plotter.plot_profile(
            distances, elevs, scatterer_point, tx_barrier, rx_barrier, image_path
        )
        print('image 生成成功')
        report_progress(channel_name, task_id, 'singlelink progress', 1.0)

        send_ws_message(channel_name, task_id, 'singlelink', {
            "id": instance.id,
            'message': '计算成功',
            'distance': round(total_dist_km, 3),
            'median_loss': round(float(final_loss), 3),
            'tx_height': int(tx_height),
            'rx_height': int(rx_height),
            'tx_theta': round(theta_t, 3),
            'rx_theta': round(theta_r, 3),
            'theta_scatter': round(theta_scatter, 3),
            'area': climate_area,
            'max_height': int(max_height),
            'tx_barrier_distance': round(float(tx_barrier[0] / 1000), 3),
            'tx_barrier_height': int(abs(tx_barrier[1] - tx_height)),
            'rx_barrier_distance': round(float((total_dist - rx_barrier[0]) / 1000), 3),
            'rx_barrier_height': int(abs(rx_barrier[1] - rx_height)),
            'scatterer_lon': float(scatterer_lonlat[0]),
            'scatterer_lat': float(scatterer_lonlat[1]),
            'scatterer_height': int(scatterer_point[1]),
            'tx_azimuth': round(tx_azimuth, 2),
            'rx_azimuth': round(rx_azimuth, 2),
            'residual_value': round(residual_value, 3),
            'reliability': round(reliability, 3),
            'recv_power': round(recv_power, 3),
            'comm_rate': comm_rate,
            'image_url': get_media_url(f'singlelink/{image_name}'),
            'profile_samples': profile_samples,
            'min_height': min_height,
            'scatterer_distance': round(float(scatterer_point[0] / 1000), 3),
            'tx_barrier_elev': int(tx_barrier[1]),
            'rx_barrier_elev': int(rx_barrier[1]),
        })

    except TaskCancelledException as e:
        print(f"[单链路计算] {e}")
    except Exception as e:
        print(f"[单链路计算错误] {e}")
        traceback.print_exc()
        send_ws_message(channel_name, task_id, 'error', {
            "message": f"单链路计算失败: {str(e)}",
        })


@shared_task(name='tasks.calculate_coverage_common')
def calculate_coverage_common(user_id: int, channel_name: str, data: dict, area_type: str):
    task_id = current_task.request.id

    try:
        # 参数提取
        tx_lon = float(data['tx_lon'])
        tx_lat = float(data['tx_lat'])
        freq = int(data['freq'])
        colors = data['colors']
        min_val = float(data['min_val'])
        max_val = float(data['max_val'])
        if data.get('climate_num'):  # 气候区编号
            climate_num = int(data.get('climate_num'))
        else:
            climate_num = None

        # 存入数据库数据
        save_data = {
            'name': data['name'],
            'tx_station_name': data['tx_station_name'],
            'tx_longitude': tx_lon,
            'tx_latitude': tx_lat,
            'frequency': freq,
            'coverage_type': area_type,
            'user': user_id,
            'tx_gain': int(data['tx_gain']),
            'rx_gain': int(data['rx_gain']),
            'diversity_order': int(data['diversity_order']),
            'trans_power': int(data['trans_power']),
            'comm_rate': data['comm_rate'],
            'image_colors': ' '.join(colors),
            'image_min': min_val,
            'image_max': max_val,
        }

        start_time = time.time()
        check_cancellation(f"task:{task_id}")
        print(f'开始计算')

        if area_type == 'rectangle':
            min_lon = min(float(data['min_lon']), float(data['max_lon']))
            min_lat = min(float(data['min_lat']), float(data['max_lat']))
            max_lon = max(float(data['min_lon']), float(data['max_lon']))
            max_lat = max(float(data['min_lat']), float(data['max_lat']))
            print(f'计算矩形区域覆盖，左下角({min_lon}, {min_lat})，右上角({max_lon}, {max_lat})')
            area_km2 = (max_lon - min_lon) * 111 * (max_lat - min_lat) * 111
            print(f'面积约 {area_km2:.2f} 平方公里')

            save_data['rectangle_min_longitude'] = min_lon
            save_data['rectangle_min_latitude'] = min_lat
            save_data['rectangle_max_longitude'] = max_lon
            save_data['rectangle_max_latitude'] = max_lat
            save_data['calculation_area'] = area_km2

            planner = CoveragePlanner2(
                tx_lon, tx_lat, min_lon, min_lat, max_lon, max_lat, freq, climate_num,
                cancel_check=lambda: check_cancellation(f"task:{task_id}"),
            )
            planner.plan_rectangle_coverage(channel_name, task_id, progress_callback=report_progress)

        else:  # circle
            center_lon = float(data['center_lon'])
            center_lat = float(data['center_lat'])
            radius_m = int(data['radius_m'])
            area_km2 = np.pi * (radius_m / 1000) ** 2
            print(f'面积约 {area_km2:.2f} 平方公里')

            save_data['circle_center_longitude'] = center_lon
            save_data['circle_center_latitude'] = center_lat
            save_data['circle_radius'] = radius_m
            save_data['calculation_area'] = area_km2

            earth_radius = 6371000
            lon_range = radius_m / (earth_radius * np.cos(np.radians(center_lat)))
            lat_range = radius_m / earth_radius

            min_lon = center_lon - np.degrees(lon_range)
            min_lat = center_lat - np.degrees(lat_range)
            max_lon = center_lon + np.degrees(lon_range)
            max_lat = center_lat + np.degrees(lat_range)

            planner = CoveragePlanner2(
                tx_lon, tx_lat, min_lon, min_lat, max_lon, max_lat, freq, climate_num,
                cancel_check=lambda: check_cancellation(f"task:{task_id}"),
            )
            planner.plan_circle_coverage(center_lon, center_lat, radius_m, channel_name, task_id, progress_callback=report_progress)

        check_cancellation(f"task:{task_id}")

        elapsed = time.time() - start_time
        calculation_duration = f'{int(elapsed // 60)}分{elapsed % 60:.2f}秒'
        print(f"计算结束 用时{calculation_duration}")
        save_data['calculation_duration'] = calculation_duration

        try:
            project = resolve_project(user_id, data)
        except ProjectResolveError as e:
            send_ws_message(channel_name, task_id, 'error', {
                "message": e.message,
            })
            return

        save_data['name'] = project.name
        existing = AreaCoverage.objects.filter(project=project).first()
        if existing and existing.tif_path and existing.image_path:
            tif_name = existing.tif_path.split('/')[-1]
            png_name = existing.image_path.split('/')[-1]
        else:
            stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_stem = f"{area_type}_area_{safe_filename(project.name)}_{stamp}"
            tif_name = f"{file_stem}.tif"
            png_name = f"{file_stem}.png"
            save_data['tif_path'] = f'/media/areacoverage/{tif_name}'
            save_data['image_path'] = get_media_url(f'areacoverage/{png_name}')

        instance = upsert_area_coverage(project, user_id, save_data)
        print(f'区域覆盖数据保存成功 id: {instance.id}')

        image_dir = os.path.join(settings.MEDIA_ROOT, 'areacoverage')
        # print(f'区域覆盖文件夹路径 {image_dir}')
        os.makedirs(image_dir, exist_ok=True)
        tif_path = os.path.join(image_dir, tif_name)
        png_path = os.path.join(image_dir, png_name)
        # print(f'区域覆盖tif文件路径 {tif_path}')

        planner.write_tiff(tif_path)
        print(f'tiff 生成成功 {tif_name}')

        convert_tif_to_image(
            input_tif_path=tif_path,
            output_image_path=png_path,
            colors=colors,
            min_val=min_val,
            max_val=max_val,
        )
        print(f'image 生成成功 {png_name}')

        report_progress(channel_name, task_id, 'coverage progress', 1.0)

        send_ws_message(channel_name, task_id, f'{area_type} area', {
            "id": instance.id,
            'message': '计算成功',
            'tif_image_url': f'/media/areacoverage/{tif_name}',
            'png_image_url': get_media_url(f'areacoverage/{png_name}'),
        })
    except TaskCancelledException:
        print(f'任务 {task_id} 已响应中止信号')

    except Exception as e:
        print(f"[区域覆盖计算错误] {e}")
        traceback.print_exc()
        send_ws_message(channel_name, task_id, 'error', {
            "message": f"区域覆盖计算失败: {str(e)}",
        })


@shared_task(name='tasks.calculate_clustering')
def calculate_clustering(user_id: int, channel_name: str, data: dict, area_type: str):
    task_id = current_task.request.id
    redis_task_key = f"task:{task_id}"
    temp_tif_abs_path = None

    try:
        start_time = time.time()

        # 初始状态检查
        check_cancellation(redis_task_key)

        # 数据解析与参数初始化
        loss_threshold = data.get('loss_threshold')  # 单位：dB
        eps_m = data.get('eps_cells')  # 单位：米
        min_samples = data.get('min_samples')  # 单位：个
        # p = data.get('p', 50)  # 百分比，默认50%
        limit_road_distance= int(data.get('limit_road_distance'))  # 道路距离限制 米(m)
        is_relay_area = data.get('id') is None
        tif_path = data.get('tif_path')

        # 禁区参数处理
        prohibited_area_type = data.get('prohibited_area_type')

        if prohibited_area_type == 'rectangle':
            p_min_lon = min(float(data['prohibited_min_lon']), float(data['prohibited_max_lon']))
            p_max_lon = max(float(data['prohibited_min_lon']), float(data['prohibited_max_lon']))
            p_min_lat = min(float(data['prohibited_min_lat']), float(data['prohibited_max_lat']))
            p_max_lat = max(float(data['prohibited_min_lat']), float(data['prohibited_max_lat']))

        elif prohibited_area_type == 'circle':
            p_center_lon = float(data['prohibited_center_lon'])
            p_center_lat = float(data['prohibited_center_lat'])
            p_radius_m = int(data['prohibited_radius_m'])

            earth_radius = 6371000
            lon_range = p_radius_m / (earth_radius * np.cos(np.radians(p_center_lat)))
            lat_range = p_radius_m / earth_radius

            p_min_lon = p_center_lon - np.degrees(lon_range)
            p_min_lat = p_center_lat - np.degrees(lat_range)
            p_max_lon = p_center_lon + np.degrees(lon_range)
            p_max_lat = p_center_lat + np.degrees(lat_range)

        # 数据库对象准备 (AreaCoverage)
        area_coverage = None
        if not is_relay_area:
            with transaction.atomic():  # 使用事务确保删除和更新原子性
                area_id = data.get('id')
                area_coverage = AreaCoverage.objects.select_for_update().get(id=area_id)
                area_coverage.loss_threshold = loss_threshold
                area_coverage.eps_cells = eps_m
                area_coverage.min_samples = min_samples
                area_coverage.p = 50
                area_coverage.limit_road_distance = limit_road_distance
                area_coverage.subrange_type = area_type

                # 更新禁区信息
                if prohibited_area_type == 'rectangle':
                    area_coverage.prohibited_min_longitude = p_min_lon
                    area_coverage.prohibited_max_longitude = p_max_lon
                    area_coverage.prohibited_min_latitude = p_min_lat
                    area_coverage.prohibited_max_latitude = p_max_lat

                elif prohibited_area_type == 'circle':
                    area_coverage.prohibited_center_longitude = p_center_lon
                    area_coverage.prohibited_center_latitude = p_center_lat
                    area_coverage.prohibited_radius = p_radius_m

                # 删除旧站点
                Stations.objects.filter(area=area_coverage).delete()
                print(f"已清理 AreaCoverage ID={area_id} 的旧数据")

        # 区域几何计算 (rectangle / circle)
        if area_type == 'rectangle':
            min_lon = min(float(data['min_lon']), float(data['max_lon']))
            min_lat = min(float(data['min_lat']), float(data['max_lat']))
            max_lon = max(float(data['min_lon']), float(data['max_lon']))
            max_lat = max(float(data['min_lat']), float(data['max_lat']))
            print(f'计算矩形区域聚类，左下角({min_lon}, {min_lat})，右上角({max_lon}, {max_lat})')
            area_km2 = (max_lon - min_lon) * 111 * (max_lat - min_lat) * 111
            print(f'面积约 {area_km2:.2f} 平方公里')

            if not is_relay_area:
                area_coverage.subrange_rectangle_min_longitude = min_lon  # 子区域矩形最小经度
                area_coverage.subrange_rectangle_max_longitude = max_lon  # 子区域矩形最大经度
                area_coverage.subrange_rectangle_min_latitude = min_lat  # 子区域矩形最小纬度
                area_coverage.subrange_rectangle_max_latitude = max_lat  # 子区域矩形最大纬度

        else:
            center_lon = float(data['center_lon'])
            center_lat = float(data['center_lat'])
            radius_m = int(data['radius_m'])
            area_km2 = np.pi * (radius_m / 1000) ** 2
            print(f'面积约 {area_km2:.2f} 平方公里')

            if not is_relay_area:
                area_coverage.subrange_circle_center_longitude = center_lon  # 子区域圆心经度
                area_coverage.subrange_circle_center_latitude = center_lat  # 子区域圆心纬度
                area_coverage.subrange_circle_radius = radius_m  # 子区域圆半径(m)

            earth_radius = 6371000
            lon_range = radius_m / (earth_radius * np.cos(np.radians(center_lat)))
            lat_range = radius_m / earth_radius

            min_lon = center_lon - np.degrees(lon_range)
            min_lat = center_lat - np.degrees(lat_range)
            max_lon = center_lon + np.degrees(lon_range)
            max_lat = center_lat + np.degrees(lat_range)

        check_cancellation(redis_task_key)  # 再次检查

        # 覆盖规划(CoveragePlanner)
        if not is_relay_area and data.get('relay_lon') and data.get('relay_lat'):
            relay_lon = float(data.get('relay_lon'))
            relay_lat = float(data.get('relay_lat'))
            area_coverage.relay_longitude = relay_lon
            area_coverage.relay_latitude = relay_lat
            freq = area_coverage.frequency
            if area_coverage.coverage_type == 'rectangle':
                coverage_min_lon = area_coverage.rectangle_min_longitude
                coverage_min_lat = area_coverage.rectangle_min_latitude
                coverage_max_lon = area_coverage.rectangle_max_longitude
                coverage_max_lat = area_coverage.rectangle_max_latitude
                coverage_planner = CoveragePlanner2(
                    relay_lon, relay_lat,
                    coverage_min_lon, coverage_min_lat, coverage_max_lon, coverage_max_lat,
                    freq,
                    cancel_check=lambda: check_cancellation(redis_task_key),
                )
                coverage_planner.plan_rectangle_coverage(channel_name, task_id, progress_callback=report_progress)
            else:  # circle
                coverage_center_lon = area_coverage.circle_center_longitude
                coverage_center_lat = area_coverage.circle_center_latitude
                coverage_radius_m = area_coverage.circle_radius

                earth_radius = 6371000
                coverage_lon_range = coverage_radius_m / (earth_radius * np.cos(np.radians(coverage_center_lat)))
                coverage_lat_range = coverage_radius_m / earth_radius

                coverage_min_lon = coverage_center_lon - np.degrees(coverage_lon_range)
                coverage_min_lat = coverage_center_lat - np.degrees(coverage_lat_range)
                coverage_max_lon = coverage_center_lon + np.degrees(coverage_lon_range)
                coverage_max_lat = coverage_center_lat + np.degrees(coverage_lat_range)

                coverage_planner = CoveragePlanner2(
                    relay_lon, relay_lat,
                    coverage_min_lon, coverage_min_lat, coverage_max_lon, coverage_max_lat,
                    freq,
                    cancel_check=lambda: check_cancellation(redis_task_key),
                )
                coverage_planner.plan_circle_coverage(
                    coverage_center_lon,
                    coverage_center_lat,
                    coverage_radius_m,
                    channel_name,
                    task_id,
                    progress_callback=report_progress
                )

            # 相对于中继点出发的区域损耗
            tif_path = f'/media/temp_coverage_{task_id}.tif'
            temp_tif_abs_path = os.path.join(settings.MEDIA_ROOT, tif_path[7:])
            coverage_planner.write_tiff(temp_tif_abs_path)
            print('重新计算损耗结束')

        report_progress(channel_name, task_id, 'coverage progress', 0.993)

        check_cancellation(redis_task_key)  # 再次检查

        # 聚类分析 (ClusteringAnalysis)
        # print(f'tif路径{tif_path}')
        planner = ClusteringAnalysis(
            tif_path,
            min_lon, min_lat, max_lon, max_lat,
            loss_threshold, eps_m, min_samples
        )

        if area_type == 'circle':
            planner.cut_cicle(center_lon, center_lat, radius_m)
        # 执行聚类分析
        cluster_stats = planner.cluster()
        print(cluster_stats, len(cluster_stats))
        
        report_progress(channel_name, task_id, 'coverage progress', 0.995)

        check_cancellation(redis_task_key)  # 再次检查

        # 结果处理与路网匹配
        # 预编译 SQL，复用 cursor
        road_query_sql = """
            WITH user_point AS (SELECT ST_SetSRID(ST_MakePoint(%s, %s), 4326) AS geom)
            SELECT gid, name, 
                   ST_X(ST_ClosestPoint(nr.geom, up.geom)) as r_lon,
                   ST_Y(ST_ClosestPoint(nr.geom, up.geom)) as r_lat,
                   ST_Distance(ST_Transform(nr.geom, 3857), ST_Transform(up.geom, 3857)) as dist
            FROM dandong nr, user_point up
            WHERE ST_DWithin(nr.geom, up.geom, 0.01) -- 优化：先用粗筛减少计算量 (约1km范围)
            ORDER BY nr.geom <-> up.geom ASC -- PostGIS KNN 操作符优化排序
            LIMIT 1;
        """

        with connection.cursor() as cursor:
            result_stations = []
            # print(cluster_stats)
            for i, info in enumerate(cluster_stats):
                lon, lat = info['min_loss_point']
                elevation = info['min_loss_evl']

                # 禁区判断 (如果在禁区内则跳过)
                if prohibited_area_type and p_min_lon < lon < p_max_lon and p_min_lat < lat < p_max_lat:
                    # print(123)
                    continue

                # 执行路网查询
                cursor.execute(road_query_sql, [lon, lat])
                row = cursor.fetchone()
                print(row)

                if not row:
                    print(456)
                    continue

                _, road_name, road_lon, road_lat, distance = row

                # 距离限制判断
                if limit_road_distance < distance:
                    print(789)
                    continue

                # 计算坡度
                road_elevation = planner.get_elevation(road_lon, road_lat)
                slope = 0
                if distance > 0:
                    slope = math.degrees(math.atan((elevation - road_elevation) / distance))
                    slope = round(abs(slope), 2)

                # 构建返回对象
                st_name = f"{'中继' if is_relay_area else '推荐'}站点{info['cluster'] + 1}"
                station_data = {
                    'name': st_name,
                    'longitude': lon,
                    'latitude': lat,
                    'count': info['num_points'],
                    'to_road_name': road_name,
                    'to_road_distance': round(distance, 2),
                    'slope': slope
                }

                # 准备入库数据
                if not is_relay_area:
                    # 使用 Serializer 验证数据是个好习惯，但为了性能可以考虑批量创建
                    # 这里保持原有 Serializer 逻辑，但收集起来最后统一提交或者放在事务里
                    save_data = {
                        'name': st_name,
                        'center_longitude': lon,
                        'center_latitude': lat,
                        'count': info['num_points'],
                        'to_road_name': road_name,
                        'to_road_slope': slope,
                        'to_road_distance': distance,
                        'area': area_id,
                    }
                    serializer = StationsSerializer(data=save_data)
                    if serializer.is_valid():
                        # 注意：如果在循环内save，务必确保外层有 transaction
                        station_obj = serializer.save()
                        station_data['id'] = station_obj.id

                result_stations.append(station_data)

        # for info in cluster_stats:
        #     print(f"站点 {info['cluster']}: 点数={info['num_points']}，位置={info['center']}")
        #     # lon, lat = info['center'][0], info['center'][1]
        #     # elevation = info['elevation']
        #     lon, lat = info['min_loss_point'][0], info['min_loss_point'][1]
        #     elevation = info['min_loss_evl']
        #
        #     if prohibited_area_type:
        #         if p_min_lon < lon < p_max_lon and p_min_lat < lat < p_max_lat:
        #             continue
        #
        #     with connection.cursor() as cursor:
        #         # 对于MULTILINESTRING，使用ST_ClosestPoint获取线上最接近用户点的坐标
        #         # 使用参数化查询避免SQL注入
        #         cursor.execute("""
        #             WITH user_point AS (
        #                 SELECT ST_SetSRID(ST_MakePoint(%s, %s), 4326) AS geom
        #             ),
        #             normalized_roads AS (
        #                 SELECT gid, name, geom,
        #                        CASE
        #                            WHEN ST_SRID(geom) = 0 OR ST_SRID(geom) IS NULL THEN
        #                                ST_SetSRID(geom, 4326)
        #                            WHEN ST_SRID(geom) = 4326 THEN
        #                                geom
        #                            ELSE
        #                                ST_SetSRID(geom, 4326)
        #                        END AS geom_4326
        #                 FROM china_roadnet2
        #                 WHERE geom IS NOT NULL
        #                   AND ST_IsValid(geom)
        #             )
        #             SELECT gid, name,
        #                    ST_X(ST_ClosestPoint(nr.geom_4326, up.geom)) AS road_lon,
        #                    ST_Y(ST_ClosestPoint(nr.geom_4326, up.geom)) AS road_lat,
        #                    ST_Distance(
        #                        ST_Transform(nr.geom_4326, 3857),
        #                        ST_Transform(up.geom, 3857)
        #                    ) AS distance
        #             FROM normalized_roads nr
        #             CROSS JOIN user_point up
        #             ORDER BY distance ASC
        #             LIMIT 1;
        #         """, [lon, lat])
        #         select_result = cursor.fetchone()
        #
        #     if select_result is None:
        #         print(f"警告: 未找到最近的路径，跳过该站点 (lon: {lon}, lat: {lat})")
        #         continue
        #
        #     nearest_id, nearest_name, road_lon, road_lat, distance = select_result
        #
        #     if road_lon is None or road_lat is None:
        #         print(f"警告: 无法获取路径最近点坐标，跳过该站点 (lon: {lon}, lat: {lat})")
        #         continue
        #
        #     road_elevation = planner.get_elevation(road_lon, road_lat)
        #
        #     # 3857坐标系距离单位是米
        #     if distance == 0:
        #         slope = 0
        #     else:
        #         slope_radians = math.atan((elevation - road_elevation) / distance)
        #         slope = math.degrees(slope_radians)  # 转换为角度制
        #         slope = round(abs(slope), 2)
        #
        #     station_obj = {
        #         # 'id': station.id,
        #         'name': f"中继站点{info['cluster'] + 1}",
        #         'longitude': lon,
        #         'latitude': lat,
        #         'count': info['num_points'],
        #         'to_road_name': nearest_name,
        #         'to_road_distance': round(distance, 2),
        #         'slope': slope,
        #     }
        #     if not is_relay_area:
        #         station_obj['name'] = f"推荐站点{info['cluster'] + 1}"
        #         save_data = {
        #             'name': station_obj['name'],
        #             'center_longitude': station_obj['longitude'],
        #             'center_latitude': station_obj['latitude'],
        #             'count': info['num_points'],
        #             'to_road_name': station_obj['to_road_name'],
        #             'to_road_slope': station_obj['slope'],
        #             'to_road_distance': distance,
        #             'area': area_id,
        #         }
        #         serializer = StationsSerializer(data=save_data)
        #         if serializer.is_valid():
        #             station = serializer.save()  # 保存数据并获取对象
        #             # print(f"已保存站点 ID: {station.id}")
        #             station_obj['id'] = station.id
        #         else:
        #             print(f"站点数据序列化失败: {serializer.errors}")
        #             continue
        #
        #     # 收集返回给前端的简要信息
        #     result_stations.append(station_obj)

        report_progress(channel_name, task_id, 'coverage progress', 0.997)

        elapsed = time.time() - start_time
        calculation_duration = f'{int(elapsed // 60)}分{elapsed % 60:.2f}秒'
        print(f"聚类计算结束，用时{calculation_duration}")
        if not is_relay_area and area_coverage:
            area_coverage.cluster_duration = calculation_duration
            area_coverage.save()
            print(f"已更新AreaCoverage记录: {area_coverage}")

        report_progress(channel_name, task_id, 'coverage progress', 1.0)

        # 返回结果
        send_ws_message(channel_name, task_id, f'{area_type} area clustering', {
            'message': '计算成功',
            'stations': result_stations,
            'stations_type': 'relay stations' if is_relay_area else 'recv stations',
            'calculation_duration': calculation_duration
        })
    except TaskCancelledException:
        print(f'任务 {task_id} 已响应中止信号')

    except Exception as e:
        # import traceback
        # traceback.print_exc()  # 打印堆栈方便调试
        print(f"[聚类系统错误] TaskID: {task_id}, Error: {e}")
        send_ws_message(channel_name, task_id, "error", {"message": f"计算失败: {str(e)}"})

    finally:
        # 清理临时文件 (如果有生成且不再需要)
        if temp_tif_abs_path and os.path.exists(temp_tif_abs_path):
            os.remove(temp_tif_abs_path)
        pass
