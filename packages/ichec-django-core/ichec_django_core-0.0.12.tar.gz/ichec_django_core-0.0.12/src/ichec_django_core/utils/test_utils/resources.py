from .models import (
    MemberCreate,
    MemberDetail,
    AddressCreate,
    OrganizationCreate,
    GroupCreate,
)


def create_members(count: int = 100, offset: int = 0) -> list[MemberCreate]:

    content = []
    for idx in range(offset, count + offset):
        content.append(
            MemberCreate(
                username=f"member_{idx}",
                email=f"member_{idx}@example.com",
                first_name="Script",
                last_name=f"User {idx}",
            )
        )
    return content


def create_groups(count: int = 100, offset: int = 0) -> list[GroupCreate]:
    content = []

    for idx in range(offset, count + offset):
        content.append(GroupCreate(name=f"Script Group {idx}"))
    return content


def create_organizations(
    count: int = 100, offset: int = 0, possible_members: tuple[MemberDetail, ...] = ()
) -> list[OrganizationCreate]:
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

        item = OrganizationCreate(
            name=f"Organization {idx}",
            acronym=f"ORG {idx}",
            description=f"Description of org {idx}",
            address=address,
            website=f"www.org{idx}.com",
            members=members,
        )

        content.append(item)
    return content
