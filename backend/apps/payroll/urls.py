from django.urls import path
from .views import (
    PayrollListView,
    PayrollDetailView,
    PayrollPreviewView,
    GeneratePayrollBulkView,
    GeneratePayrollView,
    ExportPayrollCSVView,
)

urlpatterns = [
    path("",               PayrollListView.as_view(),        name="payroll-list"),
    path("<int:pk>/",      PayrollDetailView.as_view(),      name="payroll-detail"),
    path("preview/",       PayrollPreviewView.as_view(),     name="payroll-preview"),
    path("generate-bulk/", GeneratePayrollBulkView.as_view(),name="payroll-generate-bulk"),
    path("generate/",      GeneratePayrollView.as_view(),    name="payroll-generate"),
    path("export/",        ExportPayrollCSVView.as_view(),   name="payroll-export"),
]