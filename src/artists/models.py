from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from shots.models import Shot


def get_avatar_upload_path(instance, filename):
    return f"avatars/{instance.username}/{filename}"


# Create your models here.
class User(AbstractUser):
    avatar = models.ImageField(upload_to=get_avatar_upload_path, null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shots = models.ManyToManyField(Shot, blank=True)
    shots_count = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = slugify(f"{self.first_name} {self.last_name}")
            ex = __class__.objects.filter(username=self.username).exists()
            while ex:
                i = len(
                    __class__.objects.filter(
                        first_name=self.first_name, last_name=self.last_name
                    )
                )
                username = slugify(f"{self.first_name} {self.last_name} {i+1}")

            self.username = username

        self.shots_count = self.shots.count()
        super().save(*args, **kwargs)
