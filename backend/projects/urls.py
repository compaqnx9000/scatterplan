from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    SingleLinkViewSet,
    AreaCoverageViewSet,
    MapTileServiceViewSet,
    # SitePlannerView,
    ColorSetting,
    # StationSelection,
    StationPartialUpdateView,
    StationExportExcel,
    RecalculateFadeMargin,
)

router = DefaultRouter()
router.register(r'plans', ProjectViewSet, basename='project')
router.register(r'singlelinks', SingleLinkViewSet, basename='singlelink')
router.register(r'areacoverages', AreaCoverageViewSet, basename='areacoverage')
router.register(r'map-services', MapTileServiceViewSet, basename='map-service')

urlpatterns = [
    path('', include(router.urls)),
    # path('clustering/', SitePlannerView.as_view()),
    path('ribbon-setting/', ColorSetting.as_view()),
    # path('station-selection/', StationSelection.as_view()),
    path('stations/<int:pk>/', StationPartialUpdateView.as_view(), name='station-partial-update'),
    path('station-export-excel/', StationExportExcel.as_view()),
    path('recalculate-fade-margin/', RecalculateFadeMargin.as_view()),
]
