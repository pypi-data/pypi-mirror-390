from rest_framework import permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from ichec_django_core.models import Member

from ichec_django_core.serializers import MemberListSerializer, MemberDetailSerializer

from .core import SearchableModelViewSet
from .files import ObjectFileDownloadView, ObjectFileUploadView
from .permissions import SelfEditOrDjangoModelPermissions


class MemberViewSet(SearchableModelViewSet):

    queryset = Member.objects.all()
    serializer_class = MemberListSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        SelfEditOrDjangoModelPermissions,
    ]
    ordering_fields = SearchableModelViewSet.ordering_fields + ("username",)
    ordering: tuple[str, ...] = ("username",)
    search_fields = ["username", "first_name", "last_name", "email"]

    serializers = {
        "retrieve": MemberDetailSerializer,
        "list": MemberListSerializer,
        "create": MemberDetailSerializer,
        "update": MemberDetailSerializer,
        "partial_update": MemberDetailSerializer,
    }

    def get_queryset(self):
        queryset = Member.objects.all().order_by("id")
        org_id = self.request.query_params.get("organization")
        if org_id is not None:
            queryset = queryset.filter(organizations__id=org_id)
        call_id = self.request.query_params.get("call")
        if call_id is not None:
            queryset = queryset.filter(access_boards__id=call_id)
        return queryset


class MemberProfileDownloadView(ObjectFileDownloadView):
    model = Member
    file_field = "profile"
    permissions_class = permissions.DjangoModelPermissions


class MemberProfileThumbnailDownloadView(ObjectFileDownloadView):
    model = Member
    file_field = "profile_thumbnail"
    permissions_class = permissions.DjangoModelPermissions


class MemberProfileUploadView(ObjectFileUploadView):
    model = Member
    queryset = Member.objects.all()
    file_field = "profile"
    permission_classes = [
        permissions.IsAuthenticated,
        SelfEditOrDjangoModelPermissions,
    ]


class CustomAuthToken(ObtainAuthToken):

    authentication_classes: list = []

    """
    This overrides DRFs built in api auth token view
    so we return some more user details. This helps clients
    fetch the user post auth.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key, "user_id": user.pk})
