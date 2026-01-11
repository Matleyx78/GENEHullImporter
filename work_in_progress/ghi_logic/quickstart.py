#!/usr/bin/env python
"""
Quick start script for GeneHull ODS replica.
Usage: python quickstart.py <path_to_ods> [output_file]
"""

import sys
import json
from ghi_logic import GeneHullCalculator


def main():
    if len(sys.argv) < 2:
        print("Usage: python quickstart.py <path_to_ods> [output_json]")
        print("\nExample:")
        print('  python quickstart.py "Gene-Hull Sailboat 3.4_2025 02.ods" results.json')
        sys.exit(1)
    
    ods_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "offsets.json"
    
    print(f"Loading ODS: {ods_path}")
    calc = GeneHullCalculator(ods_path)
    
    print(f"Sheets found: {list(calc.reader.sheets.keys())}")
    print("Computing offsets...")
    
    offsets = calc.compute_offsets()
    
    # Count statistics
    direct_count = sum(1 for v in offsets.values() if v.get("status") == "direct")
    computed_count = sum(1 for v in offsets.values() if v.get("status") == "computed")
    unresolved_count = sum(1 for v in offsets.values() if v.get("status") == "unresolved")
    
    print(f"\nResults:")
    print(f"  Total cells: {len(offsets)}")
    print(f"  Direct values: {direct_count}")
    print(f"  Computed: {computed_count}")
    print(f"  Unresolved: {unresolved_count}")
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(offsets, f, indent=2, default=str)
    
    print(f"\nExported to: {output_file}")
    
    # Show some examples
    print("\nFirst 10 computed cells:")
    count = 0
    for addr, data in sorted(offsets.items()):
        if data.get("status") == "computed" and count < 10:
            print(f"  {addr}: value={data['value']}, formula={data['formula'][:60]}")
            count += 1


if __name__ == "__main__":
    main()
