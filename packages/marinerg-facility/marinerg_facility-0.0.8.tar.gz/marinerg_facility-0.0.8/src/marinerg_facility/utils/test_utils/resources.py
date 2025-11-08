from ichec_django_core.utils.test_utils.models import AddressCreate, MemberDetail

from .models import FacilityCreate


def create_facilities(
    count=100, offset: int = 0, possible_members: tuple[MemberDetail, ...] = ()
) -> list[FacilityCreate]:

    content = []

    for idx in range(offset, count + offset):
        address = AddressCreate(
            line1="Apartment 123",
            line2="123 Street",
            city="City",
            region="Region",
            postcode="abc123",
            country="IE",
        )

        members = []
        if possible_members:
            num_members = len(possible_members) - 1
            ids = set(
                [
                    idx % num_members,
                    (idx + 1) % num_members,
                    (idx + 2) % num_members,
                    (idx + 4) % num_members,
                ]
            )
            members = [possible_members[jdx].url for jdx in ids]

        item = FacilityCreate(
            name=f"Facility {idx}",
            acronym=f"FAC {idx}",
            description=f"Description of facility {idx}",
            address=address,
            website=f"www.faciliy{idx}.com",
            members=members,
        )

        content.append(item)

    return content
