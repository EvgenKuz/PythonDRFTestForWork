import uuid

from django.core.validators import FileExtensionValidator
from django.db import models


class Video(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, verbose_name="Video's id"
    )
    video = models.FileField(
        upload_to="videos/",
        null=True,
        validators=(FileExtensionValidator(allowed_extensions=("mp4",)),),
        verbose_name="Video's location",
    )
    name = models.CharField(
        max_length=255, null=False, verbose_name="Video's original name"
    )
