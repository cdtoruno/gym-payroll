import math
from decimal import Decimal
from datetime import datetime

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.employees.models import Employee
from apps.payroll.models import PayrollRecord
from .models import LateArrival
from .serializers import LateArrivalSerializer, RegisterLateArrivalSerializer


class LateArrivalListView(generics.ListAPIView):
    """
    GET /api/attendance/
    Lista todas las llegadas tarde.
    Soporta ?employee=, ?month=, ?year=, ?period=
    """
    serializer_class = LateArrivalSerializer

    def get_queryset(self):
        qs = LateArrival.objects.select_related("employee").all()
        p  = self.request.query_params

        if p.get("employee"): qs = qs.filter(employee_id=p["employee"])
        if p.get("period"):   qs = qs.filter(period=p["period"])
        if p.get("month") and p.get("year"):
            qs = qs.filter(
                fecha__year=p["year"],
                fecha__month=p["month"]
            )
        elif p.get("year"):
            qs = qs.filter(fecha__year=p["year"])

        return qs


class RegisterLateArrivalView(APIView):
    """
    POST /api/attendance/register/
    Registra una llegada tarde y actualiza la nómina si ya existe.
    """
    def post(self, request):
        serializer = RegisterLateArrivalSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data         = serializer.validated_data
        employee_id  = data["employee_id"]
        fecha        = data["fecha"]
        hora_llegada = data["hora_llegada"]
        notas        = data.get("notas", "")

        # ── Buscar empleado ───────────────────────────────────────────────
        try:
            employee = Employee.objects.get(pk=employee_id, active=True)
        except Employee.DoesNotExist:
            return Response(
                {"error": f"Empleado con ID {employee_id} no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # ── Verificar horario configurado ─────────────────────────────────
        if not employee.hora_entrada:
            return Response(
                {"error": f"{employee.name} no tiene horario configurado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── Verificar duplicado ───────────────────────────────────────────
        if LateArrival.objects.filter(employee=employee, fecha=fecha).exists():
            return Response(
                {"error": f"{employee.name} ya tiene una llegada tarde registrada el {fecha}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── Calcular minutos tarde ────────────────────────────────────────
        hora_entrada_dt = datetime.combine(fecha, employee.hora_entrada)
        hora_llegada_dt = datetime.combine(fecha, hora_llegada)
        diferencia      = hora_llegada_dt - hora_entrada_dt
        minutos_tarde   = int(diferencia.total_seconds() / 60)

        if minutos_tarde <= 0:
            return Response(
                {
                    "error": (
                        f"{employee.name} no llegó tarde. "
                        f"Su hora de entrada es {employee.hora_entrada} "
                        f"y llegó a las {hora_llegada}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── Calcular horas tarde y descuento ──────────────────────────────
        horas_tarde = math.ceil(minutos_tarde / 60)
        descuento   = Decimal(str(employee.valor_por_hora)) * horas_tarde
        descuento   = descuento.quantize(Decimal("0.01"))
        period      = 1 if fecha.day <= 15 else 2

        # ── Crear registro ────────────────────────────────────────────────
        LateArrival.objects.create(
            employee      = employee,
            fecha         = fecha,
            hora_llegada  = hora_llegada,
            minutos_tarde = minutos_tarde,
            descuento     = descuento,
            period        = period,
            notas         = notas,
        )

        # ── Si ya existe nómina → actualizar el descuento ─────────────────
        nomina_actualizada = None

        nomina = PayrollRecord.objects.filter(
            employee    = employee,
            date__year  = fecha.year,
            date__month = fecha.month,
            period      = period,
        ).first()

        if nomina:
            total_descuento_tardanzas = sum(
                Decimal(str(t.descuento))
                for t in LateArrival.objects.filter(
                    employee     = employee,
                    fecha__year  = fecha.year,
                    fecha__month = fecha.month,
                    period       = period,
                )
            )
            nomina.otras_deducciones = (
                Decimal(str(nomina.otras_deducciones)) + descuento
            )
            nomina.total = (
                Decimal(str(nomina.sub_total))
                - Decimal(str(nomina.otras_deducciones))
                - Decimal(str(nomina.prestamo_adelanto))
                - Decimal(str(nomina.descuento_faltas))
            )
            nomina.save(update_fields=["otras_deducciones", "total", "updated_at"])
            nomina_actualizada = {
                "id":                nomina.id,
                "otras_deducciones": float(nomina.otras_deducciones),
                "total":             float(nomina.total),
            }

        meses = [
            "", "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        return Response(
            {
                "message": (
                    f"Llegada tarde registrada para {employee.name} "
                    f"el {fecha.day} de {meses[fecha.month]}. "
                    f"Llegó {minutos_tarde} min tarde ({horas_tarde} hora(s)). "
                    f"Descuento: C${descuento}"
                ),
                "minutos_tarde":      minutos_tarde,
                "horas_tarde":        horas_tarde,
                "descuento":          float(descuento),
                "period":             period,
                "nomina_actualizada": nomina_actualizada,
            },
            status=status.HTTP_201_CREATED
        )


class AttendanceSummaryView(APIView):
    """
    GET /api/attendance/summary/?month=3&year=2026
    Resumen de tardanzas por empleado en un mes.
    """
    def get(self, request):
        month = request.query_params.get("month")
        year  = request.query_params.get("year")

        if not month or not year:
            return Response(
                {"error": "Se requieren month y year."},
                status=status.HTTP_400_BAD_REQUEST
            )

        employees = Employee.objects.filter(active=True).order_by("name")
        summary   = []

        for emp in employees:
            tardanzas = LateArrival.objects.filter(
                employee     = emp,
                fecha__year  = year,
                fecha__month = month,
            )

            total_descuento = sum(
                Decimal(str(t.descuento)) for t in tardanzas
            )

            total_horas = sum(
                math.ceil(t.minutos_tarde / 60) for t in tardanzas
            )

            summary.append({
                "employee_id":       emp.id,
                "employee_name":     emp.name,
                "employee_position": emp.position,
                "hora_entrada":      str(emp.hora_entrada) if emp.hora_entrada else None,
                "hora_salida":       str(emp.hora_salida)  if emp.hora_salida  else None,
                "horas_por_dia":     float(emp.horas_por_dia) if emp.horas_por_dia else None,
                "valor_por_hora":    emp.valor_por_hora,
                "tardanzas_q1":      tardanzas.filter(period=1).count(),
                "tardanzas_q2":      tardanzas.filter(period=2).count(),
                "total_tardanzas":   tardanzas.count(),
                "total_horas":       total_horas,
                "total_descuento":   float(total_descuento),
                "detalle":           LateArrivalSerializer(tardanzas, many=True).data,
            })

        return Response(summary)