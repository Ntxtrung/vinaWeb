import uuid

from django.db import models
from django_countries.fields import CountryField


# Create your models here.
class Area(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Job(models.Model):
    name = models.CharField(max_length=5)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="jobs")

    def __str__(self):
        return f"{self.name} - {self.area.name} - {self.cost}"


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    country = CountryField(blank_label="(Select country)")
    area = models.ForeignKey(
        Area, on_delete=models.SET_NULL, null=True, related_name="clients"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} from {self.area.name if self.area else 'Unknown'}"
