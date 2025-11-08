from django.urls import include, path
from django.contrib import admin
from django.conf import settings

from .view_sets import (
    MemberViewSet,
    MemberProfileDownloadView,
    MemberProfileThumbnailDownloadView,
    MemberProfileUploadView,
    GroupViewSet,
    OrganizationViewSet,
    FeedbackViewSet,
    AddressViewSet,
    CustomAuthToken,
)


def register_drf_views(router):
    router.register(r"groups", GroupViewSet)
    router.register(r"organizations", OrganizationViewSet)
    router.register(r"members", MemberViewSet)
    router.register(r"addresses", AddressViewSet)
    router.register(r"feedback", FeedbackViewSet)
    return router


urlpatterns = [
    path("api-token-auth/", CustomAuthToken.as_view()),
    path(f"{settings.API_AUTH_URL}/", include("rest_framework.urls")),
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
    path(
        r"api/members/<int:pk>/profile",
        MemberProfileDownloadView.as_view(),
        name="member_profiles",
    ),
    path(
        r"api/members/<int:pk>/profile/thumbnail",
        MemberProfileThumbnailDownloadView.as_view(),
        name="member_profile_thumbnails",
    ),
    path(
        r"api/members/<int:pk>/profile/upload",
        MemberProfileUploadView.as_view(),
        name="member_profiles_upload",
    ),
]

if settings.WITH_OIDC:
    urlpatterns += [path("oidc/", include("mozilla_django_oidc.urls"))]
