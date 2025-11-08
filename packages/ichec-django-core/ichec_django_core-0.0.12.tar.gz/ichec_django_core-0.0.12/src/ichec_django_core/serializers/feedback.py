from rest_framework import serializers

from ichec_django_core.models import Feedback

from .core import SERIALIZER_BASE_FIELDS


class FeedbackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Feedback
        fields = SERIALIZER_BASE_FIELDS + ("creator", "comments")
        read_only_fields = SERIALIZER_BASE_FIELDS + ("creator",)
