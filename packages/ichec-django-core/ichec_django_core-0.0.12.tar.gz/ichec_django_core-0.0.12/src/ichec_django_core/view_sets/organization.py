from rest_framework import permissions, viewsets

from ichec_django_core.models import Organization, Address

from ichec_django_core.serializers import (
    OrganizationDetailSerializer,
    OrganizationListSerializer,
    AddressSerializer,
)

from .core import SearchableModelViewSet
from .permissions import MemberEditOrDjangoModelPermissions


class OrganizationViewSet(SearchableModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationListSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        MemberEditOrDjangoModelPermissions,
    ]
    ordering_fields = SearchableModelViewSet.ordering_fields + ("name",)
    ordering: tuple[str, ...] = ("name",)
    search_fields = ["name", "address__line1", "address__country", "address__region"]

    serializers = {
        "retrieve": OrganizationDetailSerializer,
        "list": OrganizationListSerializer,
        "create": OrganizationDetailSerializer,
        "update": OrganizationDetailSerializer,
        "partial_update": OrganizationDetailSerializer,
    }


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all().order_by("id")
    serializer_class = AddressSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
