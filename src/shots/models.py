from django.db import models
from django.utils.text import slugify

from clients.models import Client, Job

# Create your models here.


class Project(models.Model):
    project_name = models.CharField(max_length=200)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_name


class Package(models.Model):
    package_name = models.CharField(max_length=200, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.package_name} - {self.created_at}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.package_name)
        super().save(*args, **kwargs)


class Shot(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True)
    shot_id = models.CharField(max_length=36, blank=True)
    shot_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.shot_name} - {self.package.package_name} - {self.package.project.project_name}"
