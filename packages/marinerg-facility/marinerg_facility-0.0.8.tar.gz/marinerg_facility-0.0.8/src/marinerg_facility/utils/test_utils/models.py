from pydantic import BaseModel

from ichec_django_core.utils.test_utils.models import (
    Timestamped,
    register_types,
    AddressCreate,
    AddressDetail,
)


class FacilityBase(BaseModel, frozen=True):
    name: str
    acronym: str | None = None
    description: str | None = None
    website: str | None = None
    profile: str = ""
    members: list[str] = []


class FacilityCreate(FacilityBase, frozen=True):
    address: AddressCreate


class FacilityDetail(Timestamped, FacilityBase, frozen=True):
    address: AddressDetail


class EquipmentBase(BaseModel, frozen=True):
    name: str
    description: str | None = None
    image: str = ""
    facility: str


class EquipmentCreate(EquipmentBase, frozen=True):
    pass


class EquipmentDetail(Timestamped, EquipmentBase, frozen=True):
    thumbnail: str
    address: AddressDetail


register_types("facilities", {"create": FacilityCreate, "detail": FacilityDetail})
register_types("equipment", {"create": EquipmentCreate, "detail": EquipmentDetail})
