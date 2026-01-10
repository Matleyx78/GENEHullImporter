import FreeCADGui as Gui

from GENEHullImporterWorkbench import GENEHullImporterWorkbench
from ghi_commands.set_alias_cmd import register as register_set_alias
from ghi_commands.hull_doc_and_sketch_cmd import register as register_hull_doc_and_sketch
from ghi_commands.hull_curves_cmd import register as register_hull_curves
from ghi_commands.test_cmd import register as register_topol
from ghi_tp_hull.hull_offset_cmd import register_command as register_hull_calculator

register_set_alias()
register_hull_doc_and_sketch()
register_hull_curves()
register_topol()
register_hull_calculator()

Gui.addWorkbench(GENEHullImporterWorkbench())
