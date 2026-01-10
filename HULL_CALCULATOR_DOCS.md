# Hull Offset Calculator - System Documentation

## Overview
The Hull Offset Calculator is a standalone Python application that replicates the Gene-Hull ODS spreadsheet functionality without requiring the external file. It's integrated into FreeCAD via a TaskPanel GUI.

## Architecture

### Three-Layer Design

```
┌─────────────────────────────────────┐
│     FreeCAD TaskPanel (GUI)         │  ghi_tp_hull/
│  - Input fields (43 parameters)     │
│  - Compute button                   │
│  - Export (JSON/CSV)                │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│  HullCalculator (Core Engine)       │  ghi_hull_calc/
│  - set_inputs(dict)                 │
│  - compute()                        │
│  - export_json/export_csv()         │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│  Input Schema (JSON)                │  input_schema.json
│  - 43 parameters with defaults      │
│  - Unit definitions                 │
│  - Validation rules                 │
└─────────────────────────────────────┘
```

## Files and Their Roles

### `ghi_hull_calc/` Directory

#### `input_schema.json`
- **Purpose**: Define all 43 input parameters (Gene-Hull sheet rows 11-58)
- **Format**: JSON with structure:
  ```json
  {
    "inputs": {
      "Lwl": {"value": 8.0, "unit": "m", "comment": "Length of waterline"},
      "Tc": {"value": 0.37, "unit": "m", "comment": "Maximum draft"},
      ...
    }
  }
  ```
- **43 Parameters** (organized by functionality):
  1. **Dimensions**: Lwl, Tc, X_Tc
  2. **Bow/Stern**: Xbow, Zbow, X_tab_ar, Z_tab_ar
  3. **Sheer**: Bg, X_Bg, Alfa, Z_liv_m, Z_liv_ar
  4. **Chine/Deck**: Type_Chine, Zhc_av/m/ar, Z_p_m/ar, X_p_ar
  5. **Polynomials**: Cet, Kbrion, Pui_q_av/ar, Pui_liv_y, Pui_Scow, Pui_hc_z, etc.

#### `hull_calculator.py`
- **Purpose**: Pure Python calculation engine (NO dependencies on ODS or GUI)
- **Main Class**: `HullCalculator`
- **Key Methods**:
  - `set_inputs(dict)` – Accept 43 parameters
  - `compute()` – Main computation pipeline
  - `export_json(path)` – Save results to JSON
  - `export_csv(path)` – Save results to CSV
- **Output**:
  - For each section (C0-C10, Cav1-2): ~20 Z-levels from waterline to keel
  - Total: ~230 offset points
  - Format: `{section: str, x_cm: float, y_cm: float, z_cm: float}`

### `ghi_tp_hull/` Directory

#### `task_panel_hull.py`
- **Purpose**: FreeCAD TaskPanel GUI for hull design
- **Main Class**: `HullOffsetTaskPanel`
- **Features**:
  - 43 input fields organized in 5 collapsible groups:
    - Waterline & Draft
    - Bow & Stern
    - Sheer Line
    - Hard Chine & Deck
    - Shape Polynomials
  - "Compute Offsets" button → calls `HullCalculator.compute()`
  - "Export JSON" and "Export CSV" buttons
  - Live status updates

#### `hull_offset_cmd.py`
- **Purpose**: FreeCAD command registration
- **Main Class**: `HullOffsetCalculatorCmd`
- **Functionality**: Integrates TaskPanel into FreeCAD menu/toolbar
- **Registration**: Loaded by `InitGui.py` on FreeCAD startup

## Workflow

### Step 1: Launch TaskPanel
```
User selects: GENEHullImporter > Hull Calculator > Hull Offset Calculator
      ↓
FreeCAD loads hull_offset_cmd.py
      ↓
HullOffsetTaskPanel widget is created
      ↓
Input fields are populated with defaults from input_schema.json
```

### Step 2: Set Parameters
```
User enters 43 hull parameters (visual form with spin boxes)
Each field has:
  - Label with description
  - Spin box with min/max/step
  - Unit indicator (m, deg, etc.)
```

### Step 3: Compute
```
User clicks "Compute Offsets"
      ↓
HullCalculator.set_inputs(dict) loads parameters
      ↓
HullCalculator.compute() runs 3 main stages:
  1. _compute_hull_dimensions() → Loa, Boa, draft
  2. _compute_sections() → C0-C10, Cav1-2 positions
  3. _compute_offsets() → Y/Z for each section at each Z-level
      ↓
Results stored in self.outputs (list of dicts)
      ↓
StatusBar shows: "✓ Computed 230 points"
```

### Step 4: Export
```
User clicks "Export JSON" or "Export CSV"
      ↓
File dialog opens
      ↓
HullCalculator.export_json(path) / export_csv(path)
      ↓
Files saved with full computation results
```

## Computation Pipeline

### Stage 1: Hull Dimensions
- **Lwl** (waterline length) → X-axis scale
- **Tc** (maximum draft) → Z-axis underwater extent
- **Boa** (beam overall) → estimated from Bg, Kbrion
- **Loa** (length overall) → estimated from Lwl, Xbow, X_tab_ar

### Stage 2: Section Positioning
Sections are distributed along X-axis:
- **C0**: x = 0.0 m (bow)
- **C4.5, C5, C6, C6.5**: at 25%, 50%, 75%, 87.5% of Lwl
- **C10**: x = Lwl (stern)
- **Cav1, Cav2**: average sections

### Stage 3: Offset Generation
For each section, compute Y and Z coordinates:
- **Z-levels**: 10 levels from -Tc (keel) to +freeboard (deck)
  - Underwater: -Tc, -0.75×Tc, -0.5×Tc, -0.25×Tc, 0 (waterline), ...
  - Above water: +0.25×freeboard, +0.5×freeboard, ...
- **Y-values**: Using polynomials based on:
  - Section position (X)
  - Shape coefficients (Cet, Kbrion, Pui_q_av, Pui_q_ar)
  - Sheer line (Bg, X_Bg, Alfa, Pui_liv_y)
  - Chine positions (if Type_Chine ≠ 0)

## Input Parameters (43 Total)

### Dimensions (3)
| Parameter | Unit | Description |
|-----------|------|-------------|
| Lwl | m | Length of waterline |
| Tc | m | Maximum draft (underwater depth) |
| X_Tc | % Lwl | Position of maximum draft |

### Bow & Stern (4)
| Parameter | Unit | Description |
|-----------|------|-------------|
| Xbow | m | Bow position forward |
| Zbow | m | Bow freeboard height |
| X_tab_ar | m | Transom rear position |
| Z_tab_ar | m | Transom height |

### Sheer Line (5)
| Parameter | Unit | Description |
|-----------|------|-------------|
| Bg | m | Sheer line width |
| X_Bg | % Lwl | Sheer reference position |
| Alfa | deg | Sheer line angle |
| Z_liv_m | m | Midship freeboard |
| Z_liv_ar | m | Aft freeboard |

### Chine & Deck (7)
| Parameter | Unit | Description |
|-----------|------|-------------|
| Type_Chine | - | Chine type (0=none) |
| Zhc_av | m | Chine height at bow |
| Zhc_m | m | Chine height at midship |
| Zhc_ar | m | Chine height at stern |
| Pui_hc_z | - | Chine polynomial power |
| Z_p_m | m | Deck height midship |
| Z_p_ar | m | Deck height aft |

### Shape Polynomials (12)
| Parameter | Unit | Description |
|-----------|------|-------------|
| Cet | - | Bow shape coefficient |
| Kbrion | - | Brion curvature parameter |
| Pui_q_av | - | Keel front polynomial power |
| Pui_q_ar | - | Keel rear polynomial power |
| Pui_liv_y | - | Sheer Y-direction polynomial |
| Cor_Pui_liv | - | Sheer correction factor |
| Pui_Cor_Pui | - | Correction polynomial |
| X_liv_ar | m | Aft section position |
| Scow | - | Scow flatness factor |
| Pui_Scow | - | Scow polynomial |
| X_p_ar | m | Deck rear position |
| Kroof | - | Deck curvature |

## Output Structure

### JSON Format
```json
{
  "inputs": {
    "Lwl": 8.0,
    "Tc": 0.37,
    ...
  },
  "offsets": [
    {"section": "C0", "x_cm": 0.0, "y_cm": 269.01, "z_cm": -27.75},
    {"section": "C0", "x_cm": 0.0, "y_cm": 252.54, "z_cm": -18.5},
    ...
  ],
  "summary": {
    "total_points": 230,
    "sections": 12,
    "z_levels_per_section": 19
  }
}
```

### CSV Format
```
Section,X(cm),Y(cm),Z(cm)
C0,0.0,269.01,-27.75
C0,0.0,252.54,-18.5
C4.5,360.0,214.54,-27.75
...
```

## Integration with FreeCAD

### Registration
1. `InitGui.py` imports `register_hull_calculator()`
2. `hull_offset_cmd.py` registers `HullOffsetCalculatorCmd` class
3. Workbench adds toolbar button and menu item

### Activation
- User selects: **Hull Calculator** menu → **Hull Offset Calculator**
- FreeCAD calls `HullOffsetCalculatorCmd.Activated()`
- TaskPanel opens with 43 input fields

### Export Options
1. **JSON**: Full computation results + all inputs
2. **CSV**: Tabular format (Section, X, Y, Z) for CAD import

## Parametric Hull Model

The calculator uses a parametric approach based on:
- **Waterline length (Lwl)** as X-axis reference
- **Section positions** at fixed percentages of Lwl
- **Polynomial functions** for Y-width and Z-depth curves
- **Shape coefficients** (Cet, Kbrion, Pui_*) to modulate curves

### Y-Coordinate (Half-Width)
```
y(x, z) = y_base(x) × correction_factor(z)

where:
  y_base(x) = f(x, Cet, Kbrion, section_type)
  correction_factor(z) = polynomial in z with Pui_liv_y, Pui_q_av, etc.
```

### Z-Coordinate (Depth)
```
z(x, x_section) = z_waterline(x) + z_offset(x, x_section)

where:
  z_waterline = Bg × sin(Alfa) + reference_sheer(x)
  z_offset = based on draft Tc and freeboard
```

## Testing & Validation

### First Test Run
```powershell
cd ghi_hull_calc
python hull_calculator.py
# Output: "Computed 230 offset points"
# Files: offsets_output.json, offsets_output.csv
```

### Validation Against ODS
- Compare computed offsets with Gene-Hull sheet "Offsets x,y,z" (rows 9-139)
- Check first 10 rows for exact matches
- Validate section positions and Z-levels

### Expected Results
- **Total points**: ~230 (12 sections × 19 Z-levels + 2 averaged sections)
- **X-range**: 0 to 800 cm (Lwl = 8m)
- **Y-range**: 0 to 300 cm (half-beam ~3m)
- **Z-range**: -37 to +83 cm (draft -37cm, freeboard +83cm)

## Future Extensions

1. **Keel and Rudder**: Add separate modules for fin keel and rudder geometry
2. **3D Model Generation**: Convert offsets to FreeCAD Part → .step file
3. **Hydrostatics**: Add displacement, center of buoyancy, metacentric height
4. **Resistance Calculation**: Integrate Holtrop-Mennen or similar method
5. **Parametric Optimization**: Add solver for optimal hull shape

## Code Examples

### Using HullCalculator Standalone
```python
from ghi_hull_calc.hull_calculator import HullCalculator

calc = HullCalculator()
calc.set_inputs({
    'Lwl': 8.0,
    'Tc': 0.37,
    'Bg': 2.196,
    # ... 40 more parameters
})
calc.compute()
calc.export_json('my_hull.json')
```

### From FreeCAD
```
1. Switch to GENEHullImporter workbench
2. Click toolbar button "Hull Offset Calculator"
3. TaskPanel opens
4. Set parameters
5. Click "Compute Offsets"
6. Click "Export JSON"
7. Use offsets to build 3D model
```

## Troubleshooting

### Issue: "Module not found: ghi_hull_calc"
**Solution**: Ensure `sys.path` includes parent directory of GENEHullImporter

### Issue: "QMessageBox not found"
**Solution**: TaskPanel requires PySide (comes with FreeCAD)

### Issue: "Input schema JSON not found"
**Solution**: Verify `input_schema.json` exists in `ghi_hull_calc/` directory

### Issue: "Computed values don't match ODS"
**Solution**: Check parametric equations in `_compute_offsets()` method; may need coefficient tuning

## References

- Gene-Hull ODS: `Gene-Hull Sailboat 3.4_2025 02.ods` (source file)
- FreeCAD Documentation: https://wiki.freecadweb.org/
- TaskPanel API: https://wiki.freecadweb.org/Task_panel
