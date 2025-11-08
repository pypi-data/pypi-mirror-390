from pathlib import Path
import shutil
import os
import uuid

from PIL import Image

from django.db import models
from django.utils import timezone
from django.conf import settings


class TimesStampMixin(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


def make_zip(work_path: Path, output_path: Path):
    shutil.make_archive(str(output_path), "zip", str(work_path))


def generate_thumbnail(
    model: models.Model, field_name: str, field: models.ImageField, size=(128, 128)
) -> str:

    media_root = Path(settings.MEDIA_ROOT)
    storage_dir = Path(f"{model._meta.model_name}/{field_name}/thumbnails")
    print(media_root / storage_dir)
    os.makedirs(media_root / storage_dir, exist_ok=True)

    image = Image.open(field)
    image.thumbnail(size)
    file_path = storage_dir / f"{uuid.uuid4()}.png"
    image.save(media_root / file_path, "PNG")
    print(file_path)
    return str(file_path)


def content_file_name(field: str, instance, filename: str):
    """
    Handler for the Django File upload_to field for user media.
    Store the media in a prefixed directory by model and
    make sure there is a unique filename
    """
    instance.original_file_name = filename
    _, ext = os.path.splitext(filename)

    storage_dir = Path(f"{instance._meta.model_name}/{field}")
    return storage_dir / f"{uuid.uuid4()}{ext}"
