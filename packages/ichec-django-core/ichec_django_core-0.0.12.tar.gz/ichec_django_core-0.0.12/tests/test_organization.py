from django.contrib.auth.models import User
from rest_framework import status

from ichec_django_core.models import Organization, Address

from ichec_django_core.utils.test_utils.test_client import (
    setup_default_users_and_groups,
    add_group_permissions,
    AuthAPITestCase,
)


class OgranizationViewTests(AuthAPITestCase):

    template = {
        "name": "My Org",
        "acronym": "MO",
        "description": "An description of the org",
        "address": {"line1": "1234 Street", "region": "Region", "country": "IE"},
        "website": "www.org.org",
    }
    update_template = {"address": {"country": "FR"}}

    def setUp(self):
        self.url = "/api/organizations/"

        setup_default_users_and_groups()

        add_group_permissions(
            "admins",
            Organization,
            ["change_organization", "add_organization"],
        )

        add_group_permissions(
            "admins",
            Address,
            ["change_address", "add_address"],
        )

    def test_list_not_authenticated(self):
        self.assert_401(self.do_list())

    def test_detail_not_authenticated(self):
        self.assert_401(self.detail(1))

    def test_list_authenticated(self):
        self.assert_200(self.authenticated_list("regular_user"))

    def test_create_not_authenticated(self):
        self.assert_401(self.create(self.template))

    def test_create_authenticated_no_permission(self):
        self.assert_403(self.authenticated_create("regular_user", self.template))

    def test_create_authenticated_permission(self):
        self.assert_201(self.authenticated_create("admin_user", self.template))

    def test_update_authenticated_permission(self):
        created = self.assert_201(
            self.authenticated_create("admin_user", self.template)
        )

        for key, value in self.update_template.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    created[key][sub_key] = sub_value

        updated = self.assert_200(self.authenticated_update("admin_user", 1, created))

        for key, value in self.update_template.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    self.assertEqual(updated[key][sub_key], sub_value)
