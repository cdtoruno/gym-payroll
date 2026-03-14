from decimal import Decimal
from datetime import date

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.employees.models import Employee
from apps.payroll.models import PayrollRecord
from .models import Vacation, VacationAbsence
from .serializers import (
    VacationSerializer,
    VacationAbsenceSerializer,
    RegistrarFaltaSerializer,
)


class VacationListCreateView(generics.ListCreateAPIView):
    queryset         = Vacation.objects.select_related("employee").all()
    serializer_class = VacationSerializer

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get("employee")
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


class VacationAbsenceListView(generics.ListAPIView):
    """
    GET /api/vacations/absences/
    Lista todas las faltas registradas.
    Soporta ?employee=, ?month=, ?year=
    """
    serializer_class = VacationAbsenceSerializer

    def get_queryset(self):
        qs = VacationAbsence.objects.select_related("employee").all()
        p  = self.request.query_params

        if p.get("employee"):
            qs = qs.filter(employee_id=p["employee"])
        if p.get("month") and p.get("year"):
            qs = qs.filter(
                fecha__year=p["year"],
                fecha__month=p["month"]
            )
        elif p.get("year"):
            qs = qs.filter(fecha__year=p["year"])

        return qs


class RegistrarFaltaView(APIView):
    """
    POST /api/vacations/falta/
    Registra 1 día de falta por vacaciones.
    Valida que no exista ya una falta el mismo día.
    Si ya existe nómina Q1 del mes → recalcula automáticamente.
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

        # ── Buscar empleado ───────────────────────────────────────────────
        try:
            employee = Employee.objects.get(pk=employee_id, active=True)
        except Employee.DoesNotExist:
            return Response(
                {"error": f"Empleado con ID {employee_id} no existe o está inactivo."},
                status=status.HTTP_404_NOT_FOUND
            )

        # ── Validar que no exista ya una falta ese mismo día ──────────────
        ya_existe = VacationAbsence.objects.filter(
            employee=employee,
            fecha=fecha
        ).exists()

        if ya_existe:
            return Response(
                {
                    "error": (
                        f"{employee.name} ya tiene una falta registrada "
                        f"el {fecha.strftime('%d/%m/%Y')}. "
                        f"No se puede registrar dos faltas el mismo día."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── Buscar o crear registro de vacaciones ─────────────────────────
        vacation, _ = Vacation.objects.get_or_create(
            employee=employee,
            defaults={"dias_disponibles": 2, "dias_falta_q1": 0, "dias_falta_q2": 0}
        )

       # ── Registrar la falta ────────────────────────────────────────────────────────
        vacation.registrar_falta(fecha)

        # ── Determinar si es Q1 o Q2 y el mes afectado ───────────────────
        es_q1 = fecha.day <= 15

        if es_q1:
            mes_afectado = date(fecha.year, fecha.month, 1)
        else:
            if fecha.month == 12:
                mes_afectado = date(fecha.year + 1, 1, 1)
            else:
                mes_afectado = date(fecha.year, fecha.month + 1, 1)

        # ── Guardar en historial ──────────────────────────────────────────
        VacationAbsence.objects.create(
            employee     = employee,
            fecha        = fecha,
            motivo       = motivo,
            es_q1        = es_q1,
            mes_afectado = mes_afectado,
        )

        # ── Si falta en Q1 y ya existe nómina → recalcular ───────────────
        nomina_actualizada = None

        if es_q1:
            fecha_inicio_mes = date(fecha.year, fecha.month, 1)
            nomina_q1 = PayrollRecord.objects.filter(
                employee = employee,
                date     = fecha_inicio_mes,
                period   = 1,
            ).first()

            if nomina_q1:
                pago_por_dia    = Decimal(str(employee.salary_base)) / Decimal("12")
                nuevo_vac       = (pago_por_dia * vacation.dias_a_pagar).quantize(Decimal("0.01"))
                nuevo_sub_total = (
                    Decimal(str(nomina_q1.salary_base))
                    + nuevo_vac
                    + Decimal(str(nomina_q1.viatico))
                )
                nuevo_total = (
                    nuevo_sub_total
                    - Decimal(str(nomina_q1.otras_deducciones))
                    - Decimal(str(nomina_q1.prestamo_adelanto))
                )
                nomina_q1.vacation_payment = nuevo_vac
                nomina_q1.sub_total        = nuevo_sub_total.quantize(Decimal("0.01"))
                nomina_q1.total            = nuevo_total.quantize(Decimal("0.01"))
                nomina_q1.save(update_fields=[
                    "vacation_payment", "sub_total", "total", "updated_at"
                ])
                nomina_actualizada = {
                    "id":               nomina_q1.id,
                    "vacation_payment": float(nuevo_vac),
                    "sub_total":        float(nomina_q1.sub_total),
                    "total":            float(nomina_q1.total),
                }

        meses = [
            "", "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        return Response(
            {
                "message": (
                    f"Falta del {fecha.day} de "
                    f"{meses[fecha.month]} registrada para {employee.name}."
                ),
                "motivo":             motivo,
                "es_q1":              es_q1,
                "mes_afectado":       f"{meses[mes_afectado.month]} {mes_afectado.year}",
                "dias_disponibles":   vacation.dias_disponibles,
                "dias_falta_q1":      vacation.dias_falta_q1,
                "dias_falta_q2":      vacation.dias_falta_q2,
                "dias_a_pagar":       vacation.dias_a_pagar,
                "monto_siguiente_q1": vacation.monto_vacaciones,
                "nomina_actualizada": nomina_actualizada,
            },
            status=status.HTTP_200_OK
        )