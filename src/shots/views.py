import calendar

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, FormView, ListView, View
from django.views.generic.edit import FormMixin

from .forms import PackageForm, ProjectForm, ShotForm, ShotFormSet
from .models import Client, Package, Project, Shot


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
    paginate_by = 9
    form_class = ShotForm

    def get_queryset(self):
        self.package = get_object_or_404(Package, slug=self.kwargs.get("slug"))
        return Shot.objects.filter(package=self.package).order_by(
            "id"
        )  # Thêm .order_by() ở đây

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Truy xuất tất cả các Shot liên quan đến Package

        context.update(
            {
                "package": self.package,
                "shot_count": self.object_list.count(),
                "form": self.get_form(),
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object_list = self.get_queryset()
        form = self.get_form()

        if "delete" in request.POST:
            shot_id = request.POST.get("shot_id")
            shot = get_object_or_404(Shot, id=shot_id, package=self.package)
            shot.delete()
            messages.success(request, "Shot deleted successfully.")
            return self.get(request, *args, **kwargs)

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        shot = form.save(commit=False)
        shot.package = self.package
        shot.save()
        messages.success(self.request, "Shot updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("shots:main", kwargs={"slug": self.package.slug})


class PackageCreateView(View):
    template_name = "shots/package_form.html"

    def get(self, request, *args, **kwargs):
        package_form = PackageForm()
        shot_formset = ShotFormSet(queryset=Shot.objects.none())
        project_form = ProjectForm()
        clients = Client.objects.all()

        return render(
            request,
            self.template_name,
            {
                "package_form": package_form,
                "shot_formset": shot_formset,
                "project_form": project_form,
                "clients": clients,
            },
        )

    def post(self, request, *args, **kwargs):
        package_form = PackageForm(request.POST)
        shot_formset = ShotFormSet(request.POST)
        project_form = ProjectForm(request.POST)

        if (
            project_form.is_valid()
            and package_form.is_valid()
            and shot_formset.is_valid()
        ):
            try:
                with transaction.atomic():
                    project_name = project_form.cleaned_data["project_name"]
                    client = project_form.cleaned_data["client"]

                    project, created = Project.objects.get_or_create(
                        project_name=project_name, client=client
                    )

                    package = package_form.save(commit=False)
                    package.project = project
                    package.save()

                    shots = shot_formset.save(commit=False)
                    for shot in shots:
                        shot.package = package
                        shot.save()

                messages.success(request, "Package và các shot đã được tạo thành công.")
                return redirect(
                    reverse("shots:detail_package", kwargs={"slug": package.slug})
                )
            except Exception as e:
                messages.error(request, f"Có lỗi xảy ra: {e}")

        messages.error(request, "Có lỗi xảy ra khi nộp form.")
        return render(
            request,
            "shots/detail_package.html",
            {
                "package_form": package_form,
                "shot_formset": shot_formset,
                "project_form": project_form,
                "clients": Client.objects.all(),
            },
        )


# class PackageCreateView(View):
#     template_name = "shots/package_form.html"

#     def get(self, request, *args, **kwargs):
#         package_form = PackageForm()
#         shot_formset = ShotFormSet(queryset=Shot.objects.none())
#         project_form = ProjectForm()
#         clients = Client.objects.all()

#         return render(
#             request,
#             self.template_name,
#             {
#                 "package_form": package_form,
#                 "shot_formset": shot_formset,
#                 "project_form": project_form,
#                 "clients": clients,
#             },
#         )

#     def post(self, request, *args, **kwargs):
#         package_form = PackageForm(request.POST)
#         shot_formset = ShotFormSet(request.POST)
#         project_form = ProjectForm(request.POST)

#         # Manually differentiate the project and package name fields
#         project_name = request.POST.getlist("name")[
#             0
#         ]  # Project name is the first 'name'
#         package_name = request.POST.getlist("name")[
#             1
#         ]  # Package name is the second 'name'

#         # Modify the data for the forms
#         request.POST = request.POST.copy()
#         request.POST["project_name"] = project_name
#         request.POST["package_name"] = package_name

#         # Now use the modified data in the forms
#         project_form = ProjectForm(request.POST)
#         package_form = PackageForm(request.POST)

#         # Proceed with the rest of the logic
#         if (
#             project_form.is_valid()
#             and package_form.is_valid()
#             and shot_formset.is_valid()
#         ):
#             # Get or create the project
#             client = project_form.cleaned_data["client"]
#             project, created = Project.objects.get_or_create(
#                 name=project_name, client=client
#             )

#             if created:
#                 messages.success(
#                     request, f"Project '{project_name}' created successfully."
#                 )
#             else:
#                 messages.info(request, f"Project '{project_name}' already exists.")

#             # Create the package and save the shots
#             package = package_form.save(commit=False)
#             package.project = project
#             package.save()

#             shots = shot_formset.save(commit=False)
#             for shot in shots:
#                 shot.package = package
#                 shot.save()

#             messages.success(request, "Package and shots created successfully.")
#             return redirect(
#                 reverse("shots:detail_package", kwargs={"slug": package.slug})
#             )
#         else:
#             messages.error(request, "There were errors with the form submission.")

#         return render(
#             request,
#             "shots/detail_package.html",
#             {
#                 "package_form": package_form,
#                 "shot_formset": shot_formset,
#                 "project_form": project_form,
#                 "clients": Client.objects.all(),
#             },
#         )


# @csrf_exempt
# def create_project_ajax(request):
#     if request.method == "POST":
#         form = ProjectForm(request.POST)
#         print("Received POST data:", request.POST)  # Add this line
#         if form.is_valid():
#             project = form.save()
#             print("Project created:", project)  # Add this line
#             return JsonResponse(
#                 {
#                     "success": True,
#                     "project_id": project.id,
#                     "project_name": project.name,
#                     "project_client": project.client.name,
#                 }
#             )
#         else:
#             print("Form errors:", form.errors)  # Add this line
#             return JsonResponse({"success": False, "errors": form.errors})
#     return JsonResponse({"success": False, "message": "Invalid request method"})
