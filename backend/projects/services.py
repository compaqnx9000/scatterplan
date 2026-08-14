from .models import Project, AreaCoverage, SingleLink


class ProjectResolveError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


def resolve_project(user_id, data):
    project_id = data.get("project_id")
    if project_id not in (None, "", 0, "0"):
        try:
            return Project.objects.get(pk=int(project_id), user_id=user_id)
        except (Project.DoesNotExist, TypeError, ValueError):
            raise ProjectResolveError("未找到该工程")

    name = (data.get("project_name") or data.get("name") or "").strip()
    if not name:
        raise ProjectResolveError("缺少工程名称")
    project, _created = Project.objects.get_or_create(user_id=user_id, name=name)
    return project


def safe_filename(value, fallback="file"):
    text = "".join(c if c.isalnum() or c in "-_." else "_" for c in str(value or fallback))
    return (text or fallback)[:80]


def upsert_area_coverage(project, user_id, save_data):
    payload = dict(save_data)
    payload.pop("project", None)
    payload.pop("user", None)
    instance = AreaCoverage.objects.filter(project=project).first()
    if instance:
        for key, value in payload.items():
            setattr(instance, key, value)
        instance.user_id = user_id
        instance.project = project
        instance.save()
        return instance
    instance = AreaCoverage(project=project, user_id=user_id, **payload)
    instance.save()
    return instance


def upsert_single_link(project, user_id, link_name, save_data):
    payload = dict(save_data)
    payload.pop("project", None)
    payload.pop("user", None)
    payload["name"] = link_name
    instance = SingleLink.objects.filter(project=project, name=link_name).first()
    if instance:
        for key, value in payload.items():
            setattr(instance, key, value)
        instance.user_id = user_id
        instance.project = project
        instance.save()
        return instance
    instance = SingleLink(project=project, user_id=user_id, **payload)
    instance.save()
    return instance
