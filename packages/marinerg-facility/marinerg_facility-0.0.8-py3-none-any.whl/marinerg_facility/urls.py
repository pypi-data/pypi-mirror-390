from django.urls import path

from .view_sets import (
    FacilityViewSet,
    EquipmentViewSet,
    FacilityImageDownloadView,
    FacilityImageUploadView,
    FacilityThumbnailDownloadView,
    EquipmentImageDownloadView,
    EquipmentThumbnailDownloadView,
)


def register_drf_views(router):
    router.register(r"facilities", FacilityViewSet)
    router.register(r"equipment", EquipmentViewSet)


urlpatterns = [
    path(
        r"facilities/<int:pk>/image",
        FacilityImageDownloadView.as_view(),
        name="facility_images",
    ),
    path(
        r"facilities/<int:pk>/thumbnail",
        FacilityThumbnailDownloadView.as_view(),
        name="facility_thumbnails",
    ),
    path(
        r"facilities/<int:pk>/image/upload",
        FacilityImageUploadView.as_view(),
        name="facility_images_upload",
    ),
    path(
        r"equipment/<int:pk>/image",
        EquipmentImageDownloadView.as_view(),
        name="equipment_images",
    ),
    path(
        r"equipment/<int:pk>/thumbnail",
        EquipmentThumbnailDownloadView.as_view(),
        name="equipment_thumbnails",
    ),
]
