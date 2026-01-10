"""
EXAMPLE USAGE: Hull Offset Calculator

This file demonstrates how to use the Hull Offset Calculator
in different scenarios.
"""

# ============================================================================
# EXAMPLE 1: Using HullCalculator Directly in Python
# ============================================================================

def example1_standalone_calculator():
    """
    Use the calculator without FreeCAD.
    Useful for batch processing or automation.
    """
    import sys
    import os
    from ghi_hull_calc.hull_calculator import HullCalculator, load_input_schema
    
    # Load input schema
    schema_path = "ghi_hull_calc/input_schema.json"
    schema = load_input_schema(schema_path)
    
    # Extract default inputs
    inputs = {key: data.get("value", 0) for key, data in schema.items()}
    
    # Create calculator and compute
    calc = HullCalculator()
    calc.set_inputs(inputs)
    calc.compute()
    
    # Export results
    calc.export_json("my_hull_design.json")
    calc.export_csv("my_hull_design.csv")
    
    print(f"Generated {len(calc.outputs)} offset points")


# ============================================================================
# EXAMPLE 2: Custom Hull Design
# ============================================================================

def example2_custom_design():
    """
    Create a custom hull design with modified parameters.
    """
    from ghi_hull_calc.hull_calculator import HullCalculator
    
    # Define custom inputs
    custom_inputs = {
        # Dimensions
        "Lwl": 10.0,              # Longer waterline: 10m instead of 8m
        "Tc": 0.45,               # Deeper draft: 0.45m instead of 0.37m
        "X_Tc": 50,
        
        # Bow & Stern
        "Xbow": 9.5,              # Extended bow
        "Zbow": 0.95,             # Higher freeboard at bow
        "X_tab_ar": -1.5,
        "Z_tab_ar": 0.28,
        
        # Sheer Line
        "Bg": 2.5,                # Wider beam
        "X_Bg": 45,
        "Alfa": 3,                # More sheer angle
        "Z_liv_m": 0.80,
        "Z_liv_ar": 0.82,
        
        # Chine & Deck
        "Type_Chine": 0,
        "Zhc_av": 0.8,
        "Zhc_m": 0.25,
        "Zhc_ar": 0.45,
        "Pui_hc_z": 2,
        "Z_p_m": 0.90,
        "Z_p_ar": 0.85,
        "X_p_ar": -0.75,
        
        # Shape Polynomials
        "Cet": 3.5,               # More bow roundness
        "Kbrion": 0.1,
        "Pui_q_av": 2.5,
        "Pui_q_ar": 2.4,
        "Pui_liv_y": 2.2,
        "Cor_Pui_liv": 0.03,
        "Pui_Cor_Pui": 2.1,
        "X_liv_ar": -0.65,
        "Scow": 0.04,
        "Pui_Scow": 0.3,
        "Kroof": 31,
    }
    
    # Compute custom design
    calc = HullCalculator()
    calc.set_inputs(custom_inputs)
    calc.compute()
    
    # Export
    calc.export_json("custom_hull_10m.json")
    calc.export_csv("custom_hull_10m.csv")
    
    print(f"Custom 10m hull design computed: {len(calc.outputs)} points")


# ============================================================================
# EXAMPLE 3: Batch Processing Multiple Designs
# ============================================================================

def example3_batch_designs():
    """
    Create multiple hull designs and compare them.
    """
    from ghi_hull_calc.hull_calculator import HullCalculator, load_input_schema
    import json
    
    # Load base schema
    schema_path = "ghi_hull_calc/input_schema.json"
    schema = load_input_schema(schema_path)
    base_inputs = {key: data.get("value", 0) for key, data in schema.items()}
    
    # Create 3 designs with different beam widths
    designs = {
        "narrow": {"Bg": 1.8},    # Narrow beam (racey)
        "standard": {"Bg": 2.196}, # Standard Gene-Hull
        "wide": {"Bg": 2.6},       # Wide beam (stable)
    }
    
    results = {}
    
    for design_name, modifications in designs.items():
        # Apply modifications
        inputs = base_inputs.copy()
        inputs.update(modifications)
        
        # Compute
        calc = HullCalculator()
        calc.set_inputs(inputs)
        calc.compute()
        
        # Store summary
        results[design_name] = {
            "beam": inputs["Bg"],
            "points": len(calc.outputs),
            "file": f"design_{design_name}.json"
        }
        
        # Export
        calc.export_json(f"design_{design_name}.json")
    
    # Save comparison
    with open("design_comparison.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Design comparison:")
    for name, info in results.items():
        print(f"  {name}: Beam={info['beam']}m, Points={info['points']}")


# ============================================================================
# EXAMPLE 4: Analyzing Output Data
# ============================================================================

def example4_analyze_output():
    """
    Load and analyze computed hull data.
    """
    import json
    
    # Load JSON output
    with open("offsets_output.json", "r") as f:
        data = json.load(f)
    
    offsets = data["offsets"]
    
    # Extract unique sections
    sections = {}
    for point in offsets:
        section = point["section"]
        if section not in sections:
            sections[section] = []
        sections[section].append(point)
    
    print("Hull Offset Analysis")
    print("=" * 60)
    
    # Analyze each section
    for section_name in sorted(sections.keys()):
        section_data = sections[section_name]
        
        # Get X position (same for all points in section)
        x_pos = section_data[0]["x"]
        
        # Get Y and Z ranges
        y_values = [p["y"] for p in section_data]
        z_values = [p["z"] for p in section_data]
        
        y_max = max(y_values)
        z_min = min(z_values)
        z_max = max(z_values)
        
        print(f"\nSection {section_name}:")
        print(f"  X position: {x_pos:.1f} cm")
        print(f"  Max Y (half-width): {y_max:.1f} cm")
        print(f"  Z range: {z_min:.1f} to {z_max:.1f} cm")
        print(f"  Points: {len(section_data)}")


# ============================================================================
# EXAMPLE 5: Integration with FreeCAD
# ============================================================================

def example5_freecad_integration():
    """
    Code that runs inside FreeCAD's Python environment.
    This is called by the TaskPanel.
    """
    # In FreeCAD context:
    import FreeCAD as App
    import Part
    from ghi_hull_calc.hull_calculator import HullCalculator
    
    # Compute hull offsets
    calc = HullCalculator()
    calc.compute()
    
    # Create FreeCAD document with hull offsets
    doc = App.ActiveDocument or App.newDocument("HullDesign")
    
    # Convert offsets to 3D points
    points = []
    for offset in calc.outputs:
        x = offset["x"] / 100  # Convert cm to m
        y = offset["y"] / 100
        z = offset["z"] / 100
        points.append(App.Vector(x, y, z))
    
    # Create point cloud object
    obj = doc.addObject("Points::PointKernel", "HullOffsets")
    obj.Points = points
    obj.ViewObject.PointSize = 3
    
    # Recompute and save
    doc.recompute()
    doc.save()
    
    print(f"Created FreeCAD object with {len(points)} offset points")


# ============================================================================
# EXAMPLE 6: Export for CAD Software
# ============================================================================

def example6_export_for_cad():
    """
    Export hull data in formats compatible with other CAD systems.
    """
    import csv
    from ghi_hull_calc.hull_calculator import HullCalculator
    
    # Compute
    calc = HullCalculator()
    calc.compute()
    
    # Export as CSV for spreadsheet analysis
    with open("hull_analysis.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Section", "X(cm)", "Y(cm)", "Z(cm)", "Submerged"])
        
        for offset in calc.outputs:
            is_submerged = "Yes" if offset["z"] < 0 else "No"
            writer.writerow([
                offset["section"],
                f"{offset['x']:.2f}",
                f"{offset['y']:.2f}",
                f"{offset['z']:.2f}",
                is_submerged
            ])
    
    print("Exported to hull_analysis.csv")


# ============================================================================
# MAIN - Run Examples
# ============================================================================

if __name__ == "__main__":
    import os
    
    print("Hull Offset Calculator - Usage Examples")
    print("=" * 60)
    
    # Choose which examples to run
    examples = {
        "1": ("Standalone Calculator", example1_standalone_calculator),
        "2": ("Custom Design", example2_custom_design),
        "3": ("Batch Processing", example3_batch_designs),
        "4": ("Analyze Output", example4_analyze_output),
        "5": ("FreeCAD Integration", example5_freecad_integration),
        "6": ("CAD Export", example6_export_for_cad),
    }
    
    print("\nAvailable Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}: {name}")
    
    print("\nTo run all examples:")
    print("  python examples.py")
    
    print("\nTo run specific examples:")
    print("  python examples.py 1 2 3")
    
    # For now, just print this help
    print("\nNOTE: To execute, uncomment the example calls below")
    
    # Uncomment to run:
    # example1_standalone_calculator()
    # example2_custom_design()
    # example3_batch_designs()
    # example4_analyze_output()
    # example5_freecad_integration()
    # example6_export_for_cad()
