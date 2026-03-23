from django.urls import path
from .views import (
    LateArrivalListView,
    RegisterLateArrivalView,
    AttendanceSummaryView,
)

urlpatterns = [
    path("",          LateArrivalListView.as_view(),    name="attendance-list"),
    path("register/", RegisterLateArrivalView.as_view(),name="attendance-register"),
    path("summary/",  AttendanceSummaryView.as_view(),  name="attendance-summary"),
]