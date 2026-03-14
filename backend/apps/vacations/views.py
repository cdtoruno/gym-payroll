from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.employees.models import Employee
from .models import Vacation
from .serializers import VacationSerializer, RegistrarFaltaSerializer


class VacationListCreateView(generics.ListCreateAPIView):
    queryset         = Vacation.objects.select_related("employee").all()
    serializer_class = VacationSerializer

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get("employee")

        # ── Validar que venga un empleado ─────────────────────────────────────
        if not employee_id:
            return Response(
                {"error": "Debes seleccionar un empleado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            employee_id = int(employee_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "El campo empleado no es válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance = Vacation.objects.filter(employee_id=employee_id).first()

        if instance:
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)


class VacationDetailView(generics.RetrieveUpdateAPIView):
    queryset         = Vacation.objects.select_related("employee").all()
    serializer_class = VacationSerializer


class RegistrarFaltaView(APIView):
    """
    POST /api/vacations/falta/
    Registra 1 día de falta por vacaciones para un empleado.
    """
    def post(self, request):
        serializer = RegistrarFaltaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        employee_id = serializer.validated_data["employee_id"]
        fecha       = serializer.validated_data["fecha"]
        motivo      = serializer.validated_data["motivo"]

        try:
            employee = Employee.objects.get(pk=employee_id, active=True)
        except Employee.DoesNotExist:
            return Response(
                {"error": f"Empleado con ID {employee_id} no existe o está inactivo."},
                status=status.HTTP_404_NOT_FOUND
            )

        vacation, _ = Vacation.objects.get_or_create(
            employee=employee,
            defaults={"dias_disponibles": 2, "dias_falta_pendiente": 0}
        )

        registrado = vacation.registrar_falta()

        if not registrado:
            return Response(
                {
                    "error": (
                        f"{employee.name} ya tiene "
                        f"{vacation.dias_falta_pendiente} día(s) de falta "
                        f"pendiente(s). No puede exceder los días disponibles "
                        f"({vacation.dias_disponibles})."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message":              f"Falta registrada para {employee.name} el {fecha}.",
                "motivo":               motivo,
                "dias_disponibles":     vacation.dias_disponibles,
                "dias_falta_pendiente": vacation.dias_falta_pendiente,
                "dias_a_pagar":         vacation.dias_a_pagar,
                "monto_siguiente_q1":   vacation.monto_vacaciones,
            },
            status=status.HTTP_200_OK
        )