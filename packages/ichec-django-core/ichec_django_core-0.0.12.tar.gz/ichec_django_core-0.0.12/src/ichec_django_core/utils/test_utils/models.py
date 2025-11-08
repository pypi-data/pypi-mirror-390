from datetime import datetime

from pydantic import BaseModel


class File:

    def get_content(self):
        pass


class Resource(BaseModel, frozen=True):

    id: int


_TYPE_TO_PATH: dict = {}

_PATH_TO_TYPES: dict = {}


def register_types(label: str, types: dict):

    if "create" not in types:
        types["create"] = types["detail"]
    if "list" not in types:
        types["list"] = types["detail"]

    _PATH_TO_TYPES[label] = types

    for t in types.values():
        _TYPE_TO_PATH[t.__name__] = label


def get_path_from_item(resource: BaseModel) -> str:
    return _TYPE_TO_PATH[type(resource).__name__]


def get_path_from_type(item_t) -> str:
    return _TYPE_TO_PATH[item_t.__name__]


def get_type(path: str, action: str):
    return _PATH_TO_TYPES[path][action]


class Identifiable(Resource, frozen=True):
    url: str


class Timestamped(Identifiable, frozen=True):
    created_at: datetime
    updated_at: datetime


class MemberBase(BaseModel, frozen=True):
    username: str
    email: str
    first_name: str
    last_name: str | None = None
    phone: str | None = None


class MemberCreate(MemberBase, frozen=True):
    profile: str | None = None


class MemberList(Timestamped, MemberBase, frozen=True):
    organizations: list[str] = []
    profile: str | None = None
    thumbnail: str | None = None


class MemberDetail(MemberList, frozen=True):
    permissions: list[str] = []


class GroupBase(BaseModel, frozen=True):
    name: str


class GroupCreate(GroupBase, frozen=True):
    pass


class GroupDetail(Timestamped, GroupBase, frozen=True):
    pass


class AddressBase(BaseModel, frozen=True):
    line1: str
    line2: str | None = None
    line3: str | None = None
    city: str | None = None
    region: str
    postcode: str | None = None
    country: str


class AddressCreate(AddressBase, frozen=True):
    pass


class AddressDetail(Timestamped, AddressBase, frozen=True):
    pass


class OrganizationBase(BaseModel, frozen=True):
    name: str
    acronym: str | None = None
    description: str | None = None
    website: str | None = None
    members: list[str] = []


class OrganizationCreate(OrganizationBase, frozen=True):
    address: AddressCreate


class OrganizationDetail(Timestamped, frozen=True):
    address: AddressDetail


class FormFieldBase(BaseModel, frozen=True):

    label: str
    key: str
    required: bool = False
    description: str = ""
    template: str | None = None
    options: str | None = None
    default: str | None = None
    field_type: str
    order: int = 0


class FormFieldCreate(FormFieldBase, frozen=True):
    pass


class FormFieldDetail(Resource, FormFieldBase, frozen=True):
    pass


class FormGroupBase(BaseModel, frozen=True):
    label: str | None = None
    description: str | None = None
    order: int = 0


class FormGroupCreate(FormGroupBase, frozen=True):
    fields: list[FormFieldCreate] = []


class FormGroupDetail(Resource, FormGroupBase, frozen=True):
    fields: list[FormFieldDetail] = []


class FormBase(BaseModel, frozen=True):
    pass


class FormCreate(FormBase, frozen=True):
    groups: list[FormGroupCreate] = []


class FormDetail(Resource, FormBase, frozen=True):
    groups: list[FormGroupDetail] = []


class FormFieldValueBase(BaseModel, frozen=True):
    value: str
    asset: str | None = None


class FormFieldValueCreate(FormFieldValueBase, frozen=True):
    field: int


class FormFieldValueDetail(Resource, FormFieldValueBase, frozen=True):
    field: FormFieldDetail


class PopulatedFormBase(BaseModel, frozen=True):
    pass


class PopulatedFormCreate(PopulatedFormBase, frozen=True):
    values: list[FormFieldValueCreate] = []


class PopulatedFormDetail(PopulatedFormBase, frozen=True):
    values: list[FormFieldValueDetail] = []


register_types(
    "members", {"create": MemberCreate, "detail": MemberDetail, "list": MemberList}
)
register_types("groups", {"detail": GroupDetail, "create": GroupCreate})
register_types(
    "organizations", {"create": OrganizationCreate, "detail": OrganizationDetail}
)
