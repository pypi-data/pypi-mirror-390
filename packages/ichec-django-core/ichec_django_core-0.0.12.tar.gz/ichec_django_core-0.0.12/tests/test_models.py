from django.test import TestCase

from ichec_django_core.models import Organization, Address


class OrganizationTestCase(TestCase):
    def setUp(self):

        address = Address.objects.create(line1="1234 Street", region="My Region")
        Organization.objects.create(name="my_org", address=address)

    def test_query_model(self):
        org = Organization.objects.get(name="my_org")
        self.assertEqual(org.name, "my_org")
