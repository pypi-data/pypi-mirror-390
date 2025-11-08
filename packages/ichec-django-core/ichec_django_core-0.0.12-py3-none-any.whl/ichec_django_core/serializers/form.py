from rest_framework import serializers

from ..models import Form, FormField, FormFieldValue, FormGroup, PopulatedForm


class FormFieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = FormField
        fields = (
            "id",
            "label",
            "key",
            "required",
            "description",
            "template",
            "options",
            "default",
            "field_type",
            "order",
        )
        read_only_fields = ("id",)


class FormGroupSerializer(serializers.ModelSerializer):

    fields = FormFieldSerializer(many=True)

    class Meta:
        model = FormGroup
        fields = (
            "id",
            "label",
            "description",
            "order",
            "fields",
        )
        read_only_fields = ("id",)


class FormSerializer(serializers.ModelSerializer):

    groups = FormGroupSerializer(many=True)

    class Meta:
        model = Form
        fields = ("groups", "id")
        read_only_fields = ("id",)

    def create(self, validated_data):
        groups = validated_data.pop("groups")

        instance = super().create(validated_data)

        for group in groups:
            fields = group.pop("fields")
            group_instance = FormGroup.objects.create(form=instance, **group)
            FormField.objects.bulk_create(
                [FormField(group=group_instance, **field) for field in fields]
            )
        return instance


class FormFieldValueDetailSerializer(serializers.ModelSerializer):

    field = FormFieldSerializer(read_only=True)

    class Meta:
        model = FormFieldValue
        fields = ("id", "value", "field")
        read_only_fields = ("id", "field")


class FormFieldValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = FormFieldValue
        fields = ("id", "value", "field")
        read_only_fields = ("id",)

    def to_representation(self, instance):
        return FormFieldValueDetailSerializer(context=self.context).to_representation(
            instance
        )


class PopulatedFormSerializer(serializers.ModelSerializer):

    values = FormFieldValueSerializer(many=True)

    class Meta:
        model = PopulatedForm
        fields = ("id", "values")
        read_only_fields = ("id",)

    def create(self, validated_data):
        values = validated_data.pop("values")

        instance = super().create(validated_data)

        FormFieldValue.objects.bulk_create(
            [FormFieldValue(form=instance, **value) for value in values]
        )
        return instance
