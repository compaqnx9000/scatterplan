from django.db import models
from django.utils import timezone
from users.models import CustomUser


class Project(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="uniq_project_user_name"),
        ]
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return self.name

    def touch(self):
        Project.objects.filter(pk=self.pk).update(updated_at=timezone.now())


class SingleLink(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="single_links")
    name = models.CharField(max_length=100)
    tx_lon = models.FloatField()
    tx_lat = models.FloatField()
    tx_height = models.FloatField()
    tx_terrain_height = models.FloatField()
    rx_lon = models.FloatField()
    rx_lat = models.FloatField()
    rx_height = models.FloatField()
    rx_terrain_height = models.FloatField()
    tx_gain = models.IntegerField()
    rx_gain = models.IntegerField()
    freq = models.IntegerField()
    diversity_order = models.IntegerField()
    trans_power = models.IntegerField()
    comm_rate = models.CharField(max_length=20)
    tx_station_name = models.CharField(max_length=100)
    rx_station_name = models.CharField(max_length=100)

    distance_km = models.FloatField()
    median_loss = models.FloatField()
    final_loss = models.FloatField()
    tx_theta = models.FloatField()
    rx_theta = models.FloatField()
    theta_scatter = models.FloatField()
    area = models.CharField(max_length=100)
    max_height = models.FloatField()
    tx_barrier_distance = models.FloatField()
    tx_barrier_height = models.FloatField()
    rx_barrier_distance = models.FloatField()
    rx_barrier_height = models.FloatField()
    scatterer_lon = models.FloatField()
    scatterer_lat = models.FloatField()
    scatterer_height = models.FloatField()
    tx_azimuth = models.FloatField()
    rx_azimuth = models.FloatField()
    residual_value = models.FloatField()
    reliability = models.FloatField()
    recv_power = models.FloatField()
    image_path = models.CharField(max_length=100)
    calculation_duration = models.CharField(max_length=20)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "name"], name="uniq_singlelink_project_name"),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.project_id:
            self.project.touch()


class AreaCoverage(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="coverage")
    name = models.CharField(max_length=100, blank=True, null=True)
    tx_station_name = models.CharField(max_length=100)
    tx_longitude = models.FloatField()
    tx_latitude = models.FloatField()
    frequency = models.IntegerField()
    tx_gain = models.IntegerField()
    rx_gain = models.IntegerField()
    diversity_order = models.IntegerField()
    trans_power = models.IntegerField()
    comm_rate = models.CharField(max_length=20)
    coverage_type = models.CharField(max_length=20)
    rectangle_min_longitude = models.FloatField(blank=True, null=True)
    rectangle_max_longitude = models.FloatField(blank=True, null=True)
    rectangle_min_latitude = models.FloatField(blank=True, null=True)
    rectangle_max_latitude = models.FloatField(blank=True, null=True)
    circle_center_longitude = models.FloatField(blank=True, null=True)
    circle_center_latitude = models.FloatField(blank=True, null=True)
    circle_radius = models.FloatField(blank=True, null=True)
    image_colors = models.CharField(max_length=100)
    image_min = models.FloatField()
    image_max = models.FloatField()
    subrange_type = models.CharField(max_length=20, blank=True, null=True)
    subrange_rectangle_min_longitude = models.FloatField(blank=True, null=True)
    subrange_rectangle_max_longitude = models.FloatField(blank=True, null=True)
    subrange_rectangle_min_latitude = models.FloatField(blank=True, null=True)
    subrange_rectangle_max_latitude = models.FloatField(blank=True, null=True)
    subrange_circle_center_longitude = models.FloatField(blank=True, null=True)
    subrange_circle_center_latitude = models.FloatField(blank=True, null=True)
    subrange_circle_radius = models.FloatField(blank=True, null=True)

    prohibited_area_type = models.CharField(max_length=20, blank=True, null=True)
    prohibited_min_longitude = models.FloatField(blank=True, null=True)
    prohibited_max_longitude = models.FloatField(blank=True, null=True)
    prohibited_min_latitude = models.FloatField(blank=True, null=True)
    prohibited_max_latitude = models.FloatField(blank=True, null=True)
    prohibited_center_longitude = models.FloatField(blank=True, null=True)
    prohibited_center_latitude = models.FloatField(blank=True, null=True)
    prohibited_radius = models.FloatField(blank=True, null=True)

    tif_path = models.CharField(max_length=100)
    image_path = models.CharField(max_length=100)
    calculation_duration = models.CharField(max_length=20)
    calculation_area = models.CharField(max_length=100)
    cluster_duration = models.CharField(max_length=20, blank=True, null=True)

    loss_threshold = models.CharField(max_length=20, blank=True, null=True)
    eps_cells = models.CharField(max_length=20, blank=True, null=True)
    min_samples = models.IntegerField(blank=True, null=True)
    p = models.IntegerField(blank=True, null=True)
    limit_road_distance = models.IntegerField(blank=True, null=True)

    excel_path = models.CharField(max_length=100, blank=True, null=True)

    relay_longitude = models.FloatField(blank=True, null=True)
    relay_latitude = models.FloatField(blank=True, null=True)
    relay_to_road_name = models.CharField(max_length=100, blank=True, null=True)
    relay_to_road_slope = models.FloatField(blank=True, null=True)
    relay_to_road_distance = models.FloatField(blank=True, null=True)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or f"coverage-{self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.project_id:
            self.project.touch()


class Stations(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    number = models.CharField(max_length=100, blank=True, null=True)
    center_longitude = models.FloatField()
    center_latitude = models.FloatField()
    count = models.IntegerField()
    to_road_name = models.CharField(max_length=100)
    to_road_slope = models.FloatField()
    to_road_distance = models.FloatField()

    area = models.ForeignKey(AreaCoverage, on_delete=models.CASCADE, related_name="stations")
    created_at = models.DateTimeField(auto_now_add=True)
