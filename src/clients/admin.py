from django.contrib import admin

from .models import Area, Client, Job

# Register your models here.

admin.site.register(Client)
admin.site.register(Area)
admin.site.register(Job)
