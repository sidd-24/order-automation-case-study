"""
Builds business_case.xlsx: the cost/benefit model for automating order entry. Every result
is an Excel formula on the Inputs sheet, so the assumptions can be changed in Excel and the
model recalculates.

    python business_case.py
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.workbook.defined_name import DefinedName

INPUT = PatternFill("solid", fgColor="FFF2CC")
HEADER = PatternFill("solid", fgColor="1F3864")

# name, label, value, format, source
INPUTS = [
    ("docs_per_day", "Order documents per working day", 120, "0", "Assumption: mid-size industrial distributor"),
    ("working_days", "Working days per year", 250, "0", "Assumption"),
    ("manual_min", "Manual entry time per document (min)", 7, "0.0", "Assumption: 5-10 min for a 3-5 line order"),
    ("auto_share", "Share of documents auto-approved", 0.45, "0%", "Assumption; 51 % in the synthetic evaluation"),
    ("review_min", "Review time for a flagged, pre-filled document (min)", 2.5, "0.0", "Assumption"),
    ("hourly_cost", "Loaded labour cost per hour (EUR)", 38, "#,##0", "Assumption: back office, incl. overhead"),
    ("fte_hours", "Productive hours per FTE per year", 1600, "#,##0", "Assumption"),
    ("llm_cost", "LLM cost per document (EUR)", 0.001, "0.000", "Measured: USD 0.0007 per document (Groq)"),
    ("run_cost_month", "Hosting, monitoring, maintenance per month (EUR)", 1500, "#,##0", "Assumption"),
    ("one_off", "One-off build and ERP integration (EUR)", 60000, "#,##0", "Assumption"),
]

RESULTS = [
    ("Documents per year", "=docs_per_day*working_days", "#,##0"),
    ("Minutes saved per year", "=docs_per_day*working_days*(auto_share*manual_min+(1-auto_share)*(manual_min-review_min))", "#,##0"),
    ("Hours saved per year", "=B3/60", "#,##0"),
    ("FTE capacity freed", "=B4/fte_hours", "0.0"),
    ("Labour savings per year (EUR)", "=B4*hourly_cost", "#,##0"),
    ("Running cost per year (EUR)", "=run_cost_month*12+B2*llm_cost", "#,##0"),
    ("Net benefit per year (EUR)", "=B6-B7", "#,##0"),
    ("Payback (months)", "=IF(B8>0,one_off/(B8/12),\"never\")", "0.0"),
    ("Net benefit over 3 years (EUR)", "=3*B8-one_off", "#,##0"),
]


def net_benefit_formula(docs: str, share: str) -> str:
    """Net yearly benefit for given documents per day and auto-approval share (cell refs)."""
    minutes = f"{docs}*working_days*({share}*manual_min+(1-{share})*(manual_min-review_min))"
    return f"={minutes}/60*hourly_cost-(run_cost_month*12+{docs}*working_days*llm_cost)"


def build(path="business_case.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Inputs"
    for c, h in enumerate(["Input", "Value", "Source"], start=1):
        ws.cell(row=1, column=c, value=h).font = Font(bold=True, color="FFFFFF")
        ws.cell(row=1, column=c).fill = HEADER
    for r, (name, label, value, fmt, source) in enumerate(INPUTS, start=2):
        ws.cell(row=r, column=1, value=label)
        cell = ws.cell(row=r, column=2, value=value)
        cell.number_format, cell.fill = fmt, INPUT
        ws.cell(row=r, column=3, value=source)
        wb.defined_names[name] = DefinedName(name, attr_text=f"Inputs!$B${r}")
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width, ws.column_dimensions["C"].width = 50, 12, 48
    ws.cell(row=len(INPUTS) + 3, column=1, value="Yellow cells are assumptions: change them and the model recalculates.").font = Font(italic=True)

    ws = wb.create_sheet("Results")
    ws["A1"], ws["A1"].font = "Business case: automated order entry", Font(bold=True, size=14)
    for r, (label, formula, fmt) in enumerate(RESULTS, start=2):
        ws.cell(row=r, column=1, value=label)
        ws.cell(row=r, column=2, value=formula).number_format = fmt
    for r in (8, 9):
        ws.cell(row=r, column=1).font = ws.cell(row=r, column=2).font = Font(bold=True)
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 36, 14

    ws = wb.create_sheet("Sensitivity")
    ws["A1"], ws["A1"].font = "Net benefit per year (EUR) by volume and auto-approval share", Font(bold=True, size=12)
    ws["A3"] = "Documents per day →  /  auto-approved ↓"
    volumes, shares = [60, 120, 240], [0.30, 0.45, 0.60]
    for c, v in enumerate(volumes, start=2):
        ws.cell(row=3, column=c, value=v).font = Font(bold=True)
    for r, s in enumerate(shares, start=4):
        ws.cell(row=r, column=1, value=s).number_format = "0%"
        ws.cell(row=r, column=1).font = Font(bold=True)
        for c in range(2, 2 + len(volumes)):
            col = chr(64 + c)
            ws.cell(row=r, column=c, value=net_benefit_formula(f"{col}$3", f"$A{r}")).number_format = "#,##0"
    ws.column_dimensions["A"].width = 38
    for col in "BCD":
        ws.column_dimensions[col].width = 12
    wb.active = 1
    wb.save(path)


if __name__ == "__main__":
    build()
    print("wrote business_case.xlsx")
