from rest_framework import serializers
from .models import Project, SingleLink, AreaCoverage, Stations


class SingleLinkSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = SingleLink
        fields = "__all__"
        validators = []


class AreaCoverageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = AreaCoverage
        fields = "__all__"
        validators = []


class StationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stations
        fields = "__all__"


class ProjectListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    single_link_count = serializers.IntegerField(read_only=True)
    has_coverage = serializers.BooleanField(read_only=True)
    station_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "user",
            "username",
            "created_at",
            "updated_at",
            "single_link_count",
            "has_coverage",
            "station_count",
        ]
        extra_kwargs = {
            "user": {"read_only": True},
        }
        validators = []

    def validate_name(self, value):
        name = (value or "").strip()
        if not name:
            raise serializers.ValidationError("请输入工程名称")
        request = self.context.get("request")
        user = getattr(request, "user", None)
        qs = Project.objects.filter(name=name)
        if user and user.is_authenticated:
            qs = qs.filter(user=user)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("工程名称已存在")
        return name


class ProjectDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    single_links = SingleLinkSerializer(many=True, read_only=True)
    coverage = serializers.SerializerMethodField()
    stations = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "user",
            "username",
            "created_at",
            "updated_at",
            "single_links",
            "coverage",
            "stations",
        ]

    def _coverage(self, obj):
        try:
            return obj.coverage
        except AreaCoverage.DoesNotExist:
            return None

    def get_coverage(self, obj):
        coverage = self._coverage(obj)
        if coverage is None:
            return None
        return AreaCoverageSerializer(coverage).data

    def get_stations(self, obj):
        coverage = self._coverage(obj)
        if coverage is None:
            return []
        return StationsSerializer(coverage.stations.all(), many=True).data


class ColorSettingReqSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tif_path = serializers.CharField()
    png_path = serializers.CharField()
    colors = serializers.ListField(child=serializers.CharField())
    min_val = serializers.FloatField()
    max_val = serializers.FloatField()


class ColorSettingResSerializer(serializers.Serializer):
    message = serializers.CharField()


class RecalculateFadeMarginReqSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="单链路工程ID")
    comm_rate = serializers.CharField(help_text="通信速率")


class RecalculateFadeMarginResSerializer(serializers.Serializer):
    message = serializers.CharField()
    residual_value = serializers.FloatField()
    reliability = serializers.FloatField()
    recv_power = serializers.FloatField()
