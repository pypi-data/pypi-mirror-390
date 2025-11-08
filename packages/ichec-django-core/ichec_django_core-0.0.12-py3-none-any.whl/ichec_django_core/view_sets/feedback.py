from rest_framework import permissions

from ichec_django_core.models import Feedback, Member

from ichec_django_core.serializers import FeedbackSerializer

from .permissions import OwnerFullOrDjangoModelPermissions
from .core import BaseModelViewSet


class CreatorFullOrDjangoModelPermissions(OwnerFullOrDjangoModelPermissions):
    owner_field = "creator"


class FeedbackViewSet(BaseModelViewSet):

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CreatorFullOrDjangoModelPermissions,
    ]

    def filter_self(self, queryset):
        return queryset.filter(creator__id=self.request.user.id)

    def get_queryset(self):
        """
        If the user has view permissions for this model then return all objects,
        otherwise filter by their own objects only.
        """

        queryset = Feedback.objects.all().order_by("id")

        queryset = self.filter_self_or_permission(queryset, Feedback)
        if not queryset:
            return queryset

        creator_id = self.request.query_params.get("creator")
        if creator_id is not None:
            queryset = queryset.filter(creator__id=creator_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=Member.objects.get(id=self.request.user.id))
