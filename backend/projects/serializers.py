from rest_framework import serializers
from rest_framework.validators import UniqueValidator
# from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import SingleLink, AreaCoverage, Stations


class SingleLinkSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    name = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(queryset=SingleLink.objects.all(), message="名称已存在")]
    )

    class Meta:
        model = SingleLink
        fields = '__all__'


class AreaCoverageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    name = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(queryset=AreaCoverage.objects.all(), message="名称已存在")]
    )

    class Meta:
        model = AreaCoverage
        fields = '__all__'


# class DandongSerializer(GeoFeatureModelSerializer):
#     class Meta:
#         model = Dandong
#         geo_field = 'geom'
#         fields = '__all__'


class StationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stations
        fields = '__all__'


class ColorSettingReqSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tif_path = serializers.CharField()
    png_path = serializers.CharField()
    colors = serializers.ListField(child=serializers.CharField())
    min_val = serializers.FloatField()
    max_val = serializers.FloatField()


class ColorSettingResSerializer(serializers.Serializer):
    # status = serializers.CharField()
    message = serializers.CharField()


class RecalculateFadeMarginReqSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="单链路工程ID")
    comm_rate = serializers.CharField(help_text="通信速率")


class RecalculateFadeMarginResSerializer(serializers.Serializer):
    message = serializers.CharField()
    residual_value = serializers.FloatField()
    reliability = serializers.FloatField()
    recv_power = serializers.FloatField()
