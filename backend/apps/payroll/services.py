from decimal import Decimal
from datetime import date
import math

from apps.employees.models import Employee
from apps.vacations.models import Vacation, VacationAbsence
from .models import PayrollRecord


class PayrollValidationError(Exception):
    pass


def get_faltas_para_mes(employee, year: int, month: int) -> dict:
    """
    Calcula las faltas que afectan el Q1 de un mes específico
    usando directamente el campo mes_afectado de VacationAbsence.
    """
    mes_afectado_date = date(year, month, 1)

    total_faltas = VacationAbsence.objects.filter(
        employee     = employee,
        mes_afectado = mes_afectado_date,
    ).count()

    dias_a_pagar = max(0, 2 - total_faltas)

    return {
        "total_faltas": total_faltas,
        "dias_a_pagar": dias_a_pagar,
    }


def get_descuento_faltas_q2(employee, year: int, month: int) -> Decimal:
    """
    Calcula el descuento por faltas extra que se aplica en Q2.

    Regla:
    - Los 2 primeros días faltados en Q1 consumen vacaciones
    - A partir del 3er día faltado en Q1 → descuenta salario en Q2
    - Las faltas en Q2 NO descuentan salario, solo afectan vac del siguiente mes
    """
    faltas_q1 = VacationAbsence.objects.filter(
        employee     = employee,
        fecha__year  = year,
        fecha__month = month,
        es_q1        = True,
    ).count()

    # Solo los días Q1 que exceden los 2 días de vacaciones
    faltas_q1_extra = max(0, faltas_q1 - 2)

    if faltas_q1_extra == 0:
        return Decimal("0")

    pago_por_dia = Decimal(str(employee.salary_base)) / Decimal("15")
    return (pago_por_dia * faltas_q1_extra).quantize(Decimal("0.01"))
    """
    Calcula el descuento por faltas extra que se aplica en Q2.
    - Los 2 primeros días faltados del mes consumen vacaciones en Q1
    - A partir del 3er día faltado se descuenta de Q2
    - Las faltas en Q2 también descuentan directo
    """
    faltas_q1 = VacationAbsence.objects.filter(
        employee     = employee,
        fecha__year  = year,
        fecha__month = month,
        es_q1        = True,
    ).count()

    faltas_q2 = VacationAbsence.objects.filter(
        employee     = employee,
        fecha__year  = year,
        fecha__month = month,
        es_q1        = False,
    ).count()

    faltas_q1_extra      = max(0, faltas_q1 - 2)
    total_dias_descuento = faltas_q1_extra + faltas_q2

    if total_dias_descuento == 0:
        return Decimal("0")

    pago_por_dia = Decimal(str(employee.salary_base)) / Decimal("15")
    return (pago_por_dia * total_dias_descuento).quantize(Decimal("0.01"))


def get_descuento_tardanzas(employee, period: int, year: int, month: int) -> Decimal:
    """
    Recalcula el descuento real por tardanzas usando las horas reales.
    horas_tarde = ceil(minutos_tarde / 60)
    descuento   = horas_tarde × valor_por_hora
    """
    from apps.attendance.models import LateArrival

    tardanzas = LateArrival.objects.filter(
        employee     = employee,
        fecha__year  = year,
        fecha__month = month,
        period       = period,
    )

    if not tardanzas.exists():
        return Decimal("0")

    valor_por_hora = Decimal(str(employee.valor_por_hora))
    total          = Decimal("0")

    for t in tardanzas:
        horas  = math.ceil(t.minutos_tarde / 60)
        total += valor_por_hora * horas

    return total.quantize(Decimal("0.01"))


def calculate_vacation_payment(salary_base: Decimal, dias_a_pagar: int) -> Decimal:
    """
    Calcula el pago de vacaciones según días a pagar.
    dias_a_pagar × (salario ÷ 12). Mínimo C$0.
    """
    if dias_a_pagar <= 0:
        return Decimal("0")
    pago_por_dia = Decimal(str(salary_base)) / Decimal("12")
    return (pago_por_dia * dias_a_pagar).quantize(Decimal("0.01"))


def calculate_totals(
    salary_base: Decimal,
    vacation_payment: Decimal,
    viatico: Decimal,
    otras_deducciones: Decimal,
    prestamo_adelanto: Decimal,
    descuento_faltas: Decimal,
    period: int,
) -> dict:
    """
    Q1: sub_total = salary_base + vacation_payment + viatico
    Q2: sub_total = salary_base + viatico
    total = sub_total - otras_deducciones - prestamo_adelanto - descuento_faltas
    """
    salary_base       = Decimal(str(salary_base))
    viatico           = Decimal(str(viatico))
    otras_deducciones = Decimal(str(otras_deducciones))
    prestamo_adelanto = Decimal(str(prestamo_adelanto))
    descuento_faltas  = Decimal(str(descuento_faltas))
    vac               = Decimal(str(vacation_payment)) if period == 1 else Decimal("0")

    sub_total = salary_base + vac + viatico
    total     = sub_total - otras_deducciones - prestamo_adelanto - descuento_faltas

    return {
        "vacation_payment": vac,
        "sub_total":        sub_total.quantize(Decimal("0.01")),
        "total":            total.quantize(Decimal("0.01")),
    }


def get_vacation_payment_for_employee(
    employee, period: int, year: int, month: int
) -> Decimal:
    """Calcula vacaciones desde el historial real del mes."""
    if period != 1:
        return Decimal("0")

    faltas = get_faltas_para_mes(employee, year, month)
    return calculate_vacation_payment(
        salary_base  = employee.salary_base,
        dias_a_pagar = faltas["dias_a_pagar"],
    )


def generate_payroll(
    employee_id: int,
    payroll_date: date,
    period: int,
    dias_laborados: int = 15,
    viatico: Decimal = Decimal("0"),
    otras_deducciones: Decimal = Decimal("0"),
    prestamo_adelanto: Decimal = Decimal("0"),
    notes: str = "",
) -> PayrollRecord:
    """
    Genera o actualiza la nómina de un empleado.
    Q1: calcula vacation_payment desde historial real de faltas
    Q2: calcula descuento_faltas desde faltas del mes
    Ambos: calcula descuento por tardanzas usando horas reales
    """
    if period not in (1, 2):
        raise PayrollValidationError(
            "El período debe ser 1 (primera quincena) o 2 (segunda quincena)."
        )

    viatico           = Decimal(str(viatico))
    otras_deducciones = Decimal(str(otras_deducciones))
    prestamo_adelanto = Decimal(str(prestamo_adelanto))

    if otras_deducciones < 0:
        raise PayrollValidationError("Las deducciones no pueden ser negativas.")
    if prestamo_adelanto < 0:
        raise PayrollValidationError("El préstamo/adelanto no puede ser negativo.")
    if viatico < 0:
        raise PayrollValidationError("El viático no puede ser negativo.")

    try:
        employee = Employee.objects.get(pk=employee_id, active=True)
    except Employee.DoesNotExist:
        raise PayrollValidationError(
            f"Empleado con ID {employee_id} no existe o está inactivo."
        )

    # ── Vacaciones (solo Q1) ──────────────────────────────────────────────
    vacation_payment = get_vacation_payment_for_employee(
        employee = employee,
        period   = period,
        year     = payroll_date.year,
        month    = payroll_date.month,
    )

    # ── Descuento por faltas de vacaciones (solo Q2) ──────────────────────
    descuento_faltas = Decimal("0")
    if period == 2:
        descuento_faltas = get_descuento_faltas_q2(
            employee = employee,
            year     = payroll_date.year,
            month    = payroll_date.month,
        )

    # ── Descuento por tardanzas (Q1 y Q2) ────────────────────────────────
    descuento_tardanzas = get_descuento_tardanzas(
        employee = employee,
        period   = period,
        year     = payroll_date.year,
        month    = payroll_date.month,
    )

    otras_deducciones_total = otras_deducciones + descuento_tardanzas

    totals = calculate_totals(
        salary_base       = employee.salary_base,
        vacation_payment  = vacation_payment,
        viatico           = viatico,
        otras_deducciones = otras_deducciones_total,
        prestamo_adelanto = prestamo_adelanto,
        descuento_faltas  = descuento_faltas,
        period            = period,
    )

    record, _ = PayrollRecord.objects.update_or_create(
        employee = employee,
        date     = payroll_date,
        period   = period,
        defaults = {
            "dias_laborados":    dias_laborados,
            "salary_base":       employee.salary_base,
            "vacation_payment":  totals["vacation_payment"],
            "viatico":           viatico,
            "otras_deducciones": otras_deducciones_total,
            "prestamo_adelanto": prestamo_adelanto,
            "descuento_faltas":  descuento_faltas,
            "sub_total":         totals["sub_total"],
            "total":             totals["total"],
            "notes":             notes,
        }
    )

    return record


def generate_payroll_bulk(
    payroll_date: date,
    period: int,
    items: list,
) -> list:
    """Genera o actualiza la nómina de múltiples empleados."""
    if period not in (1, 2):
        raise PayrollValidationError(
            "El período debe ser 1 (primera quincena) o 2 (segunda quincena)."
        )

    if not items:
        raise PayrollValidationError("Debes incluir al menos un empleado.")

    records = []
    errors  = []

    for item in items:
        employee_id       = item["employee_id"]
        viatico           = Decimal(str(item.get("viatico",           0)))
        otras_deducciones = Decimal(str(item.get("otras_deducciones", 0)))
        prestamo_adelanto = Decimal(str(item.get("prestamo_adelanto", 0)))
        notes             = item.get("notes", "")

        try:
            employee = Employee.objects.get(pk=employee_id, active=True)
        except Employee.DoesNotExist:
            errors.append(f"Empleado ID {employee_id} no existe o está inactivo.")
            continue

        vacation_payment = get_vacation_payment_for_employee(
            employee = employee,
            period   = period,
            year     = payroll_date.year,
            month    = payroll_date.month,
        )

        descuento_faltas = Decimal("0")
        if period == 2:
            descuento_faltas = get_descuento_faltas_q2(
                employee = employee,
                year     = payroll_date.year,
                month    = payroll_date.month,
            )

        descuento_tardanzas = get_descuento_tardanzas(
            employee = employee,
            period   = period,
            year     = payroll_date.year,
            month    = payroll_date.month,
        )

        otras_deducciones_total = otras_deducciones + descuento_tardanzas

        totals = calculate_totals(
            salary_base       = employee.salary_base,
            vacation_payment  = vacation_payment,
            viatico           = viatico,
            otras_deducciones = otras_deducciones_total,
            prestamo_adelanto = prestamo_adelanto,
            descuento_faltas  = descuento_faltas,
            period            = period,
        )

        record, _ = PayrollRecord.objects.update_or_create(
            employee = employee,
            date     = payroll_date,
            period   = period,
            defaults = {
                "dias_laborados":    15,
                "salary_base":       employee.salary_base,
                "vacation_payment":  totals["vacation_payment"],
                "viatico":           viatico,
                "otras_deducciones": otras_deducciones_total,
                "prestamo_adelanto": prestamo_adelanto,
                "descuento_faltas":  descuento_faltas,
                "sub_total":         totals["sub_total"],
                "total":             totals["total"],
                "notes":             notes,
            }
        )
        records.append(record)

    if errors:
        raise PayrollValidationError(" | ".join(errors))

    return records