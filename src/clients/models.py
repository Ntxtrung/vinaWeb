import uuid

from django.db import models


# Create your models here.
class Area(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Job(models.Model):
    name_job = models.CharField(max_length=50, unique=True, default="")

    def __str__(self):
        return self.name_job


class JobRate(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_rates")
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="job_rates")
    cost_per_md = models.DecimalField(max_digits=10, decimal_places=2)  # Giá cho mỗi MD

    class Meta:
        unique_together = (
            "job",
            "area",
        )  # Đảm bảo mỗi công việc và khu vực chỉ có một giá

    def __str__(self):
        return f"{self.job.name_job} in Area: {self.area.name} - Cost per MD: {self.cost_per_md}"


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    area = models.ForeignKey(
        Area, on_delete=models.SET_NULL, null=True, related_name="clients"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} from {self.area.name if self.area else 'Unknown'}"
