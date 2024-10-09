import datetime
import uuid

from clients.models import Client, Job
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from shots.choice import STATUS_CHOICES

# Create your models here.


class ItemsBase(models.Model):
    class Meta:
        abstract = True

    # name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)


class Project(ItemsBase):
    project_name = models.CharField(max_length=200, default="")
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="projects"
    )

    def __str__(self):
        return str(self.project_name)


class Package(ItemsBase):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="packages"
    )
    slug = models.SlugField(blank=True)
    package_name = models.CharField(max_length=255, default="")

    @property
    def all_shots(self):
        return self.shot_set.all()

    def get_absolute_url(self):
        return reverse("shots:detail_package", kwargs={"slug": self.slug})

    def __str__(self):
        return str(self.package_name)

    def save(self, *args, **kwargs):
        # Tạo slug nếu chưa có
        if not self.slug and self.package_name:
            base_slug = slugify(self.package_name)
            slug = base_slug
            counter = 1

            # Tạo slug duy nhất
            while Package.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        # Lưu Package lần đầu tiên
        super().save(*args, **kwargs)


def get_annotation_upload_path(instance, filename):
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    return f"annotations/{year}/{month}/{instance.package.slug}/{filename}"


class Shot(ItemsBase):
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="shots",
    )
    shot_name = models.CharField(max_length=200, default="")
    md = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    shot_id = models.CharField(max_length=24, unique=True, editable=False)
    word_ref = models.TextField(blank=True)
    annotations = models.ImageField(
        upload_to=get_annotation_upload_path,
        blank=True,
        null=True,
        max_length=255,
    )
    delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="#0")

    def __str__(self):
        return f"{self.shot_name} - {self.package.package_name} - {self.package.project.project_name}"

    def save(self, *args, **kwargs):
        if not self.shot_id:
            self.shot_id = str(uuid.uuid4()).replace("-", "")[:24].lower()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["id"]  # hoặc bất kỳ trường nào bạn muốn sử dụng để sắp xếp
