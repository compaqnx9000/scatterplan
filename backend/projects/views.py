from os import path, remove, makedirs
import math
from datetime import datetime
# import json

import pandas as pd
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiResponse, OpenApiExample
from rest_framework import viewsets, mixins, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
# from django.contrib.gis.geos import Point
# from django.contrib.gis.db.models.functions import Distance

from .models import SingleLink, AreaCoverage, Stations
from .serializers import (
    SingleLinkSerializer,
    AreaCoverageSerializer,
    # DandongSerializer,
    StationsSerializer,
    ColorSettingReqSerializer,
    ColorSettingResSerializer,
    RecalculateFadeMarginReqSerializer,
    RecalculateFadeMarginResSerializer
)
# from scripts.clustering_analysis import ClusteringAnalysis
from scripts.tif2png import convert_tif_to_image
from scripts import utils


# 单链路查询删除
class SingleLinkViewSet(mixins.ListModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = SingleLinkSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'area', 'user__username']
    search_fields = ['name']
    ordering_fields = ['id', 'created_at']

    def get_queryset(self):
        """
        管理员可以查看所有记录，普通用户只能查看自己的记录
        """
        user = self.request.user

        queryset = SingleLink.objects.select_related('user')
        if user.is_staff or user.is_superuser:
            return queryset.order_by('-id')
        else:
            return queryset.filter(user=user).order_by('-id')

    def perform_destroy(self, instance):
        """
        管理员可以删除任意记录，普通用户只能删除自己的记录
        """
        user = self.request.user
        if not (user.is_staff or user.is_superuser or instance.user == user):
            raise PermissionDenied("你没有权限删除这个工程")

        # 删除关联的图片文件
        if instance.image_path:
            file_path = path.join(settings.MEDIA_ROOT, instance.image_path)
            if path.exists(file_path):
                try:
                    remove(file_path)
                    print(f"已删除文件: {file_path}")
                except Exception as e:
                    print(f"删除文件失败: {file_path}, 错误: {e}")

        # 删除数据库记录
        instance.delete()


# 区域覆盖查询删除
class AreaCoverageViewSet(mixins.ListModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = AreaCoverageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'user__username']
    search_fields = ['name']
    ordering_fields = ['id', 'created_at']

    def get_queryset(self):
        """
        管理员可以查看所有记录，普通用户只能查看自己的记录
        """
        user = self.request.user

        queryset = AreaCoverage.objects.select_related('user')
        if user.is_staff or user.is_superuser:
            return queryset.order_by('-id')
        else:
            return queryset.filter(user=user).order_by('-id')

    def list(self, request, *args, **kwargs):
        area_coverage_id = request.query_params.get('area_coverage_id')
        if area_coverage_id:
            # 如果传了 area_coverage_id，就查 Station 数据
            try:
                area = AreaCoverage.objects.get(pk=area_coverage_id)
            except AreaCoverage.DoesNotExist:
                return Response({'error': '指定的 AreaCoverage 不存在'}, status=404)

            user = request.user
            if not (user.is_staff or user.is_superuser or area.user == user):
                raise PermissionDenied("你没有权限查看该工程的站点")

            stations = Stations.objects.filter(area=area)
            serializer = StationsSerializer(stations, many=True)
            return Response({
                'stations': serializer.data,
                'calculation_duration': area.cluster_duration,
            })

        # 否则返回 AreaCoverage 列表（原本逻辑）
        return super().list(request, *args, **kwargs)

    def perform_destroy(self, instance):
        """
        管理员可以删除任意记录，普通用户只能删除自己的记录
        """
        user = self.request.user
        if not (user.is_staff or user.is_superuser or instance.user == user):
            raise PermissionDenied("你没有权限删除这个工程")

        # 删除关联的图片文件
        tif_path = instance.tif_path.split('media/', 1)[-1]
        image_path = instance.image_path.split('media/', 1)[-1]
        abs_tif_path = path.join(settings.MEDIA_ROOT, tif_path)
        abs_image_path = path.join(settings.MEDIA_ROOT, image_path)
        if path.exists(abs_tif_path):
            try:
                remove(abs_tif_path)
                print(f"已删除文件: {abs_tif_path}")
            except Exception as e:
                print(f"删除文件失败: {abs_tif_path}, 错误: {e}")
        if path.exists(abs_image_path):
            try:
                remove(abs_image_path)
                print(f"已删除文件: {abs_image_path}")
            except Exception as e:
                print(f"删除文件失败: {abs_image_path}, 错误: {e}")

        if instance.excel_path:
            excel_path = instance.excel_path.split('media/', 1)[-1]
            abs_excel_path = path.join(settings.MEDIA_ROOT, excel_path)
            if path.exists(abs_excel_path):
                try:
                    remove(abs_excel_path)
                    print(f"已删除文件: {abs_excel_path}")
                except Exception as e:
                    print(f"删除文件失败: {abs_excel_path}, 错误: {e}")

        # 删除数据库记录
        instance.delete()


# class SitePlannerView(APIView):
#     """
#     处理站点规划的POST请求
#     """
#
#     def post(self, request, *args, **kwargs):
#         # 获取请求数据
#         id = request.data.get('id')
#         tif_path = request.data.get('tif_path')
#         loss_threshold = request.data.get('loss_threshold')  # 单位：dB
#         eps_m = request.data.get('eps_cells')  # 单位：米
#         min_samples = request.data.get('min_samples')  # 单位：个
#         p = request.data.get('p', 50)  # 百分比，默认50%
#         area_type = request.data.get('area_type')  # rectangle 和 circle
#
#         # 验证必需参数
#         if not all([id, tif_path, loss_threshold, eps_m, min_samples]):
#             return Response(
#                 {'error': '参数缺失，请确保 tif_path、loss_threshold、eps_cells 和 min_samples 均已提供'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # 查找并更新AreaCoverage记录
#         try:
#             area_coverage = AreaCoverage.objects.get(id=id)
#             area_coverage.loss_threshold = loss_threshold
#             area_coverage.eps_cells = eps_m
#             area_coverage.min_samples = min_samples
#             area_coverage.p = p
#             area_coverage.save()
#             print(f"已更新AreaCoverage记录: {area_coverage}")
#
#             # 删除该 AreaCoverage 下的所有旧站点
#             Stations.objects.filter(area=area_coverage).delete()
#             print(f"已删除 AreaCoverage ID={id} 下的所有旧站点")
#
#         except AreaCoverage.DoesNotExist:
#             return Response(
#                 {'error': '指定的AreaCoverage记录不存在'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         abs_tif_path = path.join(settings.MEDIA_ROOT, tif_path[7:])
#
#         try:
#             # 创建SitePlanner实例
#             planner = SitePlanner(
#                 tif_path=abs_tif_path,
#                 loss_threshold=float(loss_threshold),
#                 eps_m=int(eps_m),
#                 min_samples=int(min_samples),
#                 p=int(p)
#             )
#
#             # 执行聚类分析
#             cluster_stats = planner.cluster()
#             result = []
#
#             for info in cluster_stats:
#                 print(f"站点 {info['cluster']}: 点数={info['num_points']}，位置={info['center']}")
#                 lon, lat = info['center'][0], info['center'][1]
#                 elevation = info['elevation']
#
#                 user_point = Point(lon, lat, srid=4326)
#                 user_point_proj = user_point.transform(3857, clone=True)
#
#                 nearest = (
#                     Dandong.objects.annotate(distance=Distance('geom', user_point_proj))
#                     .order_by('distance')
#                     .first()
#                 )
#
#                 road_geom = nearest.geom
#                 road_point = road_geom.centroid
#                 road_lon, road_lat = road_point.x, road_point.y
#                 road_elevation = planner.get_elevation(road_lon, road_lat)
#
#                 horizontal_distance = nearest.distance.m
#                 if horizontal_distance == 0:
#                     slope = 0
#                 else:
#                     slope = round((elevation - road_elevation) / horizontal_distance, 6)
#
#                 # serializer = DandongSerializer(nearest)
#                 # info['nearest_road'] = {
#                 #     "id": nearest.pk,
#                 #     "name": nearest.name,
#                 #     "distance_m": round(horizontal_distance, 2),
#                 #     "geometry": serializer.data['geometry'],
#                 #     "slope": slope,
#                 # }
#
#                 save_data = {
#                     'center_longitude': lon,
#                     'center_latitude': lat,
#                     'count': info['num_points'],
#                     'to_road_name': nearest.name,
#                     'to_road_slope': slope,
#                     'to_road_distance': horizontal_distance,
#                     'area': id,
#                 }
#                 serializer = StationsSerializer(data=save_data)
#                 if serializer.is_valid():
#                     station = serializer.save()  # 保存数据并获取对象
#                     # print(f"已保存站点 ID: {station.id}")
#
#                     # 收集返回给前端的简要信息
#                     result.append({
#                         'id': station.id,
#                         'longitude': lon,
#                         'latitude': lat,
#                         'count': info['num_points'],
#                         'to_road_name': nearest.name,
#                         'to_road_distance': round(horizontal_distance, 2),
#                         'slope': slope,
#                     })
#                 else:
#                     print(f"序列化失败: {serializer.errors}")
#
#             # 返回结果
#             return Response({
#                 'message': 'success',
#                 # 'cluster_stats': cluster_stats,
#                 # 'stations': [{'longitude': s[0], 'latitude': s[1]} for s in planner.stations],
#                 'stations': result,
#             }, status=status.HTTP_200_OK)
#
#         except Exception as e:
#             return Response(
#                 {'error': f'Clustering failed: {str(e)}'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


# 设置色带
class ColorSetting(APIView):
    """
    处理图像色彩设置的 POST 请求
    """

    @extend_schema(
        description='色带设置接口',
        request=ColorSettingReqSerializer,
        examples=[
            OpenApiExample(
                '正常请求示例',
                value={
                    'id': 123,
                    'tif_path': 'data/elevation.tif',
                    'png_path': 'images/elevation.png',
                    'colors': [
                        '#0000FF',  # 蓝
                        '#00FFFF',  # 青
                        '#00FF00',  # 绿
                        '#FFFF00',  # 黄
                        '#FFA500',  # 橙
                        '#FF4500',  # 暗橙
                        '#FF0000',  # 红
                    ],
                    'min_val': 100.0,
                    'max_val': 300.0,
                },
                request_only=True
            ),
        ],
        responses={
            200: ColorSettingResSerializer,
            400: OpenApiResponse(description='参数错误'),
            404: OpenApiResponse(description='记录不存在'),
            500: OpenApiResponse(description='服务器错误')
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            # 提取参数
            # print(request.data)
            id = request.data.get('id')
            tif_path = request.data.get('tif_path')
            png_path = request.data.get('png_path')
            colors = request.data.get('colors')
            min_val = request.data.get('min_val')
            max_val = request.data.get('max_val')

            # 参数校验
            if not all([tif_path, png_path, colors, min_val, max_val]):
                return Response(
                    {'error': '参数缺失，请确保 tif_path、png_path、colors、min_val 和 max_val 均已提供'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 类型转换和路径处理
            try:
                min_val = float(min_val)
                max_val = float(max_val)
            except ValueError:
                return Response(
                    {'error': 'min_val 和 max_val 应为数值类型'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 清洗路径（去掉 media/ 前缀）
            if 'media/' in tif_path:
                tif_path = tif_path.split('media/', 1)[-1]
            if 'media/' in png_path:
                png_path = png_path.split('media/')[-1].split('?')[0]

            # 拼接绝对路径
            abs_tif_path = path.join(settings.MEDIA_ROOT, tif_path)
            abs_png_path = path.join(settings.MEDIA_ROOT, png_path)

            # 调用处理函数
            convert_tif_to_image(
                input_tif_path=abs_tif_path,
                output_image_path=abs_png_path,
                colors=colors,
                min_val=min_val,
                max_val=max_val,
            )

            # 查找并更新AreaCoverage记录
            try:
                area_coverage = AreaCoverage.objects.get(id=id)
                area_coverage.image_colors = ' '.join(colors)
                area_coverage.image_min = min_val
                area_coverage.image_max = max_val
                area_coverage.save()
                print(f"已更新AreaCoverage记录: {area_coverage}")

            except AreaCoverage.DoesNotExist:
                return Response(
                    {'error': '指定的AreaCoverage记录不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({'message': '图像处理成功'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'图像处理失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 站点选择
class StationSelection(APIView):
    """
    处理站点选择的 POST 请求
    """

    def post(self, request, *args, **kwargs):
        id = request.data.get('id')
        number = request.data.get('number')
        center_longitude = request.data.get('center_longitude')
        center_latitude = request.data.get('center_latitude')
        road_name = request.data.get('road_name')
        road_slope = request.data.get('road_slope')
        road_distance = request.data.get('distance')

        # 验证必需参数
        if not all([id, number, center_longitude, center_latitude, road_name, road_slope, road_distance]):
            return Response(
                {'error': '参数缺失'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 查找并更新AreaCoverage记录
        try:
            area_coverage = AreaCoverage.objects.get(id=id)
            area_coverage.number = number
            area_coverage.rx_center_longitude = center_longitude
            area_coverage.rx_center_latitude = center_latitude
            area_coverage.to_road_name = road_name
            area_coverage.to_road_slope = road_slope
            area_coverage.to_road_distance = road_distance
            area_coverage.save()
            print(f"已更新AreaCoverage记录: {area_coverage}")

            return Response(
                {'message': '应用站点成功'},
                status=status.HTTP_200_OK
            )

        except AreaCoverage.DoesNotExist:
            return Response(
                {'error': '指定的AreaCoverage记录不存在'},
                status=status.HTTP_404_NOT_FOUND
            )


# 站点更新
class StationPartialUpdateView(APIView):
    """
    部分更新 Station，仅限 name 和 number 字段
    PATCH /stations/<id>/
    """

    def patch(self, request, pk, *args, **kwargs):
        try:
            station = Stations.objects.get(pk=pk)
        except Stations.DoesNotExist:
            return Response({'error': '站点不存在'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StationsSerializer(station, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '更新成功', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 站点列表导出到 Excel
class StationExportExcel(APIView):
    """
    处理站点导出的 POST 请求
    """

    def post(self, request, *args, **kwargs):
        try:
            # 获取请求数据
            area_coverage_id = request.data.get('id')

            if not area_coverage_id:
                return Response({'error': '缺少参数 id'}, status=status.HTTP_400_BAD_REQUEST)

            stations = Stations.objects.filter(area=area_coverage_id)
            if not stations.exists():
                return Response({'error': '未找到任何关联的站点'}, status=status.HTTP_404_NOT_FOUND)

            # 序列化数据
            serializer = StationsSerializer(stations, many=True)
            station_data = serializer.data

            # 解析数据
            records = []
            for item in station_data:
                try:
                    # nearest_road = item.get("nearest_road", {})
                    # geometry = nearest_road.get("geometry", {})
                    record = {
                        "站点编号": item.get("number", ""),
                        "站点名称": item.get("name", ""),
                        "站点经度": item.get("center_longitude"),
                        "站点纬度": item.get("center_latitude"),
                        # "点数": item.get("count"),
                        "最近道路名称": item.get("to_road_name"),
                        "站点到最近道路距离（m）": round(item.get("to_road_distance", 0), 2),
                        "站点到最近道路坡度": item.get("to_road_slope"),
                    }
                    records.append(record)
                except Exception as e:
                    # 记录异常但继续处理其他项
                    print(f"[Warning] 单项数据处理失败: {e}")

            if not records:
                return Response(
                    {'error': '无法解析任何有效的 cluster_stats 项目'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 转为 DataFrame
            df = pd.DataFrame(records)

            # 构建文件名和路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            excel_name = f"stations_{timestamp}.xlsx"
            file_dir = path.join(settings.MEDIA_ROOT, 'stations')
            makedirs(file_dir, exist_ok=True)
            excel_path = path.join(file_dir, excel_name)

            # 保存 Excel 文件
            df.to_excel(excel_path, index=False, engine='openpyxl')

            # 更新数据库中的 Excel 路径
            try:
                area_coverage = AreaCoverage.objects.get(id=area_coverage_id)
                area_coverage.excel_path = f'/media/stations/{excel_name}'
                area_coverage.save()
            except AreaCoverage.DoesNotExist:
                return Response(
                    {'error': f'找不到 ID 为 {area_coverage_id} 的区域覆盖对象'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {'message': '站点数据已成功导出', 'file_url': area_coverage.excel_path},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': f'站点数据导出失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 重新计算链路可靠度
class RecalculateFadeMargin(APIView):

    @extend_schema(
        description='重新计算衰落余量',
        request=RecalculateFadeMarginReqSerializer,
        responses={
            200: RecalculateFadeMarginResSerializer,
            400: OpenApiResponse(description='参数错误'),
            404: OpenApiResponse(description='记录不存在'),
            500: OpenApiResponse(description='服务器错误')
        },
        examples=[
            OpenApiExample(
                '正常请求示例',
                value={'id': 1, 'comm_rate': '128kbps'},
                request_only=True
            ),
            OpenApiExample(
                '成功响应示例',
                value={
                    'message': 'success',
                    'residual_value': 15.5,
                    'reliability': 99,
                    'recv_power': 0.005
                },
                response_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        # 获取请求数据
        id = request.data.get('id')
        comm_rate = request.data.get('comm_rate')  # 通信速率

        # 验证必需参数
        if not all([id, comm_rate]):
            return Response(
                {'error': '参数缺失'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            singlelink = SingleLink.objects.get(id=id)
            if not singlelink:
                return Response({'error': '未找到该单链路工程数据'}, status=status.HTTP_404_NOT_FOUND)

            # 序列化数据
            serializer = SingleLinkSerializer(singlelink)
            singlelink_data = serializer.data

            loss = singlelink_data['final_loss']  # 损耗
            tx_gain = singlelink_data['tx_gain']  # 发射增益
            rx_gain = singlelink_data['rx_gain']  # 接收增益
            trans_power = singlelink_data['trans_power']  # 发射功率（W）
            distance = singlelink_data['distance_km']  # 距离（km）
            area = singlelink_data['area']  # 气候类型

            recv_sensitivity = utils.find_recv_sensitivity(comm_rate)  # 接收灵敏度(dBm)
            trans_power_dBm = 10 * math.log10(trans_power * 1000)  # 发射功率（dBm）
            # 接收功率(dBm) = 发射功率(dBm) - 损耗(dB) + 发射增益(dB) + 接收增益(dB)
            recv_power = trans_power_dBm - loss + tx_gain + rx_gain
            # recv_power = math.pow(10, recv_power_dBm / 10)  # 接收功率（mW）
            # 信号衰落余值(dBm) = 接收功率(dBm) - 接收灵敏度(dBm) - 5
            residual_value = recv_power - recv_sensitivity - 5

            # 传播可靠度
            reliability = utils.calculate_reliability(distance, area, residual_value)

            singlelink.comm_rate = comm_rate
            singlelink.reliability = reliability
            singlelink.residual_value = residual_value
            singlelink.recv_power = recv_power
            singlelink.save()

            # 返回结果
            return Response({
                'message': 'success',
                'residual_value': round(residual_value, 3),
                'reliability': reliability,
                'recv_power': round(recv_power, 3),
            }, status=status.HTTP_200_OK)
        except SingleLink.DoesNotExist:
            return Response(
                {'error': '未找到该单链路工程数据'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {"error": f"数据验证失败：{e.detail}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {'error': f'计算报错: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
