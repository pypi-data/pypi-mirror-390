from rest_framework import serializers

from ichec_django_core.serializers.core import SERIALIZER_BASE_FIELDS

from marinerg_facility.models import Equipment


class EquipmentBaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Equipment
        fields = SERIALIZER_BASE_FIELDS + (
            "name",
            "description",
            "image",
            "thumbnail",
            "facility",
        )
        read_only_fields = SERIALIZER_BASE_FIELDS + ("thumbnail",)


class EquipmentResponseSerializer(EquipmentBaseSerializer):

    image = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="equipment_images"
    )
    thumbnail = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="equipment_thumbnails"
    )

    class Meta:
        model = Equipment
        fields = EquipmentBaseSerializer.Meta.fields
        read_only_fields = EquipmentBaseSerializer.Meta.read_only_fields + ("image",)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.image:
            rep["image"] = None
        if not instance.thumbnail:
            rep["thumbnail"] = None
        return rep


class EquipmentSerializer(EquipmentBaseSerializer):
    class Meta:
        model = Equipment
        fields = EquipmentBaseSerializer.Meta.fields
        read_only_fields = EquipmentBaseSerializer.Meta.read_only_fields

    def to_representation(self, instance):
        return EquipmentResponseSerializer(context=self.context).to_representation(
            instance
        )
