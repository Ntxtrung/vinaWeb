from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("shots/", include("shots.urls", namespace="shots")),
    # Đảm bảo không có dòng nào khác include 'shots.urls' với namespace 'shots'
]
