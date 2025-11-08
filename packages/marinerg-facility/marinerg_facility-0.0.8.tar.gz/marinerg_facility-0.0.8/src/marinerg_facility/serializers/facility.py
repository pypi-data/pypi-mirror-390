from rest_framework import serializers

from marinerg_facility.models import Facility

from ichec_django_core.models import Address
from ichec_django_core.serializers import (
    AddressSerializer,
    NestedHyperlinkedModelSerializer,
)


class FacilityBaseSerializer(NestedHyperlinkedModelSerializer):

    address = AddressSerializer()

    class Meta:
        model = Facility
        fields = NestedHyperlinkedModelSerializer.base_fields + (
            "name",
            "acronym",
            "description",
            "address",
            "website",
            "is_active",
            "members",
            "image",
            "thumbnail",
            "equipment",
        )
        read_only_fields = NestedHyperlinkedModelSerializer.base_fields + (
            "equipment",
            "thumbnail",
        )


class FacilityResponseSerializer(FacilityBaseSerializer):

    image = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="facility_images"
    )
    thumbnail = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="facility_thumbnails"
    )

    class Meta:
        model = Facility
        fields = FacilityBaseSerializer.Meta.fields
        read_only_fields = FacilityBaseSerializer.Meta.read_only_fields + ("image",)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.image:
            rep["image"] = None
        if not instance.thumbnail:
            rep["thumbnail"] = None
        return rep


class FacilityListSerializer(FacilityBaseSerializer):

    def to_representation(self, instance):
        return FacilityResponseSerializer(context=self.context).to_representation(
            instance
        )


class FacilityDetailSerializer(FacilityBaseSerializer):

    def to_representation(self, instance):
        return FacilityResponseSerializer(context=self.context).to_representation(
            instance
        )

    def create(self, validated_data):
        address_data = validated_data.pop("address")
        address = Address.objects.create(**address_data)

        many_to_many = self.pop_many_to_many(validated_data)
        instance = Facility.objects.create(address=address, **validated_data)
        self.add_many_to_many(instance, many_to_many)
        return instance

    def update(self, instance, validated_data):
        address_data = validated_data.pop("address")

        instance = super().update(instance, validated_data)
        for attr, value in address_data.items():
            setattr(instance.address, attr, value)
        return instance
