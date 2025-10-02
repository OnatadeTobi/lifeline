from django.contrib import admin
from .models import State, LocalGovernment

# Register your models here.
admin.site.register(State)
admin.site.register(LocalGovernment)