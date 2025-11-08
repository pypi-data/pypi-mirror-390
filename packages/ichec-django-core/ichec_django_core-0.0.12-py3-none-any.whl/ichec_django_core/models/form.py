from django.db import models

import functools

from .utils import TimesStampMixin, content_file_name


class FormFieldType(models.TextChoices):

    BOOLEAN = "BOOLEAN", "Boolean"
    CHAR = "CHAR", "Short Text"
    TEXT = "TEXT", "Long Text"
    RICH_TEXT = "RICH_TEXT", "Rich Text"
    SELECTION = "SELECTION", "Selection"
    INTEGER = "INTEGER", "Integer"
    FILE = "FILE", "File"


class Form(TimesStampMixin):

    class Meta:
        verbose_name = "Form"
        verbose_name_plural = "Forms"


class FormGroup(models.Model):

    class Meta:
        verbose_name = "Form Group"
        verbose_name_plural = "Form Groups"

    label = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True)
    order = models.IntegerField(default=0)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="groups")

    def __str__(self):
        return self.label if self.label else f"Form Group {self.id}"


class FormField(models.Model):

    class Meta:
        verbose_name = "Form Field"
        verbose_name_plural = "Form Fields"

    label = models.CharField(max_length=200)
    key = models.CharField(max_length=200)
    required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    field_type = models.CharField(
        max_length=10,
        choices=FormFieldType.choices,
        default=FormFieldType.CHAR,
    )

    description = models.TextField(blank=True)

    template = models.FileField(
        null=True,
        upload_to=functools.partial(content_file_name, "form_field_template"),
    )

    default = models.CharField(max_length=500, blank=True)
    options = models.CharField(max_length=200, null=True)

    group = models.ForeignKey(
        FormGroup, on_delete=models.CASCADE, related_name="fields"
    )

    def __str__(self):
        return self.label


class PopulatedForm(TimesStampMixin):

    class Meta:
        verbose_name = "Populated Form"
        verbose_name_plural = "Populated Forms"


class FormFieldValue(models.Model):

    class Meta:
        verbose_name = "Form Field Value"
        verbose_name_plural = "Form Field Values"

    value = models.CharField(max_length=500)
    asset = models.FileField(
        null=True,
        upload_to=functools.partial(content_file_name, "form_field_value"),
    )
    field = models.ForeignKey(
        FormField, on_delete=models.CASCADE, related_name="values"
    )
    form = models.ForeignKey(
        PopulatedForm, on_delete=models.CASCADE, related_name="values"
    )

    def __str__(self):
        return self.value
