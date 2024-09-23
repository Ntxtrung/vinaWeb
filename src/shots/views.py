from django.db import transaction
from django.forms import formset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render

from .forms import PackageForm, ShotFormSet
from .models import Package, Shot

# Create your views here.


def change_theme(request):
    if "is_darkMode" in request.session:
        request.session["is_darkMode"] = not request.session["is_darkMode"]
    else:
        request.session["is_darkMode"] = True
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


def shot_list(request):
    shots = Shot.objects.all()
    return render(request, "shots/shot_list.html", {"shots": shots})


def shot_create(request):
    if request.method == "POST":
        form = ShotForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("shot_list")
    else:
        form = ShotForm()
    return render(request, "shots/shot_form.html", {"form": form})


def package_create(request):
    if request.method == "POST":
        package_form = PackageForm(request.POST)
        shot_formset = ShotFormSet(request.POST, request.FILES)

        if package_form.is_valid() and shot_formset.is_valid():
            try:
                with transaction.atomic():
                    package = package_form.save()
                    instances = shot_formset.save(commit=False)
                    for instance in instances:
                        if instance.name:  # Chỉ lưu các shot có tên
                            instance.package = package
                            instance.save()

                    # Cập nhật ngày giao của package
                    package.update_package_delivery_dates()

                return redirect("package_list")
            except Exception as e:
                print(e)
    else:
        package_form = PackageForm()
        shot_formset = ShotFormSet(queryset=Shot.objects.none())

    return render(
        request,
        "shots/package_form.html",
        {"package_form": package_form, "shot_formset": shot_formset},
    )


def package_list(request):
    packages = Package.objects.all()
    return render(request, "shots/package_list.html", {"packages": packages})


def update_shot_delivery_date(request, shot_id):
    if request.method == "POST":
        try:
            shot = Shot.objects.get(id=shot_id)
            delivery_date = request.POST.get("delivery_date")
            if delivery_date:
                shot.delivery_date = delivery_date
                shot.save()
                package = shot.package
                return JsonResponse(
                    {
                        "earliest_delivery": package.earliest_delivery,
                        "latest_delivery": package.latest_delivery,
                    }
                )
        except Shot.DoesNotExist:
            return JsonResponse({"error": "Shot not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)
