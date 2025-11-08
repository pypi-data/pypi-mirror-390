from django.db import models

from django_countries.fields import CountryField

from .utils import TimesStampMixin

from .member import Member


class Address(TimesStampMixin):

    line1 = models.CharField(max_length=200)
    line2 = models.CharField(max_length=200, null=True)
    line3 = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    region = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200, null=True)
    country = CountryField()

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.line1}, {self.region}, {self.country}"

    @property
    def country_name(self):
        return self.country.name

    @property
    def country_flag(self):
        return self.country.flag


class Organization(TimesStampMixin):

    name = models.CharField(max_length=200)
    acronym = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    website = models.CharField(max_length=250, blank=True, null=True)
    members = models.ManyToManyField(Member, blank=True, related_name="organizations")

    def __str__(self):
        return self.name

    @property
    def is_facility(self):
        return hasattr(self, "facility")
