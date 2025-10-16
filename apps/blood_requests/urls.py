from django.urls import path
from .views import (
    BloodRequestCreateView,
    BloodRequestListView,
    BloodRequestDetailView,
    DonorResponseListView,
    AcceptRequestView,
    #accept_request,
    mark_fulfilled,
    confirm_donation,
)

urlpatterns = [
    path('create/', BloodRequestCreateView.as_view(), name='request_create'),
    path('', BloodRequestListView.as_view(), name='request_list'),
    path('<int:pk>/', BloodRequestDetailView.as_view(), name='request_detail'),
    path('<int:request_id>/accept/', AcceptRequestView.as_view(), name='accept_request'),
    path('<int:request_id>/fulfill/', mark_fulfilled, name='mark_fulfilled'),
    path('<int:request_id>/responses/', DonorResponseListView.as_view(), name='donor_responses'),

    path('<int:request_id>/confirm/<int:response_id>/', confirm_donation, name='confirm_donation'),
]