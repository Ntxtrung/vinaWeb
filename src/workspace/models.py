from datetime import timedelta

from artists.models import User
from django.db import models
from shots.models import Shot

STATUS_CHOICES = [
    ("#0", "working"),
    ("#1", "done"),
    ("#2", "help"),
    ("#3", "feedback"),
    ("#4", "hold"),
    ("#5", "cancelled"),
]


class Workspace(models.Model):
    shot = models.ForeignKey(Shot, on_delete=models.CASCADE)
    artist = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    work_start_date = models.DateTimeField(null=True, blank=True)
    work_end_date = models.DateTimeField(null=True, blank=True)
    working_time = models.DurationField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shot.shot_id} worked by {self.artist.username}"

    def save(self, *args, **kwargs):
        if self.work_start_date and self.work_end_date:
            self.working_time = self.work_end_date - self.work_start_date
        super().save(*args, **kwargs)
