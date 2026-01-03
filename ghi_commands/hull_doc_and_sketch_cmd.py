import FreeCAD as App
import FreeCADGui as Gui
import Sketcher

from ghi_obj_creation.hull_creation import hull_doc_creation
from ghi_obj_creation.hull_creation import hull_body_creation
from ghi_obj_creation.hull_creation import hull_section_sketch_creation
from ghi_obj_creation.hull_creation import hull_center_line_sketch_creation
from ghi_cell_alias_utils.cam_hull_section import hull_section_value
from ghi_cell_alias_utils.cam_hull_section import hull_section_name
from ghi_cell_alias_utils.cam_hull_center_line import hull_center_line_value
from ghi_cell_alias_utils.cam_hull_center_line import hull_center_line_name

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
        sec_value = hull_section_value(sheet)               #list['name_section']['row_name_or_number']['coord'] = value
        sec_value2 = hull_center_line_value(sheet)          #list['name_section']['row_name_or_number']['coord'] = value
        list_val = {**sec_value, **sec_value2}
        doc_name = hull_doc_creation(list_val) # da qui ci sono i varset pronti
        sec_name = hull_section_name()
        center_line_name = hull_center_line_name()
        App.ActiveDocument=App.getDocument(doc_name)
        App.ActiveDocument.recompute()
        App.ActiveDocument=App.getDocument(doc_name)
        body_name = hull_body_creation()                
        App.ActiveDocument.recompute()
        hull_section_sketch_creation(sec_name,body_name)
        App.ActiveDocument.recompute()
        hull_center_line_sketch_creation(center_line_name,body_name)
        App.ActiveDocument.recompute()



def register():
    Gui.addCommand(
        "GHI_Doc_Sketch_Hull",
        DocSketchHullCmd()
    )
