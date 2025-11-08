from rest_framework import permissions

from ichec_django_core.view_sets import ObjectFileDownloadView, ObjectFileUploadView
from ichec_django_core.view_sets.core import SearchableModelViewSet
from ichec_django_core.view_sets.permissions import MemberEditOrDjangoModelPermissions

from marinerg_facility.models import Facility
from marinerg_facility.serializers import (
    FacilityListSerializer,
    FacilityDetailSerializer,
)


class FacilityViewSet(SearchableModelViewSet):

    queryset = Facility.objects.all()
    serializer_class = FacilityListSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        MemberEditOrDjangoModelPermissions,
    ]
    ordering_fields = SearchableModelViewSet.ordering_fields + ("name",)
    ordering: tuple[str, ...] = ("name",)
    search_fields = ["name", "address__line1", "address__country", "address__region"]

    serializers = {
        "retrieve": FacilityDetailSerializer,
        "list": FacilityListSerializer,
        "create": FacilityDetailSerializer,
        "update": FacilityDetailSerializer,
        "partial_update": FacilityDetailSerializer,
    }

    def get_queryset(self):
        queryset = Facility.objects.all()
        member_id = self.request.query_params.get("user")
        if member_id is not None:
            queryset = queryset.filter(members__id=member_id)
        return queryset


class FacilityImageDownloadView(ObjectFileDownloadView):
    model = Facility
    file_field = "image"


class FacilityThumbnailDownloadView(ObjectFileDownloadView):
    model = Facility
    file_field = "thumbnail"


class FacilityImageUploadView(ObjectFileUploadView):
    model = Facility
    queryset = Facility.objects.all()
    file_field = "image"
    permission_classes = [
        permissions.IsAuthenticated,
        MemberEditOrDjangoModelPermissions,
    ]
