from django import forms

from .models import Shot, Package


class ShotForm(forms.ModelForm):
    class Meta:
        model = Shot
        fields = ["name", "word_ref", "delivery_date"]
        widgets = {"delivery_date": forms.DateInput(attrs={"type": "date"})}


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ["name", "project", "earliest_delivery", "latest_delivery"]
        widgets = {
            "earliest_delivery": forms.DateInput(attrs={"type": "date"}),
            "latest_delivery": forms.DateInput(attrs={"type": "date"}),
        }


class ShotFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Shot.objects.none()


ShotFormSet = forms.modelformset_factory(
    Shot,
    form=ShotForm,
    extra=5,  # Tạo 5 form trống
    max_num=5,  # Giới hạn tối đa 5 shots
)
