from django.urls import path
from .views import (
    VacationListCreateView,
    VacationDetailView,
    VacationAbsenceListView,
    RegistrarFaltaView,
)

urlpatterns = [
    path("",          VacationListCreateView.as_view(), name="vacation-list"),
    path("<int:pk>/", VacationDetailView.as_view(),     name="vacation-detail"),
    path("absences/", VacationAbsenceListView.as_view(),name="vacation-absences"),
    path("falta/",    RegistrarFaltaView.as_view(),     name="vacation-falta"),
]