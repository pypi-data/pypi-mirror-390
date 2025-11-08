from rest_framework import serializers

from django_countries.serializers import CountryFieldMixin

from ichec_django_core.models import Organization, Address

from .core import SERIALIZER_BASE_FIELDS, NestedHyperlinkedModelSerializer


class AddressSerializer(CountryFieldMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address
        fields = SERIALIZER_BASE_FIELDS + (
            "line1",
            "line2",
            "line3",
            "city",
            "region",
            "postcode",
            "country",
            "country_name",
            "country_flag",
        )
        read_only_fields = SERIALIZER_BASE_FIELDS + ("country_name", "country_flag")


class OrganizationBaseSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = NestedHyperlinkedModelSerializer.base_fields + (
            "name",
            "acronym",
            "description",
            "address",
            "website",
            "members",
        )
        read_only_fields = NestedHyperlinkedModelSerializer.base_fields


class OrganizationListSerializer(OrganizationBaseSerializer):
    pass


class OrganizationDetailSerializer(OrganizationBaseSerializer):
    address = AddressSerializer()

    def create(self, validated_data):
        address_data = validated_data.pop("address")
        address = Address.objects.create(**address_data)

        many_to_many = self.pop_many_to_many(validated_data)
        instance = Organization.objects.create(address=address, **validated_data)
        self.add_many_to_many(instance, many_to_many)
        return instance

    def update(self, instance, validated_data):
        address_data = validated_data.pop("address")

        instance = super().update(instance, validated_data)
        for attr, value in address_data.items():
            setattr(instance.address, attr, value)
        return instance
