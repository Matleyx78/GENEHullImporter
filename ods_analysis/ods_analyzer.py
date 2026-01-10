import sys
import re
import os
from typing import Dict, List, Tuple, Optional

# Lazy imports to allow running without optional deps
try:
    from odf.opendocument import load
    from odf.table import Table, TableRow, TableCell
    from odf.text import P
except Exception:
    load = None  # type: ignore

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


def col_to_letter(col_idx: int) -> str:
    letters = ""
    while col_idx > 0:
        col_idx, rem = divmod(col_idx - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def cell_address(row_idx: int, col_idx: int) -> str:
    return f"{col_to_letter(col_idx)}{row_idx}"


def get_text(cell: TableCell) -> str:
    paras = cell.getElementsByType(P)
    if not paras:
        return ""
    texts = []
    for p in paras:
        texts.append("".join([getattr(t, 'data', '') for t in p.childNodes]))
    return "\n".join(texts).strip()


def get_formula(cell: TableCell) -> Optional[str]:
    # ODF formula attribute 'formula' (e.g., of:=SUM([.A1];[.B1]))
    try:
        return cell.getAttribute("formula")
    except Exception:
        return None


def get_value(cell: TableCell) -> Optional[str]:
    try:
        val = cell.getAttribute("value")
    except Exception:
        val = None
    if val is not None:
        return val
    txt = get_text(cell)
    return txt if txt else None


def read_sheet(table: Table) -> Dict[str, Dict[str, Optional[str]]]:
    sheet_map: Dict[str, Dict[str, Optional[str]]] = {}
    row_idx = 0
    for row in table.getElementsByType(TableRow):
        row_idx += 1
        col_idx = 0
        for cell in row.getElementsByType(TableCell):
            try:
                repeat_attr = cell.getAttribute("numbercolumnsrepeated")
            except Exception:
                repeat_attr = None
            repeat = int(repeat_attr or "1")
            for _ in range(repeat):
                col_idx += 1
                addr = cell_address(row_idx, col_idx)
                sheet_map[addr] = {
                    "text": get_text(cell),
                    "value": get_value(cell),
                    "formula": get_formula(cell),
                }
    return sheet_map


def parse_references(odf_formula: str) -> List[str]:
    # Extract references inside [...] blocks; returns raw refs, e.g. '.A1', 'Sheet.A1'
    refs = re.findall(r"\[(.*?)\]", odf_formula)
    return refs


def normalize_ref(ref: str, default_sheet: str) -> Tuple[str, str]:
    # ref could be '.A1' or 'Sheet.A1' or 'Sheet.$B$2'
    # Remove leading dot indicating current sheet
    ref = ref.strip()
    sheet = default_sheet
    if ref.startswith('.'):
        addr = ref[1:]
    else:
        parts = ref.split('.')
        if len(parts) == 2:
            sheet, addr = parts[0], parts[1]
        else:
            addr = ref
    # remove $ anchors
    addr = addr.replace('$', '')
    return sheet, addr


def summarize_inputs(sheet_map: Dict[str, Dict[str, Optional[str]]]) -> List[Tuple[str, Optional[str]]]:
    inputs: List[Tuple[str, Optional[str]]] = []
    for addr, info in sheet_map.items():
        if not info.get("formula"):
            val = info.get("value")
            txt = info.get("text")
            if val and val != txt:  # numeric or explicit value
                inputs.append((addr, val))
            elif txt and txt.strip():
                # treat textual cell as potential label (value may be in right neighbor)
                inputs.append((addr, txt.strip()))
    return inputs


def summarize_outputs(sheet_name: str, sheet_map: Dict[str, Dict[str, Optional[str]]]) -> List[Dict[str, object]]:
    outputs: List[Dict[str, object]] = []
    for addr, info in sheet_map.items():
        val = info.get("value")
        formula = info.get("formula")
        if val or formula:
            entry: Dict[str, object] = {
                "sheet": sheet_name,
                "addr": addr,
                "value": val,
                "formula": formula,
                "refs": [],
            }
            if formula:
                entry["refs"] = [normalize_ref(r, sheet_name) for r in parse_references(formula)]
            outputs.append(entry)
    return outputs


def generate_pdf(report_path: str, title: str, inputs: List[Tuple[str, Optional[str]]], outputs: List[Dict[str, object]]):
    c = canvas.Canvas(report_path, pagesize=A4)
    width, height = A4
    x_margin, y_margin = 2 * cm, 2 * cm
    y = height - y_margin

    def writeln(text: str, size: int = 10, leading: int = 14):
        nonlocal y
        if y < y_margin:
            c.showPage()
            y = height - y_margin
        c.setFont("Helvetica", size)
        c.drawString(x_margin, y, text)
        y -= leading

    writeln(title, size=14, leading=18)
    writeln("", leading=8)

    writeln("Sezione Input (primo foglio)", size=12, leading=16)
    for addr, val in inputs[:500]:  # limit to avoid huge PDFs
        writeln(f"- {addr}: {val}")

    writeln("", leading=12)
    writeln("Sezione Output (ultimo foglio)", size=12, leading=16)
    for out in outputs[:500]:
        val = out.get("value") or ""
        formula = out.get("formula") or ""
        writeln(f"- {out['sheet']}.{out['addr']} = {val}")
        if formula:
            writeln(f"  formula: {formula}")
            refs = out.get("refs") or []
            if refs:
                writeln("  riferimenti:")
                for sh, a in refs[:20]:
                    writeln(f"    - {sh}.{a}")
    c.save()


def generate_text(report_path: str, title: str, inputs: List[Tuple[str, Optional[str]]], outputs: List[Dict[str, object]]):
    lines: List[str] = []
    lines.append(title)
    lines.append("")
    lines.append("Sezione Input (primo foglio)")
    lines.append("--------------------------------")
    for addr, val in inputs:
        lines.append(f"{addr}: {val}")
    lines.append("")
    lines.append("Sezione Output (ultimo foglio)")
    lines.append("--------------------------------")
    for out in outputs:
        val = out.get("value") or ""
        formula = out.get("formula") or ""
        lines.append(f"{out['sheet']}.{out['addr']} = {val}")
        if formula:
            lines.append(f"  Formula ODF: {formula}")
            refs = out.get("refs") or []
            if refs:
                lines.append("  Riferimenti risolti:")
                for sh, a in refs:
                    lines.append(f"    - {sh}.{a}")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    if load is None:
        print("Errore: libreria odfpy non disponibile. Installa con 'pip install odfpy'.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Uso: python ods_analyzer.py <percorso_file.ods> [--txt <percorso_report.txt>] [--pdf <percorso_report.pdf>]")
        sys.exit(1)

    ods_path = sys.argv[1]
    pdf_path: Optional[str] = None
    txt_path: Optional[str] = None
    if "--pdf" in sys.argv:
        idx = sys.argv.index("--pdf")
        if idx + 1 < len(sys.argv):
            pdf_path = sys.argv[idx + 1]
    if "--txt" in sys.argv:
        idx = sys.argv.index("--txt")
        if idx + 1 < len(sys.argv):
            txt_path = sys.argv[idx + 1]

    doc = load(ods_path)
    tables = doc.spreadsheet.getElementsByType(Table)
    print(f"Trovati {len(tables)} fogli nel file ODS.")
    if not tables:
        print("Nessun foglio trovato nel file ODS.")
        sys.exit(1)

    first_table = tables[0]
    last_table = tables[-1]
    first_name = first_table.getAttribute("name") or "PrimoFoglio"
    last_name = last_table.getAttribute("name") or "UltimoFoglio"
    print(f"Primo foglio: {first_name} | Ultimo foglio: {last_name}")

    first_map = read_sheet(first_table)
    last_map = read_sheet(last_table)

    inputs = summarize_inputs(first_map)
    outputs = summarize_outputs(last_name, last_map)

    title = f"Analisi ODS: input '{first_name}', output '{last_name}'"
    # Priorità TXT, altrimenti PDF se richiesto e disponibile, altrimenti TXT di default
    if txt_path:
        generate_text(txt_path, title, inputs, outputs)
        print(f"Report TXT generato: {txt_path}")
    elif pdf_path and REPORTLAB_AVAILABLE:
        generate_pdf(pdf_path, title, inputs, outputs)
        print(f"Report PDF generato: {pdf_path}")
    else:
        txt_default = os.path.join(os.path.dirname(__file__), "analysis_report.txt")
        generate_text(txt_default, title, inputs, outputs)
        print(f"Report TXT generato: {txt_default}")
        if pdf_path and not REPORTLAB_AVAILABLE:
            print("Reportlab non disponibile: generato TXT al posto del PDF.")

if __name__ == "__main__":
    main()
