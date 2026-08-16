from django.db import migrations


def seed_default_roadnet(apps, schema_editor):
    MapTileService = apps.get_model("projects", "MapTileService")
    if MapTileService.objects.filter(name="路网").exists():
        return
    MapTileService.objects.create(
        name="路网",
        service_type="wms",
        url="/geoserver/zk/wms",
        layers="zk:china_roadnet2",
        format="image/png",
        tile_matrix_set_id="EPSG:4326",
        description="默认中国路网 WMS（可通过系统管理修改为本地 GeoServer）",
        enabled=True,
        show_default=False,
        sort_order=0,
    )


def unseed(apps, schema_editor):
    MapTileService = apps.get_model("projects", "MapTileService")
    MapTileService.objects.filter(name="路网", url="/geoserver/zk/wms").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0029_map_tile_service"),
    ]

    operations = [
        migrations.RunPython(seed_default_roadnet, unseed),
    ]
