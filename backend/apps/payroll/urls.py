from django.urls import path
from .views import PayrollListView, GeneratePayrollView, ExportPayrollCSVView

urlpatterns = [
    path("",          PayrollListView.as_view(),      name="payroll-list"),
    path("generate/", GeneratePayrollView.as_view(),  name="payroll-generate"),
    path("export/",   ExportPayrollCSVView.as_view(), name="payroll-export"),
]