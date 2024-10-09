from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory

from .models import Client, Package, Project, Shot


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ["package_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "project" in self.fields:
            self.fields["package_name"].required = False


class ShotForm(forms.ModelForm):
    class Meta:
        model = Shot
        fields = ["shot_name", "md", "word_ref", "delivery_date", "status"]
        widgets = {
            "delivery_date": forms.DateInput(attrs={"type": "date"}),
        }


ShotFormSet = modelformset_factory(
    Shot,
    form=ShotForm,
    extra=1,
    can_delete=True,
    max_num=None,  # Cho phép số lượng form không giới hạn
    validate_max=False,  # Không kiểm tra giới hạn tối đa
)


class ProjectForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(), empty_label="Select a client", required=True
    )

    class Meta:
        model = Project
        fields = ["project_name", "client"]
