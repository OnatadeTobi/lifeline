from django.urls import path
from .views import StateListView, LocalGovernmentListView

urlpatterns = [
    path('states/', StateListView.as_view(), name='state_list'),
    path('states/<int:state_id>/lgas/', LocalGovernmentListView.as_view(), name='lga_list'),
    path('lgas/', LocalGovernmentListView.as_view(), name='lga_list_all'),
]