from django.contrib import admin

from .models import Package, Project, Shot

# Register your models here.

admin.site.register(Project)
admin.site.register(Package)
admin.site.register(Shot)
