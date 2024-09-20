from django.urls import path

from . import views

urlpatterns = [
    path("", views.package_list, name="package_list"),
    path("create/", views.package_create, name="package_create"),
    path(
        "update_shot_delivery_date/<int:shot_id>/",
        views.update_shot_delivery_date,
        name="update_shot_delivery_date",
    ),
]
