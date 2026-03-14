from decimal import Decimal
from datetime import date
from django.core.management.base import BaseCommand
from apps.employees.models import Employee
from apps.payroll.models import PayrollRecord


class Command(BaseCommand):
    help = 'Carga los datos del Excel de nóminas de Febrero 2026'

    def handle(self, *args, **kwargs):
        self.stdout.write('🏋️  Cargando datos del Gym Dado...\n')

        # ── Empleados ─────────────────────────────────────────────────────────
        empleados_data = [
            {
                'name':        'Giovany Jafet Martinez Montoya',
                'cedula':      '001-020803-1058H',
                'position':    'Entrenador',
                'salary_base': Decimal('5000.00'),
                'hire_date':   date(2020, 1, 1),
            },
            {
                'name':        'Julio Cesar Castillo Jarquin',
                'cedula':      '001-240493-0017J',
                'position':    'Entrenador',
                'salary_base': Decimal('4500.00'),
                'hire_date':   date(2020, 1, 1),
            },
            {
                'name':        'Aaron Haniel Duarte Lindo',
                'cedula':      '001-090880-0081S',
                'position':    'Entrenador',
                'salary_base': Decimal('6500.00'),
                'hire_date':   date(2020, 1, 1),
            },
            {
                'name':        'Sitri Zambrana Quiroz',
                'cedula':      '001-110964-0020Y',
                'position':    'Mantenimiento',
                'salary_base': Decimal('5000.00'),
                'hire_date':   date(2020, 1, 1),
            },
            {
                'name':        'Pedro José Guevara García',
                'cedula':      '001-030561-0050E',
                'position':    'Conserje',
                'salary_base': Decimal('3500.00'),
                'hire_date':   date(2020, 1, 1),
            },
            {
                'name':        'Estefany Andrea Navarro Lopez',
                'cedula':      '001-041296-0004M',
                'position':    'Recepción',
                'salary_base': Decimal('3000.00'),
                'hire_date':   date(2020, 1, 1),
            },
        ]

        empleados = {}
        for data in empleados_data:
            emp, created = Employee.objects.get_or_create(
                cedula=data['cedula'],
                defaults=data
            )
            empleados[data['cedula']] = emp
            status = '✅ Creado' if created else '⚠️  Ya existe'
            self.stdout.write(f'  {status}: {emp.name}')

        # ── Nómina Q1 — 1ra Quincena Febrero 2026 ────────────────────────────
        self.stdout.write('\n📄 Cargando Q1 (01/02/2026 - 15/02/2026)...')

        q1_data = [
            {
                'cedula':            '001-020803-1058H',
                'vacation_payment':  Decimal('833.33'),
                'otras_deducciones': Decimal('0'),
                'prestamo_adelanto': Decimal('0'),
                'sub_total':         Decimal('5833.33'),
                'total':             Decimal('5833.33'),
            },
            {
                'cedula':            '001-240493-0017J',
                'vacation_payment':  Decimal('750.00'),
                'otras_deducciones': Decimal('0'),
                'prestamo_adelanto': Decimal('0'),
                'sub_total':         Decimal('5250.00'),
                'total':             Decimal('5250.00'),
            },
            {
                'cedula':            '001-090880-0081S',
                'vacation_payment':  Decimal('1083.33'),
                'otras_deducciones': Decimal('0'),
                'prestamo_adelanto': Decimal('960.00'),
                'sub_total':         Decimal('7583.33'),
                'total':             Decimal('6623.33'),
            },
            {
                'cedula':            '001-110964-0020Y',
                'vacation_payment':  Decimal('833.33'),
                'otras_deducciones': Decimal('0'),
                'prestamo_adelanto': Decimal('0'),
                'sub_total':         Decimal('5833.33'),
                'total':             Decimal('5833.33'),
            },
            {
                'cedula':            '001-030561-0050E',
                'vacation_payment':  Decimal('350.00'),
                'otras_deducciones': Decimal('0'),
                'prestamo_adelanto': Decimal('0'),
                'sub_total':         Decimal('3850.00'),
                'total':             Decimal('3850.00'),
            },
            {
                'cedula':            '001-041296-0004M',
                'vacation_payment':  Decimal('500.00'),
                'otras_deducciones': Decimal('0'),
                'prestamo_adelanto': Decimal('0'),
                'sub_total':         Decimal('3500.00'),
                'total':             Decimal('3500.00'),
            },
        ]

        for data in q1_data:
            emp = empleados[data['cedula']]
            record, created = PayrollRecord.objects.get_or_create(
                employee=emp,
                date=date(2026, 2, 1),
                period=1,
                defaults={
                    'dias_laborados':    15,
                    'salary_base':       emp.salary_base,
                    'vacation_payment':  data['vacation_payment'],
                    'viatico':           Decimal('0'),
                    'otras_deducciones': data['otras_deducciones'],
                    'prestamo_adelanto': data['prestamo_adelanto'],
                    'sub_total':         data['sub_total'],
                    'total':             data['total'],
                }
            )
            status = '✅ Creado' if created else '⚠️  Ya existe'
            self.stdout.write(f'  {status}: Q1 — {emp.name} — C${record.total}')

        # ── Nómina Q2 — 2da Quincena Febrero 2026 ────────────────────────────
        self.stdout.write('\n📄 Cargando Q2 (16/02/2026 - 28/02/2026)...')

        q2_data = [
            {
                'cedula':            '001-020803-1058H',
                'otras_deducciones': Decimal('2929.60'),
                'prestamo_adelanto': Decimal('0'),
                'sub_total':         Decimal('5000.00'),
                'total':             Decimal('2070.40'),
            },
            {
                'cedula':            '001-240493-0017J',
                'otras_deducciones': Decimal('0'),
                'prestamo_adelanto': Decimal('0'),
                'sub_total':         Decimal('4500.00'),
                'total':             Decimal('4500.00'),
            },
            {
                'cedula':            '001-090880-0081S',
                'otras_deducciones': Decimal('0'),
                'prestamo_adelanto': Decimal('0'),
                'sub_total':         Decimal('6500.00'),
                'total':             Decimal('6500.00'),
            },
            {
                'cedula':            '001-110964-0020Y',
                'otras_deducciones': Decimal('0'),
                'prestamo_adelanto': Decimal('0'),
                'sub_total':         Decimal('5000.00'),
                'total':             Decimal('5000.00'),
            },
            {
                'cedula':            '001-030561-0050E',
                'otras_deducciones': Decimal('0'),
                'prestamo_adelanto': Decimal('0'),
                'sub_total':         Decimal('3500.00'),
                'total':             Decimal('3500.00'),
            },
            {
                'cedula':            '001-041296-0004M',
                'otras_deducciones': Decimal('0'),
                'prestamo_adelanto': Decimal('0'),
                'sub_total':         Decimal('3500.00'),
                'total':             Decimal('3500.00'),
            },
        ]

        for data in q2_data:
            emp = empleados[data['cedula']]
            record, created = PayrollRecord.objects.get_or_create(
                employee=emp,
                date=date(2026, 2, 16),
                period=2,
                defaults={
                    'dias_laborados':    15,
                    'salary_base':       emp.salary_base,
                    'vacation_payment':  Decimal('0'),
                    'viatico':           Decimal('0'),
                    'otras_deducciones': data['otras_deducciones'],
                    'prestamo_adelanto': data['prestamo_adelanto'],
                    'sub_total':         data['sub_total'],
                    'total':             data['total'],
                }
            )
            status = '✅ Creado' if created else '⚠️  Ya existe'
            self.stdout.write(f'  {status}: Q2 — {emp.name} — C${record.total}')

        self.stdout.write('\n🎉 ¡Datos cargados correctamente!\n')