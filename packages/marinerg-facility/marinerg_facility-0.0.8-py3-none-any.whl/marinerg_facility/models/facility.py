import functools

from django.db import models

from ichec_django_core.models import Organization
from ichec_django_core.models.utils import generate_thumbnail, content_file_name


class Facility(Organization):

    is_active = models.BooleanField(default=True)
    is_partner = models.BooleanField(default=False)
    image = models.ImageField(
        null=True, upload_to=functools.partial(content_file_name, "image")
    )
    thumbnail = models.ImageField(null=True)

    class Meta:
        verbose_name = "Facility"
        verbose_name_plural = "Facilities"

    def save(self, *args, **kwargs):
        if not self.image:
            self.thumbnail = None
        else:
            try:
                self.thumbnail.name = generate_thumbnail(self, "image", self.image)
            except:  # NOQA
                self.thumbnail = None
        super().save(*args, **kwargs)
