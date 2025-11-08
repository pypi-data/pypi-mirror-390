from django.contrib.auth.models import User
from rest_framework import status

from ichec_django_core.models import Feedback

from ichec_django_core.utils.test_utils.test_client import (
    setup_default_users_and_groups,
    add_group_permissions,
    AuthAPITestCase,
)


class FeedbackViewTests(AuthAPITestCase):

    template = {"comments": "This is some feedback"}
    update_template = {"comments": "This is some edited feedback"}

    def setUp(self):
        self.url = "/api/feedback/"

        setup_default_users_and_groups()

        add_group_permissions(
            "admins",
            Feedback,
            ["add_feedback"],
        )

        add_group_permissions(
            "regular_users",
            Feedback,
            ["add_feedback"],
        )

    def test_list_not_authenticated(self):
        self.assert_401(self.do_list())

    def test_detail_not_authenticated(self):
        self.assert_401(self.detail(1))

    def test_list_authenticated(self):
        self.assert_200(self.authenticated_list("regular_user"))

    def test_create_not_authenticated(self):
        self.assert_401(self.create(self.template))

    def test_create_regular_user(self):
        self.assert_201(self.authenticated_create("regular_user", self.template))

    def test_create_admin_user(self):
        self.assert_201(self.authenticated_create("admin_user", self.template))

    def test_update_admin_user(self):
        created = self.assert_201(
            self.authenticated_create("admin_user", self.template)
        )

        for key, value in self.update_template.items():
            created[key] = value

        updated = self.assert_200(self.authenticated_update("admin_user", 1, created))

        for key, value in self.update_template.items():
            self.assertEqual(updated[key], value)
