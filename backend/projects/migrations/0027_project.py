import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0026_project_and_wipe_history"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at", "-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="project",
            constraint=models.UniqueConstraint(fields=("user", "name"), name="uniq_project_user_name"),
        ),
        migrations.AddField(
            model_name="singlelink",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="single_links",
                to="projects.project",
            ),
        ),
        migrations.AddField(
            model_name="areacoverage",
            name="project",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="coverage",
                to="projects.project",
            ),
        ),
        migrations.AddConstraint(
            model_name="singlelink",
            constraint=models.UniqueConstraint(fields=("project", "name"), name="uniq_singlelink_project_name"),
        ),
    ]
