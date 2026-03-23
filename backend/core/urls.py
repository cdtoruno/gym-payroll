from django.urls import path, include

urlpatterns = [
    path("employees/",  include("apps.employees.urls")),
    path("vacations/",  include("apps.vacations.urls")),
    path("payroll/",    include("apps.payroll.urls")),
    path("attendance/", include("apps.attendance.urls")),
]