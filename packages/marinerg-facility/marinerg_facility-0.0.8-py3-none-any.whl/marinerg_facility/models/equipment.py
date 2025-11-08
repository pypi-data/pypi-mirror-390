import functools

from django.db import models

from ichec_django_core.models.utils import (
    generate_thumbnail,
    content_file_name,
    TimesStampMixin,
)

from .facility import Facility


class Equipment(TimesStampMixin):

    name = models.CharField(max_length=100)
    description = models.CharField()
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name="equipment"
    )

    image = models.ImageField(
        null=True, upload_to=functools.partial(content_file_name, "image")
    )
    thumbnail = models.ImageField(null=True)

    def save(self, *args, **kwargs):
        if not self.image:
            self.thumbnail = None
        else:
            self.thumbnail.name = generate_thumbnail(self, "image", self.image)
        super().save(*args, **kwargs)
