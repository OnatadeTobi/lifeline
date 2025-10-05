from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import State, LocalGovernment


@admin.register(State)
class StateAdmin(ModelAdmin):
    list_display = ["name", "code"]
    search_fields = ["name", "code"]
    ordering = ["name"]


@admin.register(LocalGovernment)
class LocalGovernmentAdmin(ModelAdmin):
    list_display = ["name", "state"]
    list_filter = ["state"]
    search_fields = ["name", "state__name"]
    ordering = ["state", "name"]




# from django.contrib import admin
# from .models import State, LocalGovernment

# # Register your models here.
# admin.site.register(State)
# admin.site.register(LocalGovernment)