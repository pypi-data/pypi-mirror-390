from django.contrib.auth.models import Group

from rest_framework import permissions, viewsets, filters, status
from rest_framework.response import Response

from ichec_django_core.serializers import GroupSerializer

from .permissions import get_permission

BASE_ORDERING_FIELDS = ("id", "created_at", "updated_at")


class BaseModelViewSet(viewsets.ModelViewSet):

    def filter_self_or_permission(self, queryset, model_t):
        if self.request.method == "GET":
            if self.request.user:
                if not self.has_model_view_permission(model_t):
                    return self.filter_self(queryset)
            else:
                return None
        return queryset

    def filter_self(self, queryset):
        return queryset

    def has_model_view_permission(self, model_t) -> bool:
        return self.self_has_permission(get_permission(model_t, "view"))

    def self_has_permission(self, perm: str) -> bool:
        return self.request.user.has_perm(perm)

    def get_serializer_class(self):
        if hasattr(self, "serializers"):
            return self.serializers.get(self.action, self.serializer_class)
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.check_field_permissions(request, serializer)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.check_field_permissions(request, serializer)

        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def check_field_permissions(self, _request, _serializer):
        pass


class SearchableModelViewSet(BaseModelViewSet):
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields: tuple[str, ...] = BASE_ORDERING_FIELDS
    ordering: tuple[str, ...] = ("id",)


class GroupViewSet(SearchableModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    ordering_fields: tuple[str, ...] = ("name",)
    ordering: tuple[str, ...] = ("name",)
    search_fields: tuple[str, ...] = ("name",)

    def get_queryset(self):
        queryset = Group.objects.all()
        user_id = self.request.query_params.get("user")
        if user_id is not None:
            queryset = queryset.filter(user__id=user_id)
        return queryset
