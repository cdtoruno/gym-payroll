from rest_framework import generics, filters, status
from rest_framework.response import Response

from .models import Employee
from .serializers import EmployeeSerializer


class EmployeeListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/employees/  — lista empleados (?search= ?active=true/false)
    POST /api/employees/  — crea un empleado
    """
    serializer_class = EmployeeSerializer
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ["name", "position", "phone"]
    ordering_fields  = ["name", "hire_date", "salary_base"]
    ordering         = ["name"]

    def get_queryset(self):
        qs     = Employee.objects.all()
        active = self.request.query_params.get("active")
        if active == "true":
            qs = qs.filter(active=True)
        elif active == "false":
            qs = qs.filter(active=False)
        return qs


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/employees/{id}/  — detalle
    PUT    /api/employees/{id}/  — actualización completa
    PATCH  /api/employees/{id}/  — actualización parcial
    DELETE /api/employees/{id}/  — soft delete (marca inactivo)
    """
    queryset         = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def destroy(self, request, *args, **kwargs):
        employee        = self.get_object()
        employee.active = False
        employee.save(update_fields=["active", "updated_at"])
        return Response(
            {"detail": f"Empleado '{employee.name}' desactivado correctamente."},
            status=status.HTTP_200_OK,
        )