import os

from django.conf import settings
from django.db import migrations


def wipe_history(apps, schema_editor):
    Stations = apps.get_model("projects", "Stations")
    SingleLink = apps.get_model("projects", "SingleLink")
    AreaCoverage = apps.get_model("projects", "AreaCoverage")
    Stations.objects.all().delete()
    SingleLink.objects.all().delete()
    AreaCoverage.objects.all().delete()

    media_root = getattr(settings, "MEDIA_ROOT", "")
    if not media_root:
        return
    for folder in ("singlelink", "areacoverage", "stations"):
        directory = os.path.join(media_root, folder)
        if not os.path.isdir(directory):
            continue
        for name in os.listdir(directory):
            file_path = os.path.join(directory, name)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0025_areacoverage_limit_road_distance"),
    ]

    operations = [
        migrations.RunPython(wipe_history, migrations.RunPython.noop),
    ]
