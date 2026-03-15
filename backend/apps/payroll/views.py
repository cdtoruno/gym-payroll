import csv
from datetime import datetime

from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.employees.models import Employee
from apps.vacations.models import VacationAbsence
from .models import PayrollRecord
from .serializers import (
    PayrollRecordSerializer,
    GeneratePayrollSerializer,
    BulkPayrollSerializer,
)
from .services import (
    generate_payroll,
    generate_payroll_bulk,
    get_faltas_para_mes,
    get_descuento_faltas_q2,
    PayrollValidationError,
)


class PayrollListView(generics.ListAPIView):
    """
    GET /api/payroll/
    Soporta ?period= ?date_from= ?date_to= ?employee=
    """
    serializer_class = PayrollRecordSerializer

    def get_queryset(self):
        qs = PayrollRecord.objects.select_related("employee").all()
        p  = self.request.query_params

        if p.get("period"):    qs = qs.filter(period=p["period"])
        if p.get("date_from"): qs = qs.filter(date__gte=p["date_from"])
        if p.get("date_to"):   qs = qs.filter(date__lte=p["date_to"])
        if p.get("employee"):  qs = qs.filter(employee_id=p["employee"])
        return qs


class PayrollDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/payroll/{id}/
    DELETE /api/payroll/{id}/
    """
    queryset         = PayrollRecord.objects.select_related("employee").all()
    serializer_class = PayrollRecordSerializer


class PayrollPreviewView(APIView):
    """
    GET /api/payroll/preview/?date=YYYY-MM-DD&period=1
    Muestra todos los empleados con vacaciones y descuentos
    calculados desde el historial real de faltas.
    """
    def get(self, request):
        payroll_date = request.query_params.get("date")
        period       = request.query_params.get("period")

        if not payroll_date or not period:
            return Response(
                {"error": "Se requieren los parámetros date y period."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            period       = int(period)
            payroll_date = datetime.strptime(payroll_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        employees = Employee.objects.filter(active=True).order_by("name")
        preview   = []

        for emp in employees:
            existing = PayrollRecord.objects.filter(
                employee = emp,
                date     = payroll_date,
                period   = period
            ).first()

            # ── Vacaciones desde historial real (solo Q1) ─────────────────
            vacation_payment = 0
            dias_a_pagar     = 0

            if period == 1:
                faltas       = get_faltas_para_mes(
                    employee = emp,
                    year     = payroll_date.year,
                    month    = payroll_date.month,
                )
                dias_a_pagar     = faltas["dias_a_pagar"]
                pago_por_dia     = float(emp.salary_base) / 12
                vacation_payment = round(dias_a_pagar * pago_por_dia, 2)

            # ── Descuento por faltas (solo Q2) ────────────────────────────
            descuento_faltas = 0
            dias_descuento   = 0

            if period == 2:
                # Faltas Q1 que exceden 2 días
                faltas_q1 = VacationAbsence.objects.filter(
                    employee     = emp,
                    fecha__year  = payroll_date.year,
                    fecha__month = payroll_date.month,
                    es_q1        = True,
                ).count()

                # Faltas Q2 del mes
                faltas_q2 = VacationAbsence.objects.filter(
                    employee     = emp,
                    fecha__year  = payroll_date.year,
                    fecha__month = payroll_date.month,
                    es_q1        = False,
                ).count()

                dias_descuento   = max(0, faltas_q1 - 2) + faltas_q2
                pago_por_dia_q2  = float(emp.salary_base) / 15
                descuento_faltas = round(dias_descuento * pago_por_dia_q2, 2)

            preview.append({
                "employee_id":       emp.id,
                "employee_name":     emp.name,
                "employee_cedula":   emp.cedula,
                "employee_position": emp.position,
                "salary_base":       float(emp.salary_base),
                # Q1
                "vacation_payment":  vacation_payment,
                "dias_a_pagar":      dias_a_pagar,
                # Q2
                "descuento_faltas":  descuento_faltas,
                "dias_descuento":    dias_descuento,
                # Editables existentes
                "viatico":           float(existing.viatico)           if existing else 0,
                "otras_deducciones": float(existing.otras_deducciones) if existing else 0,
                "prestamo_adelanto": float(existing.prestamo_adelanto) if existing else 0,
                "notes":             existing.notes                    if existing else "",
                "already_generated": existing is not None,
                "record_id":         existing.id                       if existing else None,
            })

        return Response(preview)


class GeneratePayrollBulkView(APIView):
    """
    POST /api/payroll/generate-bulk/
    """
    def post(self, request):
        serializer = BulkPayrollSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        try:
            records = generate_payroll_bulk(
                payroll_date = data["date"],
                period       = data["period"],
                items        = data["items"],
            )
        except PayrollValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            PayrollRecordSerializer(records, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class GeneratePayrollView(APIView):
    """
    POST /api/payroll/generate/
    """
    def post(self, request):
        serializer = GeneratePayrollSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            record = generate_payroll(
                employee_id       = data["employee"],
                payroll_date      = data["date"],
                period            = data["period"],
                dias_laborados    = data.get("dias_laborados",    15),
                viatico           = data.get("viatico",           0),
                otras_deducciones = data.get("otras_deducciones", 0),
                prestamo_adelanto = data.get("prestamo_adelanto", 0),
                notes             = data.get("notes",             ""),
            )
        except PayrollValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollRecordSerializer(record).data,
            status=status.HTTP_201_CREATED,
        )


class ExportPayrollCSVView(APIView):
    """
    GET /api/payroll/export/
    """
    def get(self, request):
        qs = PayrollRecord.objects.select_related("employee").all()
        p  = request.query_params

        if p.get("period"):    qs = qs.filter(period=p["period"])
        if p.get("date_from"): qs = qs.filter(date__gte=p["date_from"])
        if p.get("date_to"):   qs = qs.filter(date__lte=p["date_to"])

        filename = f"nomina_{datetime.now():%Y%m%d_%H%M%S}.csv"
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow([
            "No.", "Nombres y Apellidos", "Cargo", "Días Laborados", "Cédula",
            "Salario Ordinario", "Vacaciones", "Viático",
            "Sub-Total Devengado",
            "Otras Deducciones", "Deduc. Préstamo/Adelanto",
            "Descuento Faltas",
            "Total Devengado", "Notas", "Generado",
        ])

        for i, r in enumerate(qs, start=1):
            writer.writerow([
                i,
                r.employee.name,
                r.employee.position,
                r.dias_laborados,
                r.employee.cedula,
                r.salary_base,
                r.vacation_payment,
                r.viatico,
                r.sub_total,
                r.otras_deducciones,
                r.prestamo_adelanto,
                r.descuento_faltas,
                r.total,
                r.notes,
                r.created_at.strftime("%Y-%m-%d %H:%M"),
            ])

        return response