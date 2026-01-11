"""
Extract hull input parameters (rows 11-58) from Gene-Hull ODS.
Uses simple, robust extraction to avoid odfpy parsing issues.
"""

import sys
import json
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P


def get_text(cell):
    paras = cell.getElementsByType(P)
    if not paras:
        return ""
    texts = []
    for p in paras:
        for t in p.childNodes:
            if hasattr(t, 'data'):
                texts.append(t.data)
    return "".join(texts).strip()


def get_value(cell):
    try:
        val = cell.getAttribute("value")
        if val:
            try:
                return float(val)
            except ValueError:
                return val
    except:
        pass
    txt = get_text(cell)
    try:
        return float(txt) if txt else None
    except ValueError:
        return txt if txt else None


def get_sheet_data(ods_path, sheet_name):
    """Get raw sheet data without complex parsing"""
    try:
        doc = load(ods_path)
    except Exception as e:
        print(f"Error loading ODS: {e}")
        return None
    
    tables = doc.spreadsheet.getElementsByType(Table)
    for table in tables:
        try:
            name = table.getAttribute("name")
        except:
            name = ""
        
        if name == sheet_name:
            return table
    
    return None


def extract_inputs(ods_path):
    """Extract inputs from Gene-Hull rows 11-58 (columns A-G)"""
    print("Extracting inputs from Gene-Hull...")
    sheet = get_sheet_data(ods_path, "Gene-Hull")
    if not sheet:
        print("Error: Gene-Hull sheet not found")
        return {}
    
    inputs = {}
    row_idx = 0
    
    for row in sheet.getElementsByType(TableRow):
        row_idx += 1
        if row_idx < 11 or row_idx > 58:
            continue
        
        cells = []
        col_idx = 0
        for cell in row.getElementsByType(TableCell):
            try:
                repeat = int(cell.getAttribute("numbercolumnsrepeated") or "1")
            except:
                repeat = 1
            
            for _ in range(repeat):
                col_idx += 1
                value = get_value(cell)
                text = get_text(cell)
                cells.append((col_idx, text, value))
        
        # Parse: A=label, B=value, D=type, G=comment
        if cells:
            label = ""
            value = None
            param_type = ""
            comment = ""
            
            for col, txt, val in cells:
                if col == 1:  # Column A
                    label = txt
                elif col == 2 and not label:  # Column B (fallback)
                    label = txt
                elif col == 2:  # Column B (value)
                    if val is not None:
                        value = val
                    elif txt and txt not in ["<", ">", "<<", ">>"]:
                        value = txt
                elif col == 4:  # Column D
                    param_type = txt
                elif col == 7:  # Column G
                    comment = txt
            
            if label and label not in ["", "Data to enter", "<<< User space >>>"]:
                inputs[label] = {
                    "row": row_idx,
                    "value": value,
                    "type": param_type,
                    "comment": comment
                }
    
    return inputs


def main():
    ods_path = "ghi_utils/Gene-Hull Sailboat 3.4_2025 02.ods"
    
    inputs = extract_inputs(ods_path)
    print(f"\nExtracted {len(inputs)} inputs:")
    for name, data in sorted(inputs.items())[:15]:
        print(f"  {name}: {data['value']} ({data['type']})")
    
    # Save schema
    schema = {
        "inputs": inputs,
        "description": "Hull parameters from Gene-Hull ODS rows 11-58"
    }
    
    with open("ghi_hull_calc/input_schema.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print(f"\nSchema saved to ghi_hull_calc/input_schema.json")


if __name__ == "__main__":
    main()
