"""
Extract formulas and dependencies from the Gene-Hull ODS file.
Helps understand the structure and complexity for Python replica.
"""

import sys
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P
from typing import Dict, List, Optional, Set
import re


def get_cell_ref(row: int, col: int) -> str:
    """Convert row, col to cell address (A1, B2, etc.)"""
    letters = ""
    col_idx = col
    while col_idx > 0:
        col_idx, rem = divmod(col_idx - 1, 26)
        letters = chr(65 + rem) + letters
    return f"{letters}{row}"


def get_text(cell: TableCell) -> str:
    paras = cell.getElementsByType(P)
    if not paras:
        return ""
    texts = []
    for p in paras:
        texts.append("".join([getattr(t, 'data', '') for t in p.childNodes]))
    return "\n".join(texts).strip()


def get_formula(cell: TableCell) -> Optional[str]:
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


def extract_sheet_formulas(table: Table, sheet_name: str) -> Dict[str, Dict]:
    """Extract all formulas and their references from a sheet"""
    formulas: Dict[str, Dict] = {}
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
                addr = get_cell_ref(row_idx, col_idx)
                
                formula = get_formula(cell)
                value = get_value(cell)
                text = get_text(cell)
                
                if formula or value or text:
                    entry = {
                        "value": value,
                        "text": text,
                        "formula": formula,
                    }
                    formulas[addr] = entry
    
    return formulas


def parse_odf_formula_references(formula_str: str) -> Set[str]:
    """Extract cell references from ODF formula"""
    refs = set()
    # Match [.A1], [Sheet.A1], [Sheet.$A$1], etc.
    pattern = r'\[([\w\.]+)\]'
    matches = re.findall(pattern, formula_str)
    for match in matches:
        refs.add(match)
    return refs


def main():
    if len(sys.argv) < 2:
        print("Usage: python ods_formula_extractor.py <path_to.ods>")
        sys.exit(1)
    
    ods_path = sys.argv[1]
    doc = load(ods_path)
    tables = doc.spreadsheet.getElementsByType(Table)
    
    print(f"Found {len(tables)} sheets in ODS:\n")
    
    # Get first and last sheet names
    first_table = tables[0]
    last_table = tables[-1]
    
    try:
        first_name = first_table.getAttribute("name") or "PrimoFoglio"
    except Exception:
        first_name = "PrimoFoglio"
    
    try:
        last_name = last_table.getAttribute("name") or "UltimoFoglio"
    except Exception:
        last_name = "UltimoFoglio"
    
    print(f"First sheet: {first_name}")
    print(f"Last sheet: {last_name}\n")
    
    # Extract formulas from last sheet
    print(f"\n=== FORMULAS IN '{last_name}' ===\n")
    last_formulas = extract_sheet_formulas(last_table, last_name)
    
    formula_count = 0
    function_types: Dict[str, int] = {}
    cells_with_formulas: List[str] = []
    
    for addr, info in sorted(last_formulas.items()):
        if info.get("formula"):
            formula_count += 1
            cells_with_formulas.append(addr)
            formula_str = info["formula"]
            
            # Detect main function
            main_func = "UNKNOWN"
            if "SUM" in formula_str:
                main_func = "SUM"
            elif "AVERAGE" in formula_str:
                main_func = "AVERAGE"
            elif "IF" in formula_str:
                main_func = "IF"
            elif "+" in formula_str or "-" in formula_str:
                main_func = "ARITHMETIC"
            elif "*" in formula_str or "/" in formula_str:
                main_func = "MULTIPLY/DIVIDE"
            else:
                main_func = "OTHER"
            
            function_types[main_func] = function_types.get(main_func, 0) + 1
            
            if formula_count <= 50:  # Print first 50 formulas
                refs = parse_odf_formula_references(formula_str)
                print(f"{addr}: {formula_str[:120]}")
                if refs:
                    print(f"  References: {', '.join(sorted(refs)[:5])}")
                print()
    
    print(f"\n=== SUMMARY ===")
    print(f"Total cells with formulas: {formula_count}")
    print(f"Formula types detected: {function_types}")
    print(f"First 10 cells with formulas: {cells_with_formulas[:10]}")
    print(f"\nTo replicate this ODS in Python, you'll need to:")
    print("1. Implement parsing for each formula type above")
    print("2. Build a dependency graph to compute in correct order")
    print("3. Handle array formulas and cross-sheet references")


if __name__ == "__main__":
    main()
