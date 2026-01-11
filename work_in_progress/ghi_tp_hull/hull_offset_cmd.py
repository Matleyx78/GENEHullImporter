"""
Hull Offset Calculator Command for FreeCAD
Integrates the TaskPanel into the GENEHullImporter workbench
"""

import FreeCAD as App
import FreeCADGui as Gui
import os
import sys

# Add module path
module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if module_path not in sys.path:
    sys.path.insert(0, module_path)

from ghi_tp_hull.task_panel_hull import HullOffsetTaskPanel


class HullOffsetCalculatorCmd:
    """Command class for hull offset calculator"""
    
    def GetResources(self):
        return {
            'Pixmap': '',  # Optional: path to icon
            'MenuText': 'Hull Offset Calculator',
            'ToolTipText': 'Calculate hull offsets from design parameters',
            'Accel': ''
        }
    
    def Activated(self):
        """Execute the command"""
        try:
            panel = HullOffsetTaskPanel()
            Gui.Control.showDialog(panel)
        except Exception as e:
            App.Console.PrintError(f"Error launching Hull Offset Calculator: {str(e)}\n")
            import traceback
            App.Console.PrintError(traceback.format_exc())
    
    def IsActive(self):
        """Check if command is active"""
        return True


# Register the command
def register_command():
    """Register the command with FreeCAD"""
    try:
        Gui.addCommand('HullOffsetCalculator', HullOffsetCalculatorCmd())
        App.Console.PrintMessage("Hull Offset Calculator command registered\n")
    except Exception as e:
        App.Console.PrintError(f"Error registering command: {str(e)}\n")


if __name__ == '__main__':
    register_command()
