from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from ichec_django_core.view_sets import ObjectFileDownloadView
from ichec_django_core.view_sets.core import SearchableModelViewSet
from ichec_django_core.view_sets.permissions import (
    EditOrDjangoModelPermissions,
    get_permission,
)

from marinerg_facility.models import Equipment, Facility
from marinerg_facility.serializers import EquipmentSerializer


class OrgMemberEditOrDjangoModelPermissions(EditOrDjangoModelPermissions):

    def object_perm_check(self, obj, request) -> bool:
        return request.user.id in [m.id for m in obj.factility.members]


class EquipmentViewSet(SearchableModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        OrgMemberEditOrDjangoModelPermissions,
    ]
    ordering_fields = SearchableModelViewSet.ordering_fields + ("name",)
    ordering: tuple[str, ...] = ("name",)
    search_fields = ["name"]

    def get_queryset(self):
        queryset = Equipment.objects.all()
        facility_id = self.request.query_params.get("facility")
        if facility_id is not None:
            queryset = queryset.filter(facility__id=facility_id)
        return queryset

    def check_field_permissions(self, request, serializer):
        is_facility_member = self._is_facility_member(
            serializer.validated_data["facility"], request.user.id
        )
        can_edit_facility = get_permission(Facility, "edit")

        if not (is_facility_member or can_edit_facility):
            raise PermissionDenied(
                detail="Permission to add Equipment to this Facility denied."
            )

    def _is_facility_member(self, url: str, user_id: int) -> bool:
        return user_id in [m.id for m in Facility.get(url=url).members]


class EquipmentImageDownloadView(ObjectFileDownloadView):
    model = Equipment
    file_field = "image"


class EquipmentThumbnailDownloadView(ObjectFileDownloadView):
    model = Equipment
    file_field = "thumbnail"
