import base64
import calendar
import os
import re
from datetime import datetime
from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.db import transaction
from django.db.models import Case, Count, IntegerField, Max, Min, Q, Sum, When
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, FormView, ListView, View
from django.views.generic.edit import FormMixin
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from xhtml2pdf import pisa

from clients.forms import ClientForm
from clients.models import Client

from .choice import STATUS_CHOICES
from .forms import PackageForm, ProjectForm, ShotForm, ShotFormSet
from .models import Area, Package, Project, Shot


def change_theme(request):
    request.session["is_darkMode"] = not request.session.get("is_darkMode", False)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


def summary_data(request):

    current_date = timezone.now()

    selected_month = request.GET.get("month") or current_date.strftime("%Y")
    selected_year = request.GET.get("year") or current_date.strftime("%m")
    selected_status = request.GET.get("status", "go_and_done")

    try:
        studio8fx_area = Area.objects.get(name="Studio8fx")

        # Base query
        base_query = {
            "active": True,
            "package__created_at__year": selected_year,
            "package__go": True,
        }

        # Filter theo status
        if selected_status == "go":
            base_query["package__done"] = False
        elif selected_status == "done":
            base_query["package__done"] = True
            base_query.pop("package__go", None)  # Xóa điều kiện GO nếu chỉ xem DONE
        elif selected_status == "all":
            base_query.pop("package__go", None)

        if selected_month != "00":
            base_query["package__created_at__month"] = selected_month

        # Tính toán MD và trả về JSON
        studio8fx_md = Shot.objects.filter(area=studio8fx_area, **base_query).aggregate(
            roto=Sum("md_roto"),
            paint=Sum("md_paint"),
            track=Sum("md_track"),
            comp=Sum("md_comp"),
        )

        other_md = Shot.objects.filter(~Q(area=studio8fx_area), **base_query).aggregate(
            roto=Sum("md_roto"),
            paint=Sum("md_paint"),
            track=Sum("md_track"),
            comp=Sum("md_comp"),
        )

        # Format số
        for md_dict in [studio8fx_md, other_md]:
            for key in md_dict:
                md_dict[key] = "{:.2f}".format(md_dict[key] or 0)

        return JsonResponse(
            {
                "studio8fx_md": studio8fx_md,
                "other_md": other_md,
                "total_md": {
                    "roto": "{:.2f}".format(
                        float(studio8fx_md["roto"]) + float(other_md["roto"])
                    ),
                    "paint": "{:.2f}".format(
                        float(studio8fx_md["paint"]) + float(other_md["paint"])
                    ),
                    "track": "{:.2f}".format(
                        float(studio8fx_md["track"]) + float(other_md["track"])
                    ),
                    "comp": "{:.2f}".format(
                        float(studio8fx_md["comp"]) + float(other_md["comp"])
                    ),
                },
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


class PackageListView(FormView, ListView):
    model = Package
    template_name = "shots/main.html"
    context_object_name = "packages"
    form_class = PackageForm
    paginate_by = 0

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

        # Lấy shots theo điều kiện thời gian
        selected_year = self.kwargs.get("selected_year") or current_date.strftime("%Y")
        selected_month = self.kwargs.get("selected_month") or current_date.strftime(
            "%m"
        )
        # Lấy ID của area Studio8FX
        studio8fx_area = Area.objects.get(name="Studio8fx")
        # Tính tổng MD cho Studio8FX
        studio8fx_shots = Shot.objects.filter(
            area=studio8fx_area, active=True, package__created_at__year=selected_year
        ).filter(
            Q(package__go=True) | Q(package__done=True)  # Package GO hoặc DONE
        )
        if selected_month != "00":
            studio8fx_shots = studio8fx_shots.filter(
                package__created_at__month=selected_month
            )
        studio8fx_md = studio8fx_shots.aggregate(
            roto=Sum("md_roto"),
            paint=Sum("md_paint"),
            track=Sum("md_track"),
            comp=Sum("md_comp"),
        )

        # Tính tổng MD cho các area khác
        other_shots = Shot.objects.filter(
            ~Q(area=studio8fx_area),
            active=True,
            package__created_at__year=selected_year,
        ).filter(
            Q(package__go=True) | Q(package__done=True)  # Package GO hoặc DONE
        )
        if selected_month != "00":
            other_shots = other_shots.filter(package__created_at__month=selected_month)
        other_md = other_shots.aggregate(
            roto=Sum("md_roto"),
            paint=Sum("md_paint"),
            track=Sum("md_track"),
            comp=Sum("md_comp"),
        )

        # Format số với 2 chữ số thập phân
        context["studio8fx_md"] = {
            "roto": "{:.2f}".format(studio8fx_md["roto"] or 0),
            "paint": "{:.2f}".format(studio8fx_md["paint"] or 0),
            "track": "{:.2f}".format(studio8fx_md["track"] or 0),
            "comp": "{:.2f}".format(studio8fx_md["comp"] or 0),
        }

        context["other_md"] = {
            "roto": "{:.2f}".format(other_md["roto"] or 0),
            "paint": "{:.2f}".format(other_md["paint"] or 0),
            "track": "{:.2f}".format(other_md["track"] or 0),
            "comp": "{:.2f}".format(other_md["comp"] or 0),
        }
        # Tính tổng
        context["total_md"] = {
            "roto": "{:.2f}".format(
                (studio8fx_md["roto"] or 0) + (other_md["roto"] or 0)
            ),
            "paint": "{:.2f}".format(
                (studio8fx_md["paint"] or 0) + (other_md["paint"] or 0)
            ),
            "track": "{:.2f}".format(
                (studio8fx_md["track"] or 0) + (other_md["track"] or 0)
            ),
            "comp": "{:.2f}".format(
                (studio8fx_md["comp"] or 0) + (other_md["comp"] or 0)
            ),
        }

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


class OverviewView(PackageListView):
    template_name = "shots/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Lọc packages GO và BIDDING
        go_packages = context["packages"].filter(go=True, done=False)
        bidding_packages = context["packages"].filter(active=True, go=False)

        # Tính toán MD cho mỗi loại và delivery dates cho mỗi package
        for packages in [go_packages, bidding_packages]:
            for package in packages:
                shots = package.shots.all()
                md_sums = shots.aggregate(
                    total_roto=Sum("md_roto"),
                    total_paint=Sum("md_paint"),
                    total_track=Sum("md_track"),
                    total_comp=Sum("md_comp"),
                )
                package.total_roto = md_sums["total_roto"] or 0
                package.total_paint = md_sums["total_paint"] or 0
                package.total_track = md_sums["total_track"] or 0
                package.total_comp = md_sums["total_comp"] or 0
                package.earliest_delivery = shots.aggregate(Min("delivery_date"))[
                    "delivery_date__min"
                ]
                package.latest_delivery = shots.aggregate(Max("delivery_date"))[
                    "delivery_date__max"
                ]

        context["go_packages"] = go_packages
        context["bidding_packages"] = bidding_packages

        # Bỏ đi context['packages'] nếu không cần thiết trong overview
        context.pop("packages", None)

        return context

    def get_queryset(self):
        # Ghi đè phương thức này nếu bạn muốn thay đổi cách lấy queryset
        return super().get_queryset()

    def form_valid(self, form):
        # Ghi đè phương thức này nếu bạn không muốn xử lý form trong overview
        return self.get(self.request)


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


def calculate_invoice_context(package):
    shots = Shot.objects.filter(package=package)

    total_track = sum(shot.md_track or 0 for shot in shots)
    total_roto = sum(shot.md_roto or 0 for shot in shots)
    total_paint = sum(shot.md_paint or 0 for shot in shots)
    total_comp = sum(shot.md_comp or 0 for shot in shots)
    total_rate = total_track + total_roto + total_paint

    context = {
        "package": package,
        "shots": shots,
        "total_track": total_track,
        "total_roto": total_roto,
        "total_paint": total_paint,
        "total_comp": total_comp,
        "total_rate": total_rate,
        "total_with_vat": float(total_rate) * 1.1,
        "total_days": len(shots),
        "current_date": datetime.now().strftime("%Y.%m.%d"),
        "logo_data_uri": get_logo_data(),
    }

    return context


def prepare_invoice_context(package, shots, is_pdf=False):
    shots_details = []
    total_cost = Decimal("0")

    # Khởi tạo tổng chi phí cho từng loại
    totals = {
        "roto": Decimal("0"),
        "paint": Decimal("0"),
        "track": Decimal("0"),
        "comp": Decimal("0"),
    }

    for shot in shots:
        cost_details = shot.cost_details
        shot_cost = shot.calculate_total_cost()
        total_cost += Decimal(str(shot_cost))

        # Cộng dồn chi phí cho từng loại
        for job_type, detail in cost_details.items():
            if detail and "cost" in detail:
                totals[job_type] += Decimal(str(detail["cost"]))

        shots_details.append(
            {
                "shot": shot,
                "details": cost_details,
                "total_md": shot.total_md,
                "total_cost": shot_cost,
            }
        )

    vat_rate = Decimal("1.1")
    total_with_vat = total_cost * vat_rate

    return {
        "package": package,
        "shots_details": shots_details,
        "total_roto": totals["roto"],
        "total_paint": totals["paint"],
        "total_track": totals["track"],
        "total_comp": totals["comp"],
        "total_cost": total_cost,
        "total_with_vat": total_with_vat,
        "total_days": len(shots),
        "current_date": timezone.now().strftime("%Y.%m.%d"),
        "logo_data_uri": get_logo_data(),
        "is_pdf": is_pdf,
    }


# Tạo một hàm helper để lấy logo data
def get_logo_data():
    logo_path = os.path.join(
        settings.MEDIA_ROOT, "avatars/vinamation/Logo Vinamation2.PNG"
    )
    try:
        with open(logo_path, "rb") as img_file:
            logo_data = base64.b64encode(img_file.read()).decode("utf-8")
            return f"data:image/png;base64,{logo_data}"
    except FileNotFoundError:
        return None


def generate_invoice_pdf(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    shots = Shot.objects.filter(package=package)

    # Sử dụng context mới
    context = prepare_invoice_context(package, shots, is_pdf=True)

    template = get_template("shots/quote_template.html")
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{package.package_name}_invoice.pdf"'
    )

    pdf_options = {
        "page-size": "Letter",
        "margin-top": "1cm",
        "margin-right": "1cm",
        "margin-bottom": "1cm",
        "margin-left": "1cm",
        "encoding": "UTF-8",
        "quiet": True,
        "no-outline": None,
    }

    pisa_status = pisa.CreatePDF(html, dest=response, options=pdf_options)
    if pisa_status.err:
        return HttpResponse(f"PDF generation error: {pisa_status.err}")

    return response
    return redirect(reverse("shots:detail_package", kwargs={"slug": package.slug}))


def preview_invoice(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    shots = Shot.objects.filter(package=package)

    # Sử dụng context mới
    context = prepare_invoice_context(package, shots, is_pdf=False)

    return render(request, "shots/quote_template.html", context)
