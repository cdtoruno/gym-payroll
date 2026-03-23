"""
Genera el Excel de planilla de nómina con:
- Hoja general (todos los empleados)
- Una hoja por empleado
"""
import calendar
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

MESES = [
    "", "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

THIN  = Side(style="thin")
THICK = Side(style="medium")


def all_borders(thick=False):
    s = THICK if thick else THIN
    return Border(top=s, bottom=s, left=s, right=s)


HEADER_FILL  = PatternFill("solid", start_color="1F4E79", end_color="1F4E79")
SUBHEAD_FILL = PatternFill("solid", start_color="2E75B6", end_color="2E75B6")
WHITE_FILL   = PatternFill("solid", start_color="FFFFFF", end_color="FFFFFF")
ALT_FILL     = PatternFill("solid", start_color="EBF3FB", end_color="EBF3FB")
TOTAL_FILL   = PatternFill("solid", start_color="FFF2CC", end_color="FFF2CC")
FIRMA_FILL   = PatternFill("solid", start_color="F9F9F9", end_color="F9F9F9")

CURRENCY_FMT = '"C$"#,##0.00'


def title_for_period(period, month, year):
    mes = MESES[month]
    if period == 1:
        label    = "1ra. Quincena"
        date_str = f"01/{month:02d}/{year} al 15/{month:02d}/{year}"
    else:
        last_day = calendar.monthrange(year, month)[1]
        label    = "2da. Quincena"
        date_str = f"16/{month:02d}/{year} al {last_day:02d}/{month:02d}/{year}"
    return f"Planilla {label} de {mes} del ({date_str})"


def build_sheet(ws, records, period, month, year):
    title = title_for_period(period, month, year)

    # ── Fila 1: nombre empresa ────────────────────────────────────────────────
    ws.merge_cells("A1:M1")
    ws["A1"] = "GYM DADO"
    ws["A1"].font      = Font(name="Arial", size=16, bold=True, color="FFFFFF")
    ws["A1"].fill      = HEADER_FILL
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    # ── Fila 2: título de período ─────────────────────────────────────────────
    ws.merge_cells("A2:M2")
    ws["A2"] = title
    ws["A2"].font      = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    ws["A2"].fill      = SUBHEAD_FILL
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 22

    # ── Fila 3: espaciador ────────────────────────────────────────────────────
    ws.append([])
    ws.row_dimensions[3].height = 6

    # ── Fila 4: encabezados de grupo ──────────────────────────────────────────
    ws.merge_cells("F4:G4")
    ws["F4"] = "SALARIO"
    ws["F4"].font      = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    ws["F4"].fill      = HEADER_FILL
    ws["F4"].alignment = Alignment(horizontal="center", vertical="center")
    ws["F4"].border    = all_borders(thick=True)

    ws.merge_cells("I4:K4")
    ws["I4"] = "Deducciones"
    ws["I4"].font      = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    ws["I4"].fill      = HEADER_FILL
    ws["I4"].alignment = Alignment(horizontal="center", vertical="center")
    ws["I4"].border    = all_borders(thick=True)
    ws.row_dimensions[4].height = 18

    # ── Fila 5: encabezados de columna ────────────────────────────────────────
    headers = [
        "No.",
        "Nombres y Apellidos",
        "Cargo",
        "Días\nLaborados",
        "Cédula",
        "Salario\nOrdinario",
        "Vacaciones",
        "Sub-Total\nDevengado",
        "Otras\nDeducciones",
        "Préstamo /\nAdelanto",
        "Desc.\nTardanzas",
        "Total\nDevengado",
        "Firma",
    ]
    ws.append(headers)
    for cell in ws[5]:
        cell.font      = Font(name="Arial", size=9, bold=True, color="FFFFFF")
        cell.fill      = SUBHEAD_FILL
        cell.alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )
        cell.border = all_borders()
    ws.row_dimensions[5].height = 32

    # ── Filas de datos ────────────────────────────────────────────────────────
    for idx, r in enumerate(records, start=1):
        fill = ALT_FILL if idx % 2 == 0 else WHITE_FILL
        row  = [
            idx,
            r["employee_name"],
            r["employee_position"],
            r["dias_laborados"],
            r["employee_cedula"],
            r["salary_base"],
            r["vacation_payment"],
            r["sub_total"],
            r["otras_deducciones"],
            r["prestamo_adelanto"],
            r.get("descuento_tardanzas", 0),
            r["total"],
            "",  # Firma
        ]
        ws.append(row)
        data_row = ws[5 + idx]

        for ci, cell in enumerate(data_row, start=1):
            cell.font   = Font(name="Arial", size=9)
            cell.fill   = fill
            cell.border = all_borders()
            cell.alignment = Alignment(
                horizontal="center" if ci in (1, 4) else "left",
                vertical="center"
            )

        # Formato moneda para columnas numéricas
        for col_idx in (6, 7, 8, 9, 10, 11, 12):
            data_row[col_idx - 1].number_format = CURRENCY_FMT
            data_row[col_idx - 1].alignment     = Alignment(
                horizontal="right", vertical="center"
            )

        # Celda firma
        data_row[12].fill      = FIRMA_FILL
        data_row[12].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[5 + idx].height = 22

    # ── Fila de totales ───────────────────────────────────────────────────────
    total_row_num = 5 + len(records) + 1
    ws.append([])

    ws.merge_cells(
        start_row=total_row_num, start_column=1,
        end_row=total_row_num,   end_column=5
    )
    ws.cell(total_row_num, 1).value     = "TOTAL"
    ws.cell(total_row_num, 1).font      = Font(name="Arial", size=9, bold=True)
    ws.cell(total_row_num, 1).fill      = TOTAL_FILL
    ws.cell(total_row_num, 1).border    = all_borders(thick=True)
    ws.cell(total_row_num, 1).alignment = Alignment(
        horizontal="center", vertical="center"
    )

    n = len(records)
    for col_idx, col_letter in [
        (6, "F"), (7, "G"), (8, "H"),
        (9, "I"), (10, "J"), (11, "K"), (12, "L")
    ]:
        cell = ws.cell(total_row_num, col_idx)
        cell.value         = f"=SUM({col_letter}6:{col_letter}{5 + n})"
        cell.number_format = CURRENCY_FMT
        cell.font          = Font(name="Arial", size=9, bold=True)
        cell.fill          = TOTAL_FILL
        cell.border        = all_borders(thick=True)
        cell.alignment     = Alignment(horizontal="right", vertical="center")

    ws.row_dimensions[total_row_num].height = 22

    # ── Anchos de columna ─────────────────────────────────────────────────────
    widths = [5, 32, 16, 8, 22, 14, 14, 14, 14, 14, 12, 14, 18]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # ── Configuración de impresión ────────────────────────────────────────────
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToPage   = True
    ws.page_setup.fitToWidth  = 1
    ws.page_setup.fitToHeight = 0
    ws.print_title_rows       = "1:5"


def generate_payroll_excel(records_data, period, month, year):
    """
    Genera el workbook completo.
    - Hoja 'General': todos los empleados
    - Una hoja por empleado
    """
    wb = Workbook()

    # Hoja general
    ws_general       = wb.active
    ws_general.title = "General"
    build_sheet(ws_general, records_data, period, month, year)

    # Hoja individual por empleado
    for r in records_data:
        parts      = r["employee_name"].split()
        sheet_name = " ".join(parts[:2])[:31]
        ws = wb.create_sheet(title=sheet_name)
        build_sheet(ws, [r], period, month, year)

    return wb