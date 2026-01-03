import FreeCAD as App
import FreeCADGui as Gui
import Sketcher

from ghi_obj_creation.hull_creation import hull_doc_creation
from ghi_obj_creation.hull_creation import hull_body_creation
from ghi_obj_creation.hull_creation import hull_sketch_creation
from ghi_utils.cell_alias_mapping import section_value 
from ghi_utils.cell_alias_mapping import section_name 
# from model.sailboat_model import SailBoatModel
# from model.inputs import SailBoatInputs
# from model.outputs import SailBoatOutputs
from ghi_utils.cell_alias_mapping import section_cell_mapping


class DocSketchHullCmd:

    def GetResources(self):
        return {
            "MenuText": "Generate Hull doc with sketch",
            "ToolTip": "Genera il documento carena e i suoi sketch",
        }

    def Activated(self):
        doc_import = 'GH_Import_Doc'
        App.ActiveDocument=App.getDocument(doc_import)
        sheet = App.activeDocument().getObjectsByLabel("GH_Offset_Sheet")[0]
        sec_value = section_value(sheet)        # sec_value[namesection][property] = value
        doc_name = hull_doc_creation(sec_value) # da qui ci sono i varset pronti
        sec_name = section_name()
        App.ActiveDocument=App.getDocument(doc_name)
        App.ActiveDocument.recompute()
        App.ActiveDocument=App.getDocument(doc_name)
        body_name = hull_body_creation()                
        App.ActiveDocument.recompute()
        # App.ActiveDocument=App.getDocument(body_name)
        hull_sketch_creation(sec_name,body_name)
        App.ActiveDocument.recompute()



def register():
    Gui.addCommand(
        "GHI_Doc_Sketch_Hull",
        DocSketchHullCmd()
    )
