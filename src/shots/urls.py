from django.urls import path

from .views import PackageCreateView, PackageDetailView, PackageListView

app_name = "shots"

urlpatterns = [
    path("", PackageListView.as_view(), name="main"),
    path(
        "package/create/", PackageCreateView.as_view(), name="create_package"
    ),  # Thêm đường dẫn này
    path("package/<slug>/", PackageDetailView.as_view(), name="detail_package"),
    path("<str:selected_year>/", PackageListView.as_view(), name="main_year"),
    path(
        "<str:selected_year>/<str:selected_month>/",
        PackageListView.as_view(),
        name="main_year_month",
    ),
    # path("create-project/", create_project_ajax, name="create_project_ajax"),
]
