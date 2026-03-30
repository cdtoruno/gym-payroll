import math
from datetime import datetime
from decimal import Decimal
from io import BytesIO

from django.http import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.employees.models import Employee
from apps.vacations.models import VacationAbsence
from apps.attendance.models import LateArrival
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
    get_descuento_tardanzas,
    PayrollValidationError,
)
from .export import generate_payroll_excel


class PayrollListView(generics.ListAPIView):
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
    queryset         = PayrollRecord.objects.select_related("employee").all()
    serializer_class = PayrollRecordSerializer


class PayrollPreviewView(APIView):
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

            vacation_payment = 0
            dias_a_pagar     = 0

            if period == 1:
                faltas           = get_faltas_para_mes(
                    employee = emp,
                    year     = payroll_date.year,
                    month    = payroll_date.month,
                )
                dias_a_pagar     = faltas["dias_a_pagar"]
                pago_por_dia     = float(emp.salary_base) / 12
                vacation_payment = round(dias_a_pagar * pago_por_dia, 2)

            descuento_faltas = 0
            dias_descuento   = 0

            if period == 2:
                faltas_q1 = VacationAbsence.objects.filter(
                    employee     = emp,
                    fecha__year  = payroll_date.year,
                    fecha__month = payroll_date.month,
                    es_q1        = True,
                ).count()
                dias_descuento   = max(0, faltas_q1 - 2)
                pago_por_dia_q2  = float(emp.salary_base) / 15
                descuento_faltas = round(dias_descuento * pago_por_dia_q2, 2)

            descuento_tardanzas = float(get_descuento_tardanzas(
                employee = emp,
                period   = period,
                year     = payroll_date.year,
                month    = payroll_date.month,
            ))

            tardanzas = LateArrival.objects.filter(
                employee     = emp,
                fecha__year  = payroll_date.year,
                fecha__month = payroll_date.month,
                period       = period,
            )
            total_tardanzas   = tardanzas.count()
            total_horas_tarde = sum(
                math.ceil(t.minutos_tarde / 60) for t in tardanzas
            )

            preview.append({
                "employee_id":         emp.id,
                "employee_name":       emp.name,
                "employee_cedula":     emp.cedula,
                "employee_position":   emp.position,
                "salary_base":         float(emp.salary_base),
                "vacation_payment":    vacation_payment,
                "dias_a_pagar":        dias_a_pagar,
                "descuento_faltas":    descuento_faltas,
                "dias_descuento":      dias_descuento,
                "descuento_tardanzas": descuento_tardanzas,
                "total_tardanzas":     total_tardanzas,
                "total_horas_tarde":   total_horas_tarde,
                "viatico":             float(existing.viatico)           if existing else 0,
                "otras_deducciones":   float(existing.otras_deducciones) if existing else 0,
                "prestamo_adelanto":   float(existing.prestamo_adelanto) if existing else 0,
                "notes":               existing.notes                    if existing else "",
                "already_generated":   existing is not None,
                "record_id":           existing.id                       if existing else None,
            })

        return Response(preview)


class GeneratePayrollBulkView(APIView):
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
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PayrollRecordSerializer(records, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class GeneratePayrollView(APIView):
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


@method_decorator(csrf_exempt, name="dispatch")
class ExportPayrollExcelView(View):
    """
    GET /api/payroll/export/
    Vista Django pura — evita que DRF re-codifique el binario.
    """
    def get(self, request):
        import tempfile
        import os

        qs = PayrollRecord.objects.select_related("employee").all()
        p  = request.GET

        if p.get("period"):    qs = qs.filter(period=p["period"])
        if p.get("date_from"): qs = qs.filter(date__gte=p["date_from"])
        if p.get("date_to"):   qs = qs.filter(date__lte=p["date_to"])

        if not qs.exists():
            return HttpResponse(
                '{"error": "No hay registros para exportar."}',
                content_type="application/json",
                status=404
            )

        first  = qs.first()
        month  = first.date.month
        year   = first.date.year
        period = first.period

        records_data = []
        for r in qs.order_by("employee__name"):
            # Contar faltas del mes para descontar días laborados
            faltas_mes = VacationAbsence.objects.filter(
                employee     = r.employee,
                fecha__year  = r.date.year,
                fecha__month = r.date.month,
            ).count()

            dias_laborados = max(0, r.dias_laborados - faltas_mes)

            descuento_tardanzas = get_descuento_tardanzas(
                employee = r.employee,
                period   = period,
                year     = year,
                month    = month,
            )

            records_data.append({
                "employee_name":       r.employee.name,
                "employee_position":   r.employee.position,
                "employee_cedula":     r.employee.cedula,
                "dias_laborados":      dias_laborados,
                "salary_base":         float(r.salary_base),
                "vacation_payment":    float(r.vacation_payment),
                "sub_total":           float(r.sub_total),
                "otras_deducciones":   float(r.otras_deducciones),
                "prestamo_adelanto":   float(r.prestamo_adelanto),
                "descuento_tardanzas": float(descuento_tardanzas),
                "total":               float(r.total),
            })

        wb  = generate_payroll_excel(records_data, period, month, year)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        wb.save(tmp.name)
        tmp.close()

        with open(tmp.name, "rb") as f:
            excel_data = f.read()
        os.unlink(tmp.name)

        filename = f"planilla_{year}_{month:02d}_Q{period}.xlsx"
        response = HttpResponse(
            excel_data,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Content-Length"]      = len(excel_data)
        return response