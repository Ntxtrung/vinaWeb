from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import PackageCreateView  # get_projects_by_client,
from .views import (
    OverviewView,
    PackageDetailView,
    PackageListView,
    UpdateAllShotsView,
    create_client,
    create_project,
    generate_invoice_pdf,
    get_projects,
)

app_name = "shots"

urlpatterns = [
    path("", PackageListView.as_view(), name="main"),
    path(
        "package/create/", PackageCreateView.as_view(), name="create_package"
    ),  # Thêm đường dẫn này
    path("package/<slug>/", PackageDetailView.as_view(), name="detail_package"),
    path(
        "<str:selected_year>/<str:selected_month>/",
        PackageListView.as_view(),
        name="main_year_month",
    ),
    path("projects/", get_projects, name="get_projects_by_client"),
    path("create-client/", create_client, name="create_client"),
    path("create-project/", create_project, name="create_project"),
    path(
        "package/<int:package_id>/invoice/preview/",
        views.preview_invoice,
        name="preview_invoice",
    ),
    path(
        "package/<int:package_id>/invoice/download/",
        views.generate_invoice_pdf,
        name="generate_invoice_pdf",
    ),
    path("summary/", views.summary_data, name="summary_data"),
    path("overview/", views.OverviewView.as_view(), name="overview"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
