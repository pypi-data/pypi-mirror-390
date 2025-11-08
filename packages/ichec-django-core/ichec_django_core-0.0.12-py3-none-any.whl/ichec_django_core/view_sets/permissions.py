from rest_framework import permissions


class DjangoModelPermissionsWithView(permissions.DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


def get_permission(model_t, perm_t: str) -> str:
    return f"{model_t._meta.app_label}.{perm_t}_{model_t._meta.model_name}"


class CustomDjangoModelPermissions(permissions.DjangoModelPermissions):

    intercept_methods: list = []
    safe_methods: list = ["HEAD", "OPTIONS"]

    def has_authenticated_user(self, request) -> bool:
        return request.user and request.user.is_authenticated

    def method_handled_by_object(self, method: str) -> bool:
        return method in self.intercept_methods

    def is_safe_method(self, method: str) -> bool:
        return method in self.safe_methods

    def has_permission(self, request, view):

        if not self.has_authenticated_user(request):
            return False

        # Fall through to allow permission checks to happen at object level
        if self.method_handled_by_object(request.method):
            return True

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):

        # Allow metadata checks on endpoint
        if self.is_safe_method(request.method):
            return True

        if not self.has_authenticated_user(request):
            return super().has_permission(request, view)

        # If the method is handled by the object, then dispatch delegate the check to it
        if self.method_handled_by_object(request.method) and self.object_perm_check(
            obj, request
        ):
            return True

        # Otherwise fall back to Django model permissions
        return super().has_permission(request, view)

    def object_perm_check(self, obj, request) -> bool:
        raise NotImplementedError


class FullOrDjangoModelPermissions(CustomDjangoModelPermissions):

    intercept_methods: list = ["PUT", "PATCH", "DELETE"]


class EditOrDjangoModelPermissions(permissions.DjangoModelPermissions):

    intercept_methods: list = ["PUT", "PATCH"]


class OwnerFullOrDjangoModelPermissions(FullOrDjangoModelPermissions):

    owner_field = "owner"

    def object_perm_check(self, obj, request) -> bool:
        return getattr(obj, self.owner_field).id == request.user.id


class SelfEditOrDjangoModelPermissions(EditOrDjangoModelPermissions):

    def object_perm_check(self, obj, request) -> bool:
        return obj.id == request.user.id


class MemberEditOrDjangoModelPermissions(EditOrDjangoModelPermissions):

    member_field = "members"

    def object_perm_check(self, obj, request) -> bool:
        return request.user.id in [m.id for m in getattr(obj, self.member_field)]
