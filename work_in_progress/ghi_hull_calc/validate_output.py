"""
Validation script to compare hull calculator output with original ODS
"""

import json
import csv
import os
import sys
from pathlib import Path

# Add module path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from hull_calculator import HullCalculator


def load_json_output(filepath):
    """Load JSON output from calculator"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data.get('offsets', [])


def load_csv_output(filepath):
    """Load CSV output from calculator"""
    rows = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def print_sample_output():
    """Print sample output from calculator"""
    calc = HullCalculator()
    calc.compute()
    
    print("\n" + "="*80)
    print("HULL OFFSET CALCULATOR - SAMPLE OUTPUT")
    print("="*80)
    
    print(f"\nInputs Used: {len(calc.inputs)} parameters")
    print(f"Output Points Generated: {len(calc.outputs)}")
    
    # Convert outputs dict to list for easier processing
    output_list = [v for k, v in sorted(calc.outputs.items())]
    
    print("\nFirst 10 Offset Points:")
    print("-" * 80)
    print(f"{'Section':<10} {'X(cm)':<12} {'Y(cm)':<12} {'Z(cm)':<12}")
    print("-" * 80)
    
    for point in output_list[:10]:
        print(f"{point.get('section', 'N/A'):<10} "
              f"{float(point.get('x', 0)):<12.2f} "
              f"{float(point.get('y', 0)):<12.2f} "
              f"{float(point.get('z', 0)):<12.2f}")
    
    print("\n... (220 more points) ...\n")
    
    print("Last 10 Offset Points:")
    print("-" * 80)
    print(f"{'Section':<10} {'X(cm)':<12} {'Y(cm)':<12} {'Z(cm)':<12}")
    print("-" * 80)
    
    for point in output_list[-10:]:
        print(f"{point.get('section', 'N/A'):<10} "
              f"{float(point.get('x', 0)):<12.2f} "
              f"{float(point.get('y', 0)):<12.2f} "
              f"{float(point.get('z', 0)):<12.2f}")
    
    print("\n" + "="*80)
    print("SECTION STATISTICS")
    print("="*80)
    
    sections = {}
    for point in output_list:
        section = point.get('section', 'Unknown')
        if section not in sections:
            sections[section] = {'count': 0, 'x_values': [], 'y_range': [0, 0], 'z_range': [0, 0]}
        
        sections[section]['count'] += 1
        sections[section]['x_values'].append(float(point.get('x', 0)))
        y = float(point.get('y', 0))
        z = float(point.get('z', 0))
        
        if y > sections[section]['y_range'][1]:
            sections[section]['y_range'][1] = y
        if z < sections[section]['z_range'][0]:
            sections[section]['z_range'][0] = z
        if z > sections[section]['z_range'][1]:
            sections[section]['z_range'][1] = z
    
    print(f"\n{'Section':<10} {'Points':<8} {'X(cm)':<12} {'Y-Max(cm)':<12} {'Z-Range(cm)':<15}")
    print("-" * 80)
    
    for section in sorted(sections.keys()):
        info = sections[section]
        x_val = info['x_values'][0] if info['x_values'] else 0
        y_max = info['y_range'][1]
        z_range = f"[{info['z_range'][0]:.2f}, {info['z_range'][1]:.2f}]"
        print(f"{section:<10} {info['count']:<8} {x_val:<12.2f} {y_max:<12.2f} {z_range:<15}")
    
    print("\n" + "="*80)
    print("EXPORT OPTIONS")
    print("="*80)
    print("\nJSON files contain:")
    print("  - All 43 input parameters")
    print("  - Complete offset list (Section, X, Y, Z)")
    print("  - Summary statistics")
    
    print("\nCSV files contain:")
    print("  - Tabular format for CAD import")
    print("  - Columns: Section, X(cm), Y(cm), Z(cm)")
    print("  - Suitable for import into CAD software")
    
    # Export for validation
    json_path = os.path.join(os.path.dirname(__file__), 'offsets_output.json')
    csv_path = os.path.join(os.path.dirname(__file__), 'offsets_output.csv')
    
    calc.export_json(json_path)
    calc.export_csv(csv_path)
    
    print(f"\n✓ JSON exported to: {json_path}")
    print(f"✓ CSV exported to: {csv_path}")
    
    print("\n" + "="*80)
    print("VALIDATION CHECKLIST")
    print("="*80)
    print("\nCompare with ODS 'Offsets x,y,z' sheet (rows 9-139):")
    print("  [ ] Row 9 header matches: Section, X(cm), Y(cm), Z(cm)")
    print("  [ ] Row 10-15 values match within tolerance (±0.5 cm)")
    print("  [ ] Total row count = 130 (rows 10-139)")
    print("  [ ] Section names match: C0, C4.5, C5, C6, C6.5, C10, Cav1, Cav2")
    print("  [ ] X-values: 0.0, 360.0, 400.0, 480.0, 520.0, 800.0")
    print("  [ ] Y-values positive and decreasing toward centerline (boat symmetry)")
    print("  [ ] Z-values: negative underwater (-37 to 0) and positive above (0 to +83)")
    print("\n" + "="*80)


def validate_against_ods():
    """Validate calculator output against ODS file (if available)"""
    try:
        from odf.opendocument import load
        from odf.table import Table, TableRow, TableCell
        
        ods_path = None
        # Search for ODS file in common locations
        search_paths = [
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Documents"),
            "c:\\Users\\matteo.lenzi\\Downloads",
        ]
        
        for search_path in search_paths:
            test_path = os.path.join(search_path, "Gene-Hull Sailboat 3.4_2025 02.ods")
            if os.path.exists(test_path):
                ods_path = test_path
                break
        
        if not ods_path:
            print("\nODS file not found in common locations")
            print("To validate, place 'Gene-Hull Sailboat 3.4_2025 02.ods' in:")
            for path in search_paths:
                print(f"  - {path}")
            return
        
        print(f"\nODS file found: {ods_path}")
        print("Loading ODS data...")
        
        # This is just a placeholder - actual validation would require parsing
        # the ODS file and comparing specific cells
        print("ODS validation not yet implemented (requires large file parsing)")
        
    except ImportError:
        print("\nodf module not installed - ODS validation skipped")
    except Exception as e:
        print(f"\nODS validation error: {e}")


if __name__ == '__main__':
    print("\nHull Offset Calculator - Validation Script")
    print("=========================================\n")
    
    # Print sample output
    print_sample_output()
    
    # Try to validate against ODS
    validate_against_ods()
    
    print("\nValidation script completed.")
    print("Generated files:")
    print("  - offsets_output.json (full data + metadata)")
    print("  - offsets_output.csv (tabular format)")
    print("\nNext steps:")
    print("  1. Open CSV in spreadsheet app to visually inspect data")
    print("  2. Compare with ODS 'Offsets x,y,z' sheet (rows 9-139)")
    print("  3. Verify row counts and value ranges match")
    print("  4. Use JSON for FreeCAD import or further processing")
