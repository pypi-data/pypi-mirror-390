from django.contrib.auth.models import Group

from rest_framework import serializers
from rest_framework.utils import model_meta


SERIALIZER_BASE_FIELDS = ("id", "url", "created_at", "updated_at")


class NestedHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):

    base_fields = SERIALIZER_BASE_FIELDS

    def pop_many_to_many(self, validated_data) -> dict:
        ModelClass = self.Meta.model
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)
        return many_to_many

    def add_many_to_many(self, instance, many_to_many):
        if not many_to_many:
            return

        for field_name, value in many_to_many.items():
            field = getattr(instance, field_name)
            field.set(value)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name", "id"]
