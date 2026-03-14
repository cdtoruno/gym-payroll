from decimal import Decimal
from datetime import date

from apps.employees.models import Employee
from apps.vacations.models import Vacation, VacationAbsence
from .models import PayrollRecord


class PayrollValidationError(Exception):
    pass


def calculate_vacation_payment(salary_base: Decimal, dias_a_pagar: int) -> Decimal:
    """
    Calcula el pago de vacaciones según días a pagar.
    dias_a_pagar × (salario ÷ 12). Mínimo C$0.
    """
    if dias_a_pagar <= 0:
        return Decimal("0")
    pago_por_dia = Decimal(str(salary_base)) / Decimal("12")
    return (pago_por_dia * dias_a_pagar).quantize(Decimal("0.01"))


def get_faltas_para_mes(employee, year: int, month: int) -> dict:
    """
    Calcula las faltas que afectan el Q1 de un mes específico
    usando directamente el campo mes_afectado de VacationAbsence.

    mes_afectado ya fue calculado correctamente al registrar la falta:
    - Falta en Q1 de Marzo  → mes_afectado = 01/03
    - Falta en Q2 de Marzo  → mes_afectado = 01/04

    Por lo tanto filtrar por mes_afectado = date(year, month, 1)
    devuelve exactamente las faltas que afectan ese Q1 y solo ese.
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
    
    
    """
    Calcula las faltas reales para un mes específico
    consultando directamente el historial de VacationAbsence.

    Reglas:
    - Faltas en Q1 del mes year/month → descuentan del Q1 de ese mes
    - Faltas en Q2 del mes anterior  → también descuentan del Q1 de year/month

    Retorna:
        {
          "faltas_q1": int,   faltas directas en Q1 de este mes
          "faltas_q2_prev": int,  faltas en Q2 del mes anterior
          "total_faltas": int,   suma de ambas
          "dias_a_pagar": int,   max(0, 2 - total_faltas)
        }
    """
    # Faltas en Q1 del mes actual (días 1-15)
    faltas_q1 = VacationAbsence.objects.filter(
        employee   = employee,
        fecha__year  = year,
        fecha__month = month,
        es_q1        = True,
    ).count()

    # Faltas en Q2 del mes anterior (días 16-31 del mes previo)
    if month == 1:
        prev_year  = year - 1
        prev_month = 12
    else:
        prev_year  = year
        prev_month = month - 1

    faltas_q2_prev = VacationAbsence.objects.filter(
        employee     = employee,
        fecha__year  = prev_year,
        fecha__month = prev_month,
        es_q1        = False,
    ).count()

    total_faltas = faltas_q1 + faltas_q2_prev
    dias_a_pagar = max(0, 2 - total_faltas)

    return {
        "faltas_q1":      faltas_q1,
        "faltas_q2_prev": faltas_q2_prev,
        "total_faltas":   total_faltas,
        "dias_a_pagar":   dias_a_pagar,
    }


def calculate_totals(
    salary_base: Decimal,
    vacation_payment: Decimal,
    viatico: Decimal,
    otras_deducciones: Decimal,
    prestamo_adelanto: Decimal,
    period: int,
) -> dict:
    """
    Cálculo puro sin acceso a BD.
    sub_total = salary_base + viatico [+ vacation_payment si Q1]
    total     = sub_total - otras_deducciones - prestamo_adelanto
    """
    salary_base       = Decimal(str(salary_base))
    viatico           = Decimal(str(viatico))
    otras_deducciones = Decimal(str(otras_deducciones))
    prestamo_adelanto = Decimal(str(prestamo_adelanto))
    vac               = Decimal(str(vacation_payment)) if period == 1 else Decimal("0")

    sub_total = salary_base + vac + viatico
    total     = sub_total - otras_deducciones - prestamo_adelanto

    return {
        "vacation_payment": vac,
        "sub_total":        sub_total.quantize(Decimal("0.01")),
        "total":            total.quantize(Decimal("0.01")),
    }


def get_vacation_payment_for_employee(
    employee, period: int, year: int, month: int
) -> Decimal:
    """
    Calcula el pago de vacaciones para un empleado en un período específico.
    Consulta VacationAbsence para el mes exacto — no usa el estado persistido.
    Solo aplica en Q1 (period == 1).
    """
    if period != 1:
        return Decimal("0")

    faltas = get_faltas_para_mes(employee, year, month)
    vacation_payment = calculate_vacation_payment(
        salary_base  = employee.salary_base,
        dias_a_pagar = faltas["dias_a_pagar"],
    )

    return vacation_payment


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
    Las vacaciones se calculan desde el historial real de faltas
    del mes de la nómina — no desde el estado persistido del modelo.
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

    # ── Calcular vacaciones desde el historial real del mes ───────────────
    vacation_payment = get_vacation_payment_for_employee(
        employee = employee,
        period   = period,
        year     = payroll_date.year,
        month    = payroll_date.month,
    )

    totals = calculate_totals(
        salary_base       = employee.salary_base,
        vacation_payment  = vacation_payment,
        viatico           = viatico,
        otras_deducciones = otras_deducciones,
        prestamo_adelanto = prestamo_adelanto,
        period            = period,
    )

    # Crear o actualizar
    record, _ = PayrollRecord.objects.update_or_create(
        employee = employee,
        date     = payroll_date,
        period   = period,
        defaults = {
            "dias_laborados":    dias_laborados,
            "salary_base":       employee.salary_base,
            "vacation_payment":  totals["vacation_payment"],
            "viatico":           viatico,
            "otras_deducciones": otras_deducciones,
            "prestamo_adelanto": prestamo_adelanto,
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
    """
    Genera o actualiza la nómina de múltiples empleados.
    """
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

        # Calcular vacaciones desde historial real del mes
        vacation_payment = get_vacation_payment_for_employee(
            employee = employee,
            period   = period,
            year     = payroll_date.year,
            month    = payroll_date.month,
        )

        totals = calculate_totals(
            salary_base       = employee.salary_base,
            vacation_payment  = vacation_payment,
            viatico           = viatico,
            otras_deducciones = otras_deducciones,
            prestamo_adelanto = prestamo_adelanto,
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
                "otras_deducciones": otras_deducciones,
                "prestamo_adelanto": prestamo_adelanto,
                "sub_total":         totals["sub_total"],
                "total":             totals["total"],
                "notes":             notes,
            }
        )
        records.append(record)

    if errors:
        raise PayrollValidationError(" | ".join(errors))

    return records
