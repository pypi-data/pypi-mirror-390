from rest_framework import serializers

from ichec_django_core.models import Member

from .core import SERIALIZER_BASE_FIELDS


class MemberBaseSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Member
        fields = SERIALIZER_BASE_FIELDS + (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "profile",
        )
        read_only_fields = SERIALIZER_BASE_FIELDS


class MemberResponseSerializer(MemberBaseSerializer):

    profile = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="member_profiles"
    )
    profile_thumbnail = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="member_profile_thumbnails"
    )

    class Meta:
        model = Member
        fields = MemberBaseSerializer.Meta.fields + (
            "organizations",
            "profile_thumbnail",
        )
        read_only_fields = ("profile", "profile_thumbnail", "organizations")

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.profile:
            rep["profile"] = None
        if not instance.profile_thumbnail:
            rep["profile_thumbnail"] = None
        return rep


class MemberDetailResponseSerializer(MemberResponseSerializer):

    permissions = serializers.SerializerMethodField("get_all_permissions")

    class Meta:
        model = Member
        fields = MemberResponseSerializer.Meta.fields + ("permissions",)
        read_only_fields = MemberResponseSerializer.Meta.read_only_fields + (
            "permissions",
        )

    def get_all_permissions(self, obj):
        return obj.get_all_permissions()


class MemberListSerializer(MemberBaseSerializer):
    class Meta:
        model = Member
        fields = MemberBaseSerializer.Meta.fields
        read_only_fields = MemberBaseSerializer.Meta.read_only_fields

    def to_representation(self, instance):
        return MemberResponseSerializer(context=self.context).to_representation(
            instance
        )


class MemberDetailSerializer(MemberBaseSerializer):
    class Meta:
        model = Member
        fields = MemberBaseSerializer.Meta.fields
        read_only_fields = MemberBaseSerializer.Meta.read_only_fields

    def to_representation(self, instance):
        return MemberDetailResponseSerializer(context=self.context).to_representation(
            instance
        )
