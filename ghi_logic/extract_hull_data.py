"""
Extract hull input parameters (rows 11-58) and output formulas (rows 9-139)
from Gene-Hull ODS to create schema and formula mapping.
"""

from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P
from typing import Dict, Optional, List
import json
import re


def get_cell_ref(row: int, col: int) -> str:
    """Convert row, col to cell address"""
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


def get_value(cell: TableCell) -> Optional[str]:
    try:
        val = cell.getAttribute("value")
        if val is not None:
            return val
    except Exception:
        pass
    return get_text(cell)


def get_formula(cell: TableCell) -> Optional[str]:
    try:
        return cell.getAttribute("formula")
    except Exception:
        return None


def extract_sheet_rows(ods_path: str, sheet_name: str, start_row: int, end_row: int) -> Dict[int, Dict[str, dict]]:
    """Extract rows from a sheet"""
    doc = load(ods_path)
    tables = doc.spreadsheet.getElementsByType(Table)
    
    sheet = None
    for table in tables:
        try:
            name = table.getAttribute("name")
        except Exception:
            name = ""
        if name == sheet_name:
            sheet = table
            break
    
    if not sheet:
        raise ValueError(f"Sheet '{sheet_name}' not found")
    
    rows_data: Dict[int, Dict[str, dict]] = {}
    row_idx = 0
    
    for row in sheet.getElementsByType(TableRow):
        row_idx += 1
        if row_idx < start_row or row_idx > end_row:
            continue
        
        row_cells = {}
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
                
                row_cells[addr] = {
                    "col": col_idx,
                    "text": text,
                    "value": value,
                    "formula": formula
                }
        
        rows_data[row_idx] = row_cells
    
    return rows_data


def extract_inputs(ods_path: str) -> Dict[str, dict]:
    """Extract input parameters from Gene-Hull rows 11-58"""
    print("Extracting inputs from Gene-Hull rows 11-58...")
    rows = extract_sheet_rows(ods_path, "Gene-Hull", 11, 58)
    
    inputs = {}
    
    for row_idx, row_cells in sorted(rows.items()):
        # Typically: A = param name, B = value, D = type, G = comment
        a_cell = row_cells.get("A1", {})  # Reset for each row
        
        # Find parameter name (usually in columns A or B)
        param_label = row_cells.get("A" + str(row_idx), {}).get("text", "").strip() or \
                      row_cells.get("B" + str(row_idx), {}).get("text", "").strip()
        
        # Find value (usually in column B or nearby)
        param_value = None
        for col_letter in ['B', 'C', 'D']:
            cell_key = col_letter + str(row_idx)
            if cell_key in row_cells:
                val = row_cells[cell_key].get("value")
                if val and val not in ["", "<<", ">>", "<", ">"]:
                    try:
                        param_value = float(val)
                    except (ValueError, TypeError):
                        param_value = val
                    if param_value:
                        break
        
        # Find comment (usually in column G)
        comment = row_cells.get("G" + str(row_idx), {}).get("text", "").strip()
        
        if param_label:
            inputs[param_label] = {
                "row": row_idx,
                "value": param_value,
                "comment": comment,
                "cells": row_cells
            }
    
    return inputs


def extract_formulas(ods_path: str) -> Dict[str, dict]:
    """Extract formulas from Offsets x,y,z rows 9-139"""
    print("Extracting formulas from Offsets x,y,z rows 9-139...")
    rows = extract_sheet_rows(ods_path, "Offsets x,y,z", 9, 139)
    
    formulas = {}
    
    for row_idx, row_cells in sorted(rows.items()):
        for addr, cell_data in row_cells.items():
            formula = cell_data.get("formula")
            value = cell_data.get("value")
            
            if formula or value:
                formulas[addr] = {
                    "row": row_idx,
                    "formula": formula,
                    "value": value,
                    "text": cell_data.get("text", "")
                }
    
    return formulas


def main():
    ods_path = "ghi_utils/Gene-Hull Sailboat 3.4_2025 02.ods"
    
    # Extract inputs
    inputs = extract_inputs(ods_path)
    print(f"\nFound {len(inputs)} input parameters:")
    for name, data in sorted(inputs.items())[:10]:
        print(f"  {name}: {data['value']} - {data['comment'][:50]}")
    
    # Extract formulas
    formulas = extract_formulas(ods_path)
    print(f"\nFound {len(formulas)} cells with formulas/values")
    
    # Save schema
    schema = {
        "inputs": {name: {"value": data["value"], "comment": data["comment"], "row": data["row"]} 
                   for name, data in inputs.items()},
        "outputs": {addr: {"row": data["row"], "formula": data["formula"]} 
                    for addr, data in formulas.items()}
    }
    
    with open("ghi_hull_calc/input_schema.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print("\nSchema saved to ghi_hull_calc/input_schema.json")
    
    # Save raw formula mappings
    with open("ghi_hull_calc/formula_mappings.json", "w", encoding="utf-8") as f:
        json.dump(formulas, f, indent=2, ensure_ascii=False, default=str)
    
    print("Formulas saved to ghi_hull_calc/formula_mappings.json")


if __name__ == "__main__":
    main()
