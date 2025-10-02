from django.urls import path
from .views import DonorRegistrationView, DonorProfileView, toggle_availability

urlpatterns = [
    path('register/', DonorRegistrationView.as_view(), name='donor_register'),
    path('profile/', DonorProfileView.as_view(), name='donor_profile'),
    path('toggle-availability/', toggle_availability, name='toggle_availability'),
]