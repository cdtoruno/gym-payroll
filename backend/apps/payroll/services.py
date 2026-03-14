from decimal import Decimal
from datetime import date

from apps.employees.models import Employee
from apps.vacations.models import Vacation
from .models import PayrollRecord


class PayrollValidationError(Exception):
    pass


def calculate_vacation_payment(salary_base: Decimal, dias_a_pagar: int) -> Decimal:
    """
    Calcula el pago de vacaciones según días a pagar.

    Fórmula: dias_a_pagar × (salario ÷ 12)
    - 2 días → salario ÷ 6  (normal)
    - 1 día  → salario ÷ 12 (faltó 1 día en Q1 o Q2 anterior)
    - 0 días → C$0           (faltó ambos días)
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
    period: int,
) -> dict:
    """
    Cálculo puro sin acceso a BD.

    Fórmula:
        sub_total = salary_base + viatico [+ vacation_payment si Q1]
        total     = sub_total - otras_deducciones - prestamo_adelanto
    """
    salary_base       = Decimal(str(salary_base))
    viatico           = Decimal(str(viatico))
    otras_deducciones = Decimal(str(otras_deducciones))
    prestamo_adelanto = Decimal(str(prestamo_adelanto))

    vac = Decimal(str(vacation_payment)) if period == 1 else Decimal("0")

    sub_total = salary_base + vac + viatico
    total     = sub_total - otras_deducciones - prestamo_adelanto

    return {
        "vacation_payment": vac,
        "sub_total":        sub_total.quantize(Decimal("0.01")),
        "total":            total.quantize(Decimal("0.01")),
    }


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
    Valida, calcula y persiste el registro de nómina.

    Lógica de vacaciones en Q1:
    1. Se llama iniciar_nuevo_mes() → acredita 2 días frescos y
       transfiere faltas de Q2 anterior a Q1 actual
    2. Se calcula el pago según dias_a_pagar (ya con las faltas aplicadas)
    3. Las faltas de Q1 que ocurran DESPUÉS de generar la nómina
       aún afectan retroactivamente (se registran via /vacations/falta/)

    Raises:
        PayrollValidationError: si se violan reglas de negocio.
    """
    # ── Validar período ───────────────────────────────────────────────────────
    if period not in (1, 2):
        raise PayrollValidationError(
            "El período debe ser 1 (primera quincena) o 2 (segunda quincena)."
        )

    # ── Convertir y validar montos ────────────────────────────────────────────
    viatico           = Decimal(str(viatico))
    otras_deducciones = Decimal(str(otras_deducciones))
    prestamo_adelanto = Decimal(str(prestamo_adelanto))

    if otras_deducciones < 0:
        raise PayrollValidationError("Las deducciones no pueden ser negativas.")
    if prestamo_adelanto < 0:
        raise PayrollValidationError("El préstamo/adelanto no puede ser negativo.")
    if viatico < 0:
        raise PayrollValidationError("El viático no puede ser negativo.")

    # ── Buscar empleado activo ────────────────────────────────────────────────
    try:
        employee = Employee.objects.get(pk=employee_id, active=True)
    except Employee.DoesNotExist:
        raise PayrollValidationError(
            f"Empleado con ID {employee_id} no existe o está inactivo."
        )

    # ── Verificar nómina duplicada ────────────────────────────────────────────
    if PayrollRecord.objects.filter(
        employee=employee, date=payroll_date, period=period
    ).exists():
        quincena = "primera" if period == 1 else "segunda"
        raise PayrollValidationError(
            f"Ya existe una nómina para '{employee.name}' "
            f"en la {quincena} quincena de "
            f"{payroll_date.strftime('%B %Y')}."
        )

    # ── Calcular vacaciones en Q1 ─────────────────────────────────────────────
    vacation_payment = Decimal("0")
    vacation_record  = None

    if period == 1:
        # Buscar o crear registro de vacaciones
        vacation_record, _ = Vacation.objects.get_or_create(
            employee=employee,
            defaults={
                "dias_disponibles":  2,
                "dias_falta_q1":     0,
                "dias_falta_q2":     0,
            }
        )

        # Iniciar nuevo mes:
        # - Acredita 2 días frescos
        # - Transfiere faltas de Q2 anterior → Q1 actual
        vacation_record.iniciar_nuevo_mes(
            year=payroll_date.year,
            month=payroll_date.month,
        )

        # Calcular pago con las faltas ya aplicadas
        vacation_payment = calculate_vacation_payment(
            salary_base  = employee.salary_base,
            dias_a_pagar = vacation_record.dias_a_pagar,
        )

    # ── Calcular sub_total y total ────────────────────────────────────────────
    totals = calculate_totals(
        salary_base       = employee.salary_base,
        vacation_payment  = vacation_payment,
        viatico           = viatico,
        otras_deducciones = otras_deducciones,
        prestamo_adelanto = prestamo_adelanto,
        period            = period,
    )

    # ── Persistir nómina ──────────────────────────────────────────────────────
    record = PayrollRecord.objects.create(
        employee          = employee,
        date              = payroll_date,
        period            = period,
        dias_laborados    = dias_laborados,
        salary_base       = employee.salary_base,
        vacation_payment  = totals["vacation_payment"],
        viatico           = viatico,
        otras_deducciones = otras_deducciones,
        prestamo_adelanto = prestamo_adelanto,
        sub_total         = totals["sub_total"],
        total             = totals["total"],
        notes             = notes,
    )

    return record
