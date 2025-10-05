from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ["email", "role", "is_verified", "is_active"]
    search_fields = ["email", "role"]

# from django.contrib import admin
# from .models import User

# # Register your models here.
# admin.site.register(User)