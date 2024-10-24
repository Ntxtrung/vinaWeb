import calendar

from django.contrib import messages
from django.core.cache import cache
from django.db import transaction
from django.db.models import Case, Count, IntegerField, Sum, When
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, FormView, ListView, View
from django.views.generic.edit import FormMixin
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from clients.forms import ClientForm
from clients.models import Client

from .choice import STATUS_CHOICES
from .forms import PackageForm, ProjectForm, ShotForm, ShotFormSet
from .models import Package, Project, Shot


def change_theme(request):
    request.session["is_darkMode"] = not request.session.get("is_darkMode", False)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class PackageListView(FormView, ListView):
    model = Package
    template_name = "shots/main.html"
    context_object_name = "packages"
    form_class = PackageForm
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        selected_month = self.kwargs.get("selected_month") or timezone.now().strftime(
            "%m"
        )
        selected_year = self.kwargs.get("selected_year") or timezone.now().strftime(
            "%Y"
        )

        queryset = queryset.filter(created_at__year=selected_year)
        if selected_month != "00":
            queryset = queryset.filter(created_at__month=selected_month)
        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = timezone.now()
        packages = context["packages"]

        # Tính toán ngày giao hàng sớm nhất và muộn nhất cho từng Package
        for package in packages:
            shots = package.shots.all()
            delivery_dates = [
                shot.delivery_date for shot in shots if shot.delivery_date
            ]
            package.earliest_delivery = min(delivery_dates) if delivery_dates else None
            package.latest_delivery = max(delivery_dates) if delivery_dates else None

        # Thêm tháng và năm đã chọn vào context
        context.update(
            {
                "selected_month": self.kwargs.get("selected_month")
                or current_date.strftime("%m"),
                "selected_year": self.kwargs.get("selected_year")
                or current_date.strftime("%Y"),
                "months": [("00", "All Months")]
                + [(f"{i:02d}", calendar.month_name[i]) for i in range(1, 13)],
                "years": [
                    str(year)
                    for year in range(current_date.year - 2, current_date.year + 1)
                ],
            }
        )
        return context

    def form_valid(self, form):
        instance = form.save()
        messages.info(self.request, f"Package: {instance.name} has been created")
        return HttpResponseRedirect(
            reverse_lazy("shots:detail_package", kwargs={"slug": instance.slug})
        )

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class PackageDetailView(FormMixin, ListView):
    model = Shot
    template_name = "shots/detail_package.html"

    form_class = ShotForm

    def get_queryset(self):
        self.package = get_object_or_404(Package, slug=self.kwargs.get("slug"))
        return Shot.objects.filter(package=self.package).order_by("id")

    def get_package_summary(self):
        cache_key = f"package_summary_{self.package.id}"
        summary = cache.get(cache_key)

        if summary is None:
            summary = self.get_queryset().aggregate(
                total_shots=Count("id"),
                total_roto=Sum("md_roto"),
                total_paint=Sum("md_paint"),
                total_track=Sum("md_track"),
                total_comp=Sum("md_comp"),
                roto_shots=Count(
                    Case(When(md_roto__gt=0, then=1), output_field=IntegerField())
                ),
                paint_shots=Count(
                    Case(When(md_paint__gt=0, then=1), output_field=IntegerField())
                ),
                track_shots=Count(
                    Case(When(md_track__gt=0, then=1), output_field=IntegerField())
                ),
                comp_shots=Count(
                    Case(When(md_comp__gt=0, then=1), output_field=IntegerField())
                ),
            )
            cache.set(cache_key, summary, 3600)  # Cache for 1 hour

        return {k: v for k, v in summary.items() if v is not None and v > 0}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summary = self.get_package_summary()
        context.update(
            {
                "package": self.package,
                "shot_count": summary.get("total_shots", 0),
                "summary": summary,
                "shot_statuses": STATUS_CHOICES,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object_list = self.get_queryset()

        if "delete" in request.POST:
            shot_id = request.POST.get("delete")
            shot = get_object_or_404(Shot, id=shot_id, package=self.package)
            shot.delete()
            messages.success(request, "Shot deleted successfully.")
        else:
            with transaction.atomic():
                for key, value in request.POST.items():
                    if "-" in key:
                        shot_id, field = key.rsplit("-", 1)
                        shot = get_object_or_404(Shot, id=shot_id, package=self.package)
                        if field == "delivery_date":
                            setattr(shot, field, parse_date(value) if value else None)
                        elif field in ["md_roto", "md_paint", "md_track", "md_comp"]:
                            setattr(shot, field, float(value) if value else None)
                        else:
                            setattr(shot, field, value)
                        shot.save()
            messages.success(request, "Changes saved successfully.")

        self.invalidate_cache()
        return self.get(request, *args, **kwargs)

    def invalidate_cache(self):
        cache.delete(f"package_summary_{self.package.id}")


class PackageCreateView(View):
    template_name = "shots/package_form.html"

    def get(self, request, *args, **kwargs):
        shot_formset = ShotFormSet(queryset=Shot.objects.none())
        project_form = ProjectForm()
        clients = Client.objects.all()
        client_form = ClientForm()

        # Lấy client_id từ URL hoặc request
        client_id = self.kwargs.get("client_id")
        package_form = PackageForm(client_id=client_id)

        if client_id:
            # Nếu client_id được cung cấp, lấy các project liên quan
            project_form.fields["client"].queryset = Project.objects.filter(
                client_id=client_id
            )
        else:
            # Nếu không có client_id, đặt queryset trống
            project_form.fields["client"].queryset = Project.objects.none()

        return render(
            request,
            self.template_name,
            {
                "package_form": package_form,
                "shot_formset": shot_formset,
                "project_form": project_form,
                "clients": clients,
                "client_form": client_form,
            },
        )

    def post(self, request, *args, **kwargs):
        client_id = request.POST.get("client")
        package_form = PackageForm(request.POST, client_id=client_id)
        shot_formset = ShotFormSet(request.POST)

        project_data = request.POST.copy()
        project_form = ProjectForm(project_data)
        client_form = ClientForm(request.POST)

        print("POST data:", request.POST)  # Kiểm tra dữ liệu POST

        if not project_form.is_valid():
            print("Project form errors:", project_form.errors)

        if not package_form.is_valid():
            print("Package form errors:", package_form.errors)

        if not shot_formset.is_valid():
            print("Shot formset errors:", shot_formset.errors)

        if "create_client" in request.POST:
            if client_form.is_valid():
                new_client = client_form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "client_id": new_client.id,
                        "client_name": new_client.name,
                    }
                )
            print("Client Form Errors:", client_form.errors)
            return JsonResponse({"success": False, "errors": client_form.errors})

        # Kiểm tra tính hợp lệ của tất cả các form

        if (
            project_form.is_valid()
            and package_form.is_valid()
            and shot_formset.is_valid()
        ):
            try:
                with transaction.atomic():

                    # Nếu đã chọn project có sẵn
                    if project_data.get("project"):
                        try:
                            project = Project.objects.get(id=project_data["project"])
                        except Project.DoesNotExist:
                            messages.error(request, "Dự án được chọn không tồn tại.")
                            return redirect(request.path)
                    else:
                        project_name = (
                            project_data.get("project_name", "").strip() or "Unknown"
                        )
                        project = Project.objects.create(
                            project_name=project_name, client_id=client_id
                        )

                    # Lưu Package và liên kết với Project
                    package = package_form.save(commit=False)
                    package.project = project
                    package.save()

                    # Lưu tất cả các Shot liên quan
                    shots = shot_formset.save(commit=False)
                    for shot in shots:
                        shot.package = package
                        # shot.area = project.client.area
                        shot.save()

                messages.success(request, "Package và các shot đã được tạo thành công.")
                return redirect(
                    reverse("shots:detail_package", kwargs={"slug": package.slug})
                )
            except Exception as e:
                messages.error(request, f"Có lỗi xảy ra: {e}")
        else:
            print("Package form errors:", package_form.errors)
            print("Shot formset errors:", shot_formset.errors)
            for i, form in enumerate(shot_formset):
                print(f"Shot form {i} errors:", form.errors)

        messages.error(request, "Có lỗi xảy ra khi nộp form.")
        return render(
            request,
            # "shots/detail_package.html",
            "shots/package_form.html",
            {
                "package_form": package_form,
                "shot_formset": shot_formset,
                "project_form": project_form,
                "clients": Client.objects.all(),
            },
        )


class UpdateAllShotsView(View):
    def post(self, request, package_id):
        package = Package.objects.get(id=package_id)
        all_delivery_date = request.POST.get("all_delivery_date")
        all_status = request.POST.get("all_status")

        shots = Shot.objects.filter(package=package)
        updated_count = 0

        for shot in shots:
            updated = False
            if all_delivery_date:
                shot.delivery_date = all_delivery_date
                updated = True
            if all_status:
                shot.status = all_status
                updated = True
            if updated:
                shot.save()
                updated_count += 1

        if updated_count > 0:
            messages.success(request, f"Successfully updated {updated_count} shots.")
        else:
            messages.info(request, "No shots were updated.")

        return redirect("package_detail", pk=package_id)


def get_projects(request):
    client_id = request.GET.get("client_id")
    projects = Project.objects.filter(client_id=client_id).values("id", "project_name")
    return JsonResponse(list(projects), safe=False)


def create_client(request):
    """API để tạo mới một Client."""
    if request.method == "POST":
        client_form = ClientForm(request.POST)
        if client_form.is_valid():
            new_client = client_form.save()
            return JsonResponse(
                {
                    "success": True,
                    "client_id": new_client.id,
                    "client_name": new_client.name,
                }
            )
        return JsonResponse({"success": False, "errors": client_form.errors})
    return JsonResponse({"success": False, "message": "Invalid request method"})


def create_project(request):
    """API để tạo mới một Project."""
    if request.method == "POST":
        project_form = ProjectForm(request.POST)
        if project_form.is_valid():
            new_project = project_form.save()
            return JsonResponse(
                {
                    "success": True,
                    "project_id": new_project.id,
                    "project_name": new_project.project_name,
                }
            )
        return JsonResponse({"success": False, "errors": project_form.errors})
    return JsonResponse({"success": False, "message": "Invalid request method"})
