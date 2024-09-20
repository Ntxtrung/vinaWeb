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
        return self.project_name


class Package(ItemsBase):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return f"{self.package_name} - {self.created_at}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Shot(ItemsBase):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True)
    shot_id = models.CharField(max_length=36, blank=True)

    word_ref = models.TextField(blank=True)
    annotations = models.ImageField(upload_to="annotations/{name}", blank=True)

    def __str__(self):
        return f"{self.shot_name} - {self.package.name} - {self.package.project.name}"
