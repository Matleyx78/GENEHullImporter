import FreeCADGui as Gui

from GENEHullImporterWorkbench import GENEHullImporterWorkbench
from ghi_commands.set_alias_cmd import register as register_set_alias
#from ghi_commands.hull_doc_and_sketch_cmd import register as register_hull_doc_and_sketch

register_set_alias()
#register_hull_doc_and_sketch()

Gui.addWorkbench(GENEHullImporterWorkbench())
