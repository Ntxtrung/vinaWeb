import uuid

from clients.models import Client, Job
from django.db import models
from django.utils.text import slugify

# Create your models here.


class ItemsBase(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)


class Project(ItemsBase):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} from {self.client.name}"


class Package(ItemsBase):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="packages"
    )
    slug = models.SlugField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.created_at}"  # Corrected to use self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Shot(ItemsBase):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="shots")
    job = models.ForeignKey(
        Job, on_delete=models.SET_NULL, null=True, blank=True, related_name="shots"
    )
    shot_id = models.CharField(max_length=36, unique=True, editable=False)
    word_ref = models.TextField(blank=True)
    annotations = models.ImageField(upload_to="annotations/", blank=True)

    def __str__(self):
        return f"{self.name} - {self.package.name} - {self.package.project.name}"

    def save(self, *args, **kwargs):
        if not self.shot_id:
            self.shot_id = str(uuid.uuid4())
        super().save(*args, **kwargs)
