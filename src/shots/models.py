import datetime
import uuid
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from clients.models import Area, Client, Job, JobRate
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
    project_name = models.CharField(max_length=255, blank=True, default="Unknown")
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="projects"
    )

    @classmethod
    def get_default_project(cls):
        default_project, created = cls.objects.get_or_create(
            project_name="Default Project",
            defaults={
                "client": Client.objects.first()
            },  # Đảm bảo có ít nhất một Client
        )
        return default_project.id

    def __str__(self):
        return str(self.project_name)


class Package(ItemsBase):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="packages"
    )
    slug = models.SlugField(blank=True)
    package_name = models.CharField(max_length=255, default="")
    go = models.BooleanField(default=False)
    done = models.BooleanField(default=False)

    @property
    def all_shots(self):
        return self.shots.all()

    @property
    def total_roto_md(self):
        return (
            self.shots.filter(active=True).aggregate(Sum("md_roto"))["md_roto__sum"]
            or 0
        )

    @property
    def total_paint_md(self):
        return (
            self.shots.filter(active=True).aggregate(Sum("md_paint"))["md_paint__sum"]
            or 0
        )

    @property
    def total_track_md(self):
        return (
            self.shots.filter(active=True).aggregate(Sum("md_track"))["md_track__sum"]
            or 0
        )

    @property
    def total_comp_md(self):
        return (
            self.shots.filter(active=True).aggregate(Sum("md_comp"))["md_comp__sum"]
            or 0
        )

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
        super().save(*args, **kwargs)
        # Cập nhật trạng thái của package dựa trên trạng thái của các shot
        self.update_status()
        # Lưu Package lần đầu tiên
        super().save(*args, **kwargs)

    def update_status(self):
        shots = self.shots.all()

        if shots.exists():
            # Định nghĩa các nhóm status
            hold_cancel_statuses = ["#3", "#10"]
            active_statuses = ["#2", "#4", "#5", "#6", "#7", "#8", "#9"]
            bidding_statuses = ["#0", "#1"]  # new, ready

            # Đếm số lượng shots trong mỗi nhóm
            total_shots = shots.count()
            hold_cancel_count = shots.filter(status__in=hold_cancel_statuses).count()
            active_count = shots.filter(status__in=active_statuses).count()
            bidding_count = shots.filter(status__in=bidding_statuses).count()

            if hold_cancel_count == total_shots:
                # Tất cả shots là hold/cancel
                self.active = False
                self.go = False
                self.done = False
            elif active_count > 0:
                # Có ít nhất 1 shot active
                self.active = True
                self.go = True
                self.done = (
                    shots.filter(status="#7").count() == total_shots - hold_cancel_count
                )
            elif bidding_count > 0:
                # Các shots đang ở trạng thái bidding
                self.active = True
                self.go = False
                self.done = False

        Package.objects.filter(id=self.id).update(
            active=self.active, go=self.go, done=self.done
        )

    def calculate_total_cost(self):
        # Lấy tất cả các Shot của Package này và tính tổng chi phí
        shots = self.shots.all()
        total_cost = sum(shot.calculate_total_cost() for shot in shots)
        return total_cost


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
    area = models.ForeignKey(
        Area, on_delete=models.CASCADE, related_name="shots", null=True, blank=True
    )
    shot_name = models.CharField(max_length=200, default="")
    md_roto = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    md_paint = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    md_track = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    md_comp = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
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
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.shot_name} - {self.package.package_name} - {self.package.project.project_name}"

    def save(self, *args, **kwargs):
        if not self.shot_id:
            self.shot_id = str(uuid.uuid4()).replace("-", "")[:24].lower()

        if not self.area and self.package and self.package.project.client.area:
            self.area = self.package.project.client.area

        # Cập nhật trạng thái active của shot dựa trên status
        active_statuses = [
            "#2",
            "#4",
            "#5",
            "#6",
            "#7",
            "#8",
            "#9",
        ]
        # self.active = self.status in active_statuses
        # Tự động cập nhật active dựa trên status
        if self.status in active_statuses:  # hoặc bất kỳ status nào bạn muốn
            self.active = True
        else:
            self.active = False

        super().save(*args, **kwargs)

        # Chỉ cập nhật `Package` nếu `Shot` đã được lưu thành công và `Package` đã có `primary key`
        if self.package_id:
            self.package.update_status()
            self.package.save()

    def calculate_total_cost(self):
        if not self.area:
            return Decimal("0")

        # Cache các giá trị MD để tránh truy cập DB nhiều lần
        md_values = {
            "roto": self.md_roto or 0,
            "paint": self.md_paint or 0,
            "track": self.md_track or 0,
            "comp": self.md_comp or 0,
        }

        # Lấy tất cả JobRate cho area một lần
        job_rates = JobRate.objects.filter(
            area=self.area, job__name_job__in=md_values.keys()
        ).select_related("job")

        # Tạo mapping giữa job và rate
        rates_by_job = {
            rate.job.name_job.lower(): rate.cost_per_md for rate in job_rates
        }

        # Tính tổng chi phí
        total_cost = sum(
            md * rates_by_job.get(job_name, 0)
            for job_name, md in md_values.items()
            if md > 0 and job_name in rates_by_job
        )

        return Decimal(str(total_cost))  # Đảm bảo kết quả là Decimal

    @property
    def total_md(self):
        """Tính tổng số man-day của shot"""
        return sum(
            value or 0
            for value in [self.md_roto, self.md_paint, self.md_track, self.md_comp]
        )

    @property
    def cost_details(self):
        """Trả về chi tiết chi phí cho từng loại công việc"""
        if not self.area:
            return {}

        job_rates = JobRate.objects.filter(area=self.area).select_related("job")

        rates_by_job = {
            rate.job.name_job.lower(): rate.cost_per_md for rate in job_rates
        }

        details = {}
        for job_type, md_value in {
            "roto": self.md_roto,
            "paint": self.md_paint,
            "track": self.md_track,
            "comp": self.md_comp,
        }.items():
            if md_value and md_value > 0:
                rate = rates_by_job.get(job_type, 0)
                details[job_type] = {
                    "md": float(md_value),
                    "rate": float(rate),
                    "cost": float(md_value * rate),
                }

        return details

    class Meta:
        ordering = ["id"]  # hoặc bất kỳ trường nào bạn muốn sử dụng để sắp xếp
