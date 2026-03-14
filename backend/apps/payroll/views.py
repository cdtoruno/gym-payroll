import csv
from datetime import datetime

from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import PayrollRecord
from .serializers import PayrollRecordSerializer, GeneratePayrollSerializer
from .services import generate_payroll, PayrollValidationError


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


class GeneratePayrollView(APIView):
    """
    POST /api/payroll/generate/
    Valida, calcula y guarda un nuevo registro de nómina.
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
    Descarga el historial como CSV — mismo formato que el Excel.
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
        response.write("\ufeff")  # BOM para Excel en Windows

        writer = csv.writer(response)
        writer.writerow([
            "No.", "Nombres y Apellidos", "Cargo", "Días Laborados", "Cédula",
            "Salario Ordinario", "Vacaciones", "Viático",
            "Sub-Total Devengado",
            "Otras Deducciones", "Deduc. Préstamo/Adelanto",
            "Total Devengado",
            "Notas", "Generado",
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
                r.total,
                r.notes,
                r.created_at.strftime("%Y-%m-%d %H:%M"),
            ])

        return response