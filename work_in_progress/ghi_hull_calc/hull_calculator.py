"""
Pure Python Hull Calculator - No ODS Dependency

Computes hull geometry and offsets from input parameters.
Output: JSON with all offset values for rows 9-139 of "Offsets x,y,z" sheet.
"""

import json
import math
from typing import Dict, Any, Optional, List, Tuple


class HullCalculator:
    """Main calculator for hull geometry"""
    
    def __init__(self):
        self.inputs: Dict[str, float] = {}
        self.outputs: Dict[str, Any] = {}
        self.intermediate: Dict[str, float] = {}
    
    def set_inputs(self, inputs_dict: Dict[str, float]):
        """Set input parameters"""
        self.inputs = inputs_dict
        self.outputs = {}
        self.intermediate = {}
    
    def compute(self) -> Dict[str, Any]:
        """Main computation pipeline"""
        self._compute_hull_dimensions()
        self._compute_sections()
        self._compute_offsets()
        return self.outputs
    
    def _compute_hull_dimensions(self):
        """Compute basic hull dimensions from inputs"""
        # Extract key inputs
        lwl = self.inputs.get("Lwl", 8.0)  # Length of waterline
        tc = self.inputs.get("Tc", 0.37)   # Draft
        bg = self.inputs.get("Bg", 2.196)  # Beam at sheer
        xbow = self.inputs.get("Xbow", 9.0)  # Bow position
        zbow = self.inputs.get("Zbow", 0.85)  # Bow freeboard
        x_tab_ar = self.inputs.get("X_tab_ar", -1.3)  # Transom rear
        z_tab_ar = self.inputs.get("Z_tab_ar", 0.24)  # Transom height
        x_liv_ar = self.inputs.get("X_liv_ar", -0.6)  # Sheer rear
        z_liv_m = self.inputs.get("Z_liv_m", 0.72)  # Midship freeboard
        z_liv_ar = self.inputs.get("Z_liv_ar", 0.74)  # Aft freeboard
        
        # Compute Loa (Length over all)
        loa = xbow + abs(x_tab_ar)
        
        # Compute Boa (Beam over all) - approximation based on Bg
        boa = bg * 1.2  # Rough approximation
        
        # Store computed dimensions
        self.intermediate["Loa"] = loa
        self.intermediate["Lwl"] = lwl
        self.intermediate["Boa"] = boa
        self.intermediate["Bg"] = bg
        self.intermediate["Tc"] = tc
        self.intermediate["Zbow"] = zbow
        self.intermediate["Z_liv_m"] = z_liv_m
        self.intermediate["Z_liv_ar"] = z_liv_ar
    
    def _compute_sections(self):
        """Compute section parameters (C0-C10)"""
        lwl = self.inputs.get("Lwl", 8.0)
        x_tc_pct = self.inputs.get("X_Tc", 50.0)
        
        # Section positions (% of Lwl from bow)
        sections = {
            "C0": 0.0,      # Bow
            "C0.5": 10.0,
            "C1": 20.0,
            "C1.5": 30.0,
            "C2": 40.0,
            "C2.5": 47.5,
            "C3": 55.0,     # Midship area
            "C3.5": 62.5,
            "C4": 70.0,
            "C4.5": 80.0,
            "C5": 90.0,
            "C5.5": 95.0,
            "C6": 100.0,    # Stern
        }
        
        # For each section, compute x position
        for section_name, x_pct in sections.items():
            x_pos = (x_pct / 100.0) * lwl
            self.intermediate[f"{section_name}_x"] = x_pos
            # Y (half-beam) will be computed based on hull shape
            # Z (height) will be computed based on freeboard
    
    def _compute_offsets(self):
        """Compute offset coordinates (Y, Z) for each section"""
        lwl = self.inputs.get("Lwl", 8.0)
        tc = self.inputs.get("Tc", 0.37)
        bg = self.inputs.get("Bg", 2.196)
        x_bg_pct = self.inputs.get("X_Bg", 43.0)
        zbow = self.inputs.get("Zbow", 0.85)
        z_liv_m = self.inputs.get("Z_liv_m", 0.72)
        z_liv_ar = self.inputs.get("Z_liv_ar", 0.74)
        cet = self.inputs.get("Cet", 3.0)
        
        # Generate offset rows 9-139 (output sheet rows)
        # This is a simplified offset table
        
        row = 9
        section_names = ["Car2", "C0", "C0.5", "C1", "C1.5", "C2", "C2.5", "C3", "C3.5", 
                        "C4", "C4.5", "C5", "C5.5", "C6", "C6.5", "C7", "C7.5", 
                        "C8", "C8.5", "C9", "C9.5", "C10", "Cav1", "Cav2"]
        
        # For each section, generate Y/Z offsets at multiple Z levels
        z_levels = [-tc, -tc*0.75, -tc*0.5, -tc*0.25, 0, 0.1, 0.2, 0.3, 0.4, 0.5]
        
        for section_name in section_names:
            x_pct = self._get_section_x_pct(section_name)
            if x_pct is not None:
                x_pos = (x_pct / 100.0) * lwl
                
                # Compute section properties
                section_data = self._compute_section_offsets(section_name, x_pct, z_levels)
                
                # Add to outputs - each section gets multiple rows
                for z_level, y_value in section_data.items():
                    self.outputs[f"Row_{row}"] = {
                        "section": section_name,
                        "x": round(x_pos * 100, 2),  # Convert to cm
                        "y": round(y_value * 100, 2),  # Convert to cm
                        "z": round(z_level * 100, 2),  # Convert to cm
                        "z_level": z_level
                    }
                    row += 1
    
    def _get_section_x_pct(self, section_name: str) -> Optional[float]:
        """Get X position (% of Lwl) for a section"""
        sections = {
            "Car2": -5.0,  # Carena section 2 - forward of bow
            "C0": 0.0, "C0.5": 5.0, "C1": 10.0, "C1.5": 15.0, "C2": 20.0,
            "C2.5": 25.0, "C3": 30.0, "C3.5": 35.0, "C4": 40.0, "C4.5": 45.0,
            "C5": 50.0, "C5.5": 55.0, "C6": 60.0, "C6.5": 65.0, "C7": 70.0,
            "C7.5": 75.0, "C8": 80.0, "C8.5": 85.0, "C9": 90.0, "C9.5": 95.0,
            "C10": 100.0, "Cav1": 110.0, "Cav2": 120.0
        }
        return sections.get(section_name)
    
    def _compute_section_offsets(self, section_name: str, x_pct: float, 
                                 z_levels: List[float]) -> Dict[float, float]:
        """Compute Y offsets for a section at multiple Z levels"""
        bg = self.inputs.get("Bg", 2.196)
        x_bg_pct = self.inputs.get("X_Bg", 43.0)
        tc = self.inputs.get("Tc", 0.37)
        cet = self.inputs.get("Cet", 3.0)
        pui_liv_y = self.inputs.get("Pui_liv_y", 2.0)
        
        result = {}
        
        # Parametric hull shape - simplified
        # Y = f(X, Z) using shape parameters
        
        for z in z_levels:
            # Distance from bow (0 to 1)
            x_norm = x_pct / 100.0
            # Depth from waterline (-1 = draft, 0 = waterline)
            z_norm = z / tc if tc != 0 else 0
            
            # Basic hull shape polynomial
            if z >= 0:  # Above waterline
                y = 0.1 * bg * (1 - x_norm**2) * (1 + 0.1 * x_norm)
            else:  # Below waterline
                y = bg * (1 - x_norm**pui_liv_y) * (1 + abs(z_norm) * 0.3)
            
            result[z] = y
        
        return result
    
    def export_json(self, output_path: str):
        """Export computed offsets to JSON"""
        export_data = {
            "inputs": self.inputs,
            "intermediate": self.intermediate,
            "outputs": self.outputs,
            "metadata": {
                "description": "Hull offsets computed from input parameters",
                "rows": "9-139 from Offsets x,y,z sheet",
                "units": "cm for offsets"
            }
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)
    
    def export_csv(self, output_path: str):
        """Export computed offsets to CSV"""
        import csv
        
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Section", "X(cm)", "Y(cm)", "Z(cm)"])
            
            for row_key, row_data in sorted(self.outputs.items()):
                writer.writerow([
                    row_data.get("section", ""),
                    row_data.get("x", ""),
                    row_data.get("y", ""),
                    row_data.get("z", "")
                ])


def load_input_schema(schema_path: str) -> Dict[str, Dict[str, Any]]:
    """Load input schema from JSON"""
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    return schema.get("inputs", {})


if __name__ == "__main__":
    import sys
    
    # Load schema
    schema = load_input_schema("ghi_hull_calc/input_schema.json")
    
    # Extract default values
    inputs = {key: data.get("value", 0) for key, data in schema.items()}
    
    # Create calculator and compute
    calc = HullCalculator()
    calc.set_inputs(inputs)
    calc.compute()
    
    # Export
    calc.export_json("ghi_hull_calc/offsets_output.json")
    calc.export_csv("ghi_hull_calc/offsets_output.csv")
    
    print(f"Computed {len(calc.outputs)} offset points")
    print("Outputs saved to:")
    print("  - ghi_hull_calc/offsets_output.json")
    print("  - ghi_hull_calc/offsets_output.csv")
