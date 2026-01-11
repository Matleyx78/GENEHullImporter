"""
Gene-Hull ODS Replica - Core Module
Reads Gene-Hull ODS and replicates calculations for "Offsets x,y,z" sheet.
"""

from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P
from typing import Dict, Optional, Tuple, Any
import re
import json


class GeneHullODSReader:
    """Read and extract data from Gene-Hull ODS"""
    
    def __init__(self, ods_path: str):
        self.ods_path = ods_path
        self.doc = load(ods_path)
        self.sheets: Dict[str, Dict[str, Dict]] = {}
        self._load_all_sheets()
    
    def _get_cell_ref(self, row: int, col: int) -> str:
        """Convert row, col to cell address"""
        letters = ""
        col_idx = col
        while col_idx > 0:
            col_idx, rem = divmod(col_idx - 1, 26)
            letters = chr(65 + rem) + letters
        return f"{letters}{row}"
    
    def _get_text(self, cell: TableCell) -> str:
        paras = cell.getElementsByType(P)
        if not paras:
            return ""
        texts = []
        for p in paras:
            texts.append("".join([getattr(t, 'data', '') for t in p.childNodes]))
        return "\n".join(texts).strip()
    
    def _get_formula(self, cell: TableCell) -> Optional[str]:
        try:
            return cell.getAttribute("formula")
        except Exception:
            return None
    
    def _get_value(self, cell: TableCell) -> Optional[Any]:
        try:
            val = cell.getAttribute("value")
            if val is not None:
                try:
                    return float(val)
                except ValueError:
                    return val
        except Exception:
            pass
        txt = self._get_text(cell)
        return txt if txt else None
    
    def _load_all_sheets(self):
        """Load all sheets from ODS"""
        tables = self.doc.spreadsheet.getElementsByType(Table)
        for table in tables:
            try:
                sheet_name = table.getAttribute("name") or "Sheet"
            except Exception:
                sheet_name = "Sheet"
            
            sheet_data = self._load_sheet(table)
            self.sheets[sheet_name] = sheet_data
    
    def _load_sheet(self, table: Table) -> Dict[str, Dict]:
        """Load single sheet data"""
        sheet_map: Dict[str, Dict] = {}
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
                    addr = self._get_cell_ref(row_idx, col_idx)
                    
                    formula = self._get_formula(cell)
                    value = self._get_value(cell)
                    text = self._get_text(cell)
                    
                    if formula or value is not None or text:
                        entry = {
                            "value": value,
                            "text": text,
                            "formula": formula,
                        }
                        sheet_map[addr] = entry
        
        return sheet_map
    
    def get_sheet(self, sheet_name: str) -> Dict[str, Dict]:
        return self.sheets.get(sheet_name, {})
    
    def get_cell(self, sheet_name: str, cell_addr: str) -> Optional[Any]:
        """Get value or formula of a cell"""
        sheet = self.get_sheet(sheet_name)
        if cell_addr in sheet:
            return sheet[cell_addr].get("value")
        return None
    
    def get_formula(self, sheet_name: str, cell_addr: str) -> Optional[str]:
        """Get formula of a cell"""
        sheet = self.get_sheet(sheet_name)
        if cell_addr in sheet:
            return sheet[cell_addr].get("formula")
        return None


class FormulaParser:
    """Parse and evaluate ODF formulas"""
    
    # Regex to extract cell references: [Sheet.A1], [.A1], [Sheet.$A$1]
    REF_PATTERN = re.compile(r"\[(['\"]?[\w\s-]+['\"]?\.)?([A-Z]+)(\$?)(\d+)\]")
    
    @staticmethod
    def parse_cell_reference(ref_str: str) -> Tuple[Optional[str], str]:
        """
        Parse reference string like:
        - 'Gene-Hull'.B715 -> ('Gene-Hull', 'B715')
        - .A1 -> (None, 'A1')
        """
        # Remove quotes if present
        ref_str = ref_str.strip().strip("'\"")
        
        if '.' in ref_str:
            parts = ref_str.rsplit('.', 1)  # Split from right to handle sheet names with dots
            if len(parts) == 2:
                sheet, cell = parts
                sheet = sheet.strip("'\"")
                return (sheet, cell)
        
        return (None, ref_str)
    
    @staticmethod
    def extract_references(formula_str: str) -> list:
        """Extract all cell references from an ODF formula"""
        refs = re.findall(r"\[([^\]]+)\]", formula_str)
        return refs
    
    @staticmethod
    def evaluate_arithmetic(expr: str, context: Dict[str, Any]) -> Optional[float]:
        """
        Safely evaluate arithmetic expressions with variable substitution.
        E.g., "A1+B2*C3" becomes "10+20*30"
        """
        try:
            # This is simplified; real production code should use a proper expression evaluator
            result = eval(expr, {"__builtins__": {}}, context)
            return float(result)
        except Exception as e:
            return None


class GeneHullCalculator:
    """Main calculator for Gene-Hull replica"""
    
    def __init__(self, ods_path: str):
        self.reader = GeneHullODSReader(ods_path)
        self.cache: Dict[str, Any] = {}
    
    def compute_offsets(self) -> Dict[str, Dict]:
        """
        Compute all offsets from input sheet and formulas.
        Returns computed sheet data for "Offsets x,y,z".
        """
        input_sheet = self.reader.get_sheet("Gene-Hull")
        output_sheet = self.reader.get_sheet("Offsets x,y,z")
        
        results = {}
        
        # For each cell in output sheet
        for cell_addr, cell_data in sorted(output_sheet.items()):
            formula = cell_data.get("formula")
            value = cell_data.get("value")
            
            if formula:
                # Parse and resolve formula
                computed_value = self._resolve_formula(formula, input_sheet)
                results[cell_addr] = {
                    "value": computed_value,
                    "formula": formula,
                    "status": "computed" if computed_value is not None else "unresolved"
                }
            else:
                results[cell_addr] = {
                    "value": value,
                    "status": "direct"
                }
        
        return results
    
    def _resolve_formula(self, formula_str: str, input_sheet: Dict) -> Optional[Any]:
        """Resolve an ODF formula to a value"""
        if not formula_str:
            return None
        
        # Remove "of:=" prefix
        formula_str = formula_str.replace("of:=", "").strip()
        
        # Extract all references
        refs = FormulaParser.extract_references(formula_str)
        
        # Build context dict with cell values
        context = {}
        resolved_formula = formula_str
        
        for ref in refs:
            sheet_name, cell_addr = FormulaParser.parse_cell_reference(ref)
            
            if sheet_name is None:
                sheet_name = "Gene-Hull"  # Default to input sheet
            
            # Get value from input sheet
            if sheet_name in self.reader.sheets:
                sheet = self.reader.sheets[sheet_name]
                if cell_addr in sheet:
                    cell_value = sheet[cell_addr].get("value")
                    if cell_value is not None:
                        context[f"'{ref}'"] = cell_value
                        resolved_formula = resolved_formula.replace(f"[{ref}]", str(cell_value))
        
        # Try to evaluate
        try:
            if resolved_formula.replace(" ", "").replace("+", "").replace("-", "").replace("*", "").replace("/", "").replace(".", "").replace("-", "").isdigit():
                return float(resolved_formula)
            else:
                result = eval(resolved_formula, {"__builtins__": {}})
                return float(result) if isinstance(result, (int, float)) else result
        except Exception:
            return None
    
    def export_offsets(self, output_file: str, format_type: str = "json"):
        """
        Export computed offsets to file (JSON or CSV).
        """
        offsets = self.compute_offsets()
        
        if format_type == "json":
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(offsets, f, indent=2, default=str)
        elif format_type == "csv":
            import csv
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Cell", "Value", "Formula", "Status"])
                for addr, data in sorted(offsets.items()):
                    writer.writerow([addr, data.get("value", ""), data.get("formula", ""), data.get("status", "")])


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gene_hull_calculator.py <ods_path> [output_json]")
        sys.exit(1)
    
    ods_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "offsets_computed.json"
    
    calc = GeneHullCalculator(ods_path)
    calc.export_offsets(output_file, format_type="json")
    print(f"Offsets exported to {output_file}")
