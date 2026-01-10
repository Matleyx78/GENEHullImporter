"""
FreeCAD TaskPanel for Hull Offset Calculator
"""

from PySide import QtGui, QtCore
import os
import sys
import json

try:
    import FreeCAD as App
except ImportError:
    App = None

# Add path to ghi_hull_calc
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ghi_hull_calc.hull_calculator import HullCalculator


class HullOffsetTaskPanel:
    """Task Panel for computing hull offsets"""
    
    def __init__(self):
        # Create main form widget
        self.form = QtGui.QWidget()
        self.form.setWindowTitle("Hull Offset Calculator")
        
        # Initialize data structures
        self.inputs_data = {}
        self.input_widgets = {}
        self.calculator = None
        
        try:
            # Load schema first
            self._load_schema()
            
            # Initialize calculator
            self.calculator = HullCalculator()
            
            # Create UI
            self._create_ui()
            
            if App:
                App.Console.PrintMessage("TaskPanel initialized successfully\n")
        except Exception as e:
            error_msg = f"Error initializing TaskPanel: {str(e)}"
            if App:
                App.Console.PrintError(f"{error_msg}\n")
            raise
    
    def _create_ui(self):
        """Create the task panel UI"""
        layout = QtGui.QVBoxLayout(self.form)
        
        # Title
        title = QtGui.QLabel("Hull Input Parameters")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Scroll area for inputs
        scroll = QtGui.QScrollArea()
        scroll_widget = QtGui.QWidget()
        scroll_layout = QtGui.QVBoxLayout(scroll_widget)
        
        # Group boxes for different categories
        self.lwl_group = self._create_input_group("Waterline & Draft", [
            ("Lwl", "Length of waterline (m)"),
            ("Tc", "Maximum draft (m)"),
            ("X_Tc", "Position of draft (% Lwl)"),
        ])
        scroll_layout.addWidget(self.lwl_group)
        
        self.bow_group = self._create_input_group("Bow & Stern", [
            ("Xbow", "Bow position (m)"),
            ("Zbow", "Bow freeboard (m)"),
            ("X_tab_ar", "Transom rear (m)"),
            ("Z_tab_ar", "Transom height (m)"),
        ])
        scroll_layout.addWidget(self.bow_group)
        
        self.sheer_group = self._create_input_group("Sheer Line", [
            ("Bg", "Sheer line width (m)"),
            ("X_Bg", "Sheer position (% Lwl)"),
            ("Alfa", "Sheer angle (deg)"),
            ("Z_liv_m", "Midship freeboard (m)"),
            ("Z_liv_ar", "Aft freeboard (m)"),
        ])
        scroll_layout.addWidget(self.sheer_group)
        
        self.chine_group = self._create_input_group("Hard Chine & Deck", [
            ("Type_Chine", "Chine type (0=none)"),
            ("Zhc_av", "Chine height bow (m)"),
            ("Zhc_m", "Chine height mid (m)"),
            ("Zhc_ar", "Chine height aft (m)"),
            ("Z_p_m", "Deck height mid (m)"),
            ("X_p_ar", "Deck rear (m)"),
            ("Z_p_ar", "Deck height aft (m)"),
        ])
        scroll_layout.addWidget(self.chine_group)
        
        self.poly_group = self._create_input_group("Shape Polynomials", [
            ("Cet", "Bow shape coefficient"),
            ("Kbrion", "Brion parameter"),
            ("Pui_q_av", "Keel front polynomial"),
            ("Pui_q_ar", "Keel rear polynomial"),
            ("Pui_liv_y", "Sheer polynomial y"),
            ("Pui_Scow", "Scow polynomial"),
        ])
        scroll_layout.addWidget(self.poly_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QtGui.QHBoxLayout()
        
        self.compute_btn = QtGui.QPushButton("Compute Offsets")
        self.compute_btn.clicked.connect(self.on_compute)
        button_layout.addWidget(self.compute_btn)
        
        self.export_json_btn = QtGui.QPushButton("Export JSON")
        self.export_json_btn.clicked.connect(self.on_export_json)
        button_layout.addWidget(self.export_json_btn)
        
        self.export_csv_btn = QtGui.QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self.on_export_csv)
        button_layout.addWidget(self.export_csv_btn)
        
        layout.addLayout(button_layout)
        
        # Status bar
        self.status_label = QtGui.QLabel("Ready")
        layout.addWidget(self.status_label)
    
    def _create_input_group(self, title: str, input_specs: list) -> QtGui.QGroupBox:
        """Create a group of input fields"""
        group = QtGui.QGroupBox(title)
        layout = QtGui.QGridLayout()
        
        for row, (key, label) in enumerate(input_specs):
            lbl = QtGui.QLabel(label)
            spin = QtGui.QDoubleSpinBox()
            spin.setRange(-1000, 1000)
            spin.setSingleStep(0.01)
            spin.setDecimals(3)
            
            # Get default value from schema
            if key in self.inputs_data:
                spin.setValue(self.inputs_data[key].get("value", 0))
            
            self.input_widgets[key] = spin
            layout.addWidget(lbl, row, 0)
            layout.addWidget(spin, row, 1)
        
        group.setLayout(layout)
        return group
    
    def _load_schema(self):
        """Load input schema from JSON"""
        try:
            schema_path = os.path.join(os.path.dirname(__file__), 
                                      "..", "ghi_hull_calc", "input_schema.json")
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.inputs_data = data.get("inputs", {})
                    if App:
                        App.Console.PrintMessage(f"Loaded {len(self.inputs_data)} input parameters\n")
            else:
                if App:
                    App.Console.PrintWarning(f"Schema file not found: {schema_path}\n")
        except Exception as e:
            if App:
                App.Console.PrintError(f"Error loading schema: {str(e)}\n")
    
    def on_compute(self):
        """Compute hull offsets"""
        try:
            if not self.calculator:
                raise RuntimeError("Calculator not initialized")
            
            # Collect input values
            inputs = {}
            for key, widget in self.input_widgets.items():
                inputs[key] = widget.value()
            
            # Compute
            self.calculator.set_inputs(inputs)
            self.calculator.compute()
            
            # Update status
            point_count = len(self.calculator.outputs)
            self.status_label.setText(f"OK - Computed {point_count} points")
            
            if App:
                App.Console.PrintMessage(f"Computed {point_count} hull offset points\n")
            
            QtGui.QMessageBox.information(self.form, "Success", 
                                         f"Hull offsets computed!\nTotal points: {point_count}")
        except Exception as e:
            error_msg = str(e)
            self.status_label.setText(f"ERROR: {error_msg}")
            if App:
                App.Console.PrintError(f"Computation failed: {error_msg}\n")
            QtGui.QMessageBox.critical(self.form, "Error", f"Computation failed:\n{error_msg}")
    
    def on_export_json(self):
        """Export to JSON"""
        if not self.calculator or not self.calculator.outputs:
            QtGui.QMessageBox.warning(self.form, "No Data", "Please compute first!")
            return
        
        filename, _ = QtGui.QFileDialog.getSaveFileName(self.form, "Export JSON", 
                                                       "", "JSON Files (*.json)")
        if filename:
            try:
                self.calculator.export_json(filename)
                basename = os.path.basename(filename)
                self.status_label.setText(f"OK - Exported to {basename}")
                if App:
                    App.Console.PrintMessage(f"Exported JSON to {filename}\n")
                QtGui.QMessageBox.information(self.form, "Success", f"Exported to:\n{filename}")
            except Exception as e:
                self.status_label.setText(f"ERROR - Export failed")
                if App:
                    App.Console.PrintError(f"Export failed: {str(e)}\n")
                QtGui.QMessageBox.critical(self.form, "Error", f"Export failed:\n{str(e)}")
    
    def on_export_csv(self):
        """Export to CSV"""
        if not self.calculator or not self.calculator.outputs:
            QtGui.QMessageBox.warning(self.form, "No Data", "Please compute first!")
            return
        
        filename, _ = QtGui.QFileDialog.getSaveFileName(self.form, "Export CSV", 
                                                       "", "CSV Files (*.csv)")
        if filename:
            try:
                self.calculator.export_csv(filename)
                basename = os.path.basename(filename)
                self.status_label.setText(f"OK - Exported to {basename}")
                if App:
                    App.Console.PrintMessage(f"Exported CSV to {filename}\n")
                QtGui.QMessageBox.information(self.form, "Success", f"Exported to:\n{filename}")
            except Exception as e:
                self.status_label.setText(f"ERROR - Export failed")
                if App:
                    App.Console.PrintError(f"Export failed: {str(e)}\n")
                QtGui.QMessageBox.critical(self.form, "Error", f"Export failed:\n{str(e)}")
    
    def accept(self):
        """Accept button (for FreeCAD task panel)"""
        self.on_compute()
        return True
    
    def reject(self):
        """Reject button (for FreeCAD task panel)"""
        return True
