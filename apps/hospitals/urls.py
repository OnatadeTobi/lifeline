from django.urls import path
from .views import HospitalRegistrationView, HospitalProfileView

urlpatterns = [
    path('register/', HospitalRegistrationView.as_view(), name='hospital_register'),
    path('profile/', HospitalProfileView.as_view(), name='hospital_profile'),
]