import json
import asyncio
from os import path, makedirs
from time import time
from datetime import datetime
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from concurrent.futures import ProcessPoolExecutor, as_completed
from django.conf import settings
from scripts.elevation_plotter import ElevationPlotter
from scripts.climate_loss_calculator import ClimateLossCalculator
from scripts.coverage_planner import CoveragePlanner, compute_profile_loss_standalone
from scripts.coverage_tiff_exporter import CoverageTiffExporter
from scripts.tif2png import convert_tif_to_image
from scripts.dem_profile_extractor import DemProfileExtractor
from projects.serializers import SingleLinkSerializer


class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # await self.accept()
        # print("[WebSocket] 连接建立")
        # 检查用户是否已认证
        if self.scope["user"].is_authenticated:
            await self.accept()
            print(f"[WebSocket] 用户 {self.scope['user']} 连接建立")
        else:
            # 如果需要认证才能连接，可以拒绝连接
            await self.close(code=4001)
            # 或者允许连接但标记为未认证用户
            # await self.accept()
            # print("[WebSocket] 未认证连接建立")

    async def disconnect(self, close_code):
        print(f"[WebSocket] 连接关闭，代码：{close_code}")

    async def receive(self, text_data: str):
        try:
            data = json.loads(text_data)
            print(f"[WebSocket] 收到 {self.scope['user']} 数据: {data}")

            message = data.get("message", "")
            type = data.get("type", "")

            if message == "ping":
                await self.send_json({'message': 'pong'})
            elif type == 'singlelink':
                await asyncio.to_thread(self.calculation_singlelink_sync, data)
            elif type == 'rectangle area coverage':
                # await asyncio.to_thread(self.calculation_rectangle_sync, data)
                await asyncio.to_thread(self._calculate_coverage_common, data, 'rectangle')
            elif type == 'circle area coverage':
                # await asyncio.to_thread(self.calculation_circle_sync, data)
                await asyncio.to_thread(self._calculate_coverage_common, data, 'circle')
            elif type == 'ribbon setting':
                await asyncio.to_thread(self._set_ribbon, data)
            elif type == 'clustering analysis':
                pass

        except json.JSONDecodeError:
            await self.send_json({'error': '无效的 JSON 格式'})

    def _report_progress(self, progress):
        """报告进度的辅助方法"""
        # 将进度作为 JSON 发送到前端
        asyncio.run(self.send_json({
            'type': 'progress',
            'progress': round(progress * 100, 2)
        }))

    def calculation_singlelink_sync(self, data: dict):
        """阻塞逻辑放在独立线程中运行"""
        try:
            start_time = time()

            # 参数提取
            tx_lon = float(data['tx_lon'])
            tx_lat = float(data['tx_lat'])
            rx_lon = float(data['rx_lon'])
            rx_lat = float(data['rx_lat'])
            tx_gain = int(data['tx_gain'])
            rx_gain = int(data['rx_gain'])
            freq = int(data['freq'])
            diversity_order = int(data['diversity_order'])
            trans_power = int(data['trans_power'])

            # 报告开始计算
            self._report_progress(0.1)

            calculator = ClimateLossCalculator(tx_lon, tx_lat, rx_lon, rx_lat, tx_gain, rx_gain, freq, diversity_order)

            # 报告开始计算损耗
            self._report_progress(0.3)

            loss, scatterer_point, tx_barrier_point, rx_barrier_point, scatterer_lonlat = calculator.calculate_loss()
            # print(f'lonlat{float(scatterer_lonlat[0])}, {float(scatterer_lonlat[1])}')

            # 报告计算完成
            self._report_progress(0.6)

            distance_km = round(calculator.D[-1] / 1000.0, 3)

            # 方位角
            tx_azimuth, rx_azimuth = calculator.calculate_azimuths(tx_lat, tx_lon, rx_lat, rx_lon)

            # 信号衰落余值，传播可靠度
            residual_value, reliability = calculator.calculate_residual_value()

            # 接收功率
            recv_power = trans_power - loss[-1]
            print(f'接收功率: {recv_power}, 衰落余值: {residual_value}, 信道可靠度: {reliability}')

            image_name = f"{data['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image_dir = path.join(settings.MEDIA_ROOT, 'singlelink')
            makedirs(image_dir, exist_ok=True)
            image_path = path.join(image_dir, image_name)

            # 存入数据库
            save_data = {
                'name': data['name'],
                'tx_lon': tx_lon,
                'tx_lat': tx_lat,
                'tx_height': calculator.H[0],
                'rx_lon': rx_lon,
                'rx_lat': rx_lat,
                'rx_height': calculator.H[-1],
                'tx_gain': tx_gain,
                'rx_gain': rx_gain,
                'freq': freq,
                'diversity_order': diversity_order,
                'trans_power': trans_power,
                'distance_km': distance_km,
                'median_loss': np.median(loss),
                'tx_theta': calculator.theta_t,
                'rx_theta': calculator.theta_r,
                'theta_scatter': calculator.theta_scatter,
                'area': calculator.area,
                'max_height': np.max(calculator.H),
                'tx_barrier_distance': tx_barrier_point[0] / 1000,
                'tx_barrier_height': float(tx_barrier_point[1]),
                'rx_barrier_distance': (calculator.D[-1] - rx_barrier_point[0]) / 1000,
                'rx_barrier_height': float(rx_barrier_point[1]),
                'scatterer_lon': float(scatterer_lonlat[0]),
                'scatterer_lat': float(scatterer_lonlat[1]),
                'scatterer_height': float(scatterer_point[1]),
                'tx_azimuth': tx_azimuth,
                'rx_azimuth': rx_azimuth,
                'residual_value': residual_value,
                'reliability': reliability,
                'recv_power': recv_power,
                'image_path': 'singlelink/' + image_name,
                'user': self.scope['user'].id,
            }
            serializer = SingleLinkSerializer(data=save_data)
            if serializer.is_valid():
                instance = serializer.save()
                print(f'单链路数据存入库成功 id: {instance.id}')
                # 可选：发送成功消息、返回 ID 等
                # asyncio.run(self.send_json({
                #     "status": "success",
                #     "id": instance.id,
                # }))
            else:
                asyncio.run(self.send_json({
                    "type": "error",
                    "errors": serializer.errors,
                    "message": "数据验证失败",
                }))
                return

            plotter = ElevationPlotter()
            plotter.plot_profile(
                calculator.D, calculator.H, scatterer_point, tx_barrier_point, rx_barrier_point, image_path
            )

            # 报告绘图完成
            self._report_progress(0.9)

            elapsed = time() - start_time
            print(f"计算用时{int(elapsed // 60)}分{elapsed % 60:.2f}秒")

            # send() 是异步方法，线程中不能直接调用，改为排队发送
            asyncio.run(self.send_json({
                'type': 'singlelink',
                'message': '计算成功',
                'distance': round(distance_km, 3),
                'median_loss': round(float(np.median(loss)), 3),
                'tx_height': int(calculator.H[0]),
                'rx_height': int(calculator.H[-1]),
                'tx_theta': round(float(calculator.theta_t), 3),
                'rx_theta': round(float(calculator.theta_r), 3),
                'theta_scatter': round(float(calculator.theta_scatter), 3),
                'area': calculator.area,
                'max_height': int(np.max(calculator.H)),
                'tx_barrier_distance': round(float(tx_barrier_point[0] / 1000), 3),
                'tx_barrier_height': int(tx_barrier_point[1]),
                'rx_barrier_distance': round(float((calculator.D[-1] - rx_barrier_point[0]) / 1000), 3),
                'rx_barrier_height': int(rx_barrier_point[1]),
                'scatterer_lon': float(scatterer_lonlat[0]),
                'scatterer_lat': float(scatterer_lonlat[1]),
                'scatterer_height': int(scatterer_point[1]),
                'tx_azimuth': tx_azimuth,
                'rx_azimuth': rx_azimuth,
                'image_url': f"/media/singlelink/{image_name}",
            }))

            # 报告完成
            self._report_progress(1.0)

        except Exception as e:
            print(f"[错误] {e}")
            asyncio.run(self.send_json({'error': f'计算失败: {str(e)}'}))
