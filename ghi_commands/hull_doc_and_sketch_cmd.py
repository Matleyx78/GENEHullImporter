import FreeCAD as App
import FreeCADGui as Gui
import Sketcher

from ghi_varset_utils.ghi_varset_creation import varset_creation
from ghi_varset_utils.ghi_varset_creation import varset_get_value
from ghi_obj_creation.hull_creation import hull_doc_creation
from ghi_obj_creation.hull_creation import hull_body_creation
from ghi_obj_creation.hull_creation import hull_section_sketch_creation
from ghi_obj_creation.hull_creation import hull_center_line_sketch_creation
from ghi_obj_creation.rear_transom import rear_transom_creation
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
        doc_name = hull_doc_creation(sheet)              # da qui ci sono i varset pronti
        # check hard chine type
        val1 = varset_get_value(doc_name, 'Chine_and_Sheer_line', 'Car2_z_c')
        val2 = varset_get_value(doc_name, 'Chine_and_Sheer_line', 'Car2_z_s')
        if val1 == val2:
            App.Console.PrintMessage('Hard chine type: Uguale\n')
            hc_type = 0 # non dritto ma stondato
        else:
            App.Console.PrintMessage('Hard chine type: Diverso\n')
            hc_type = 1 # dritto
        # body creation        
        body_name = hull_body_creation()                
        App.ActiveDocument.recompute()
        # creo le sezioni della carena
        hull_section_sketch_creation(body_name)
        # creo la center line
        hull_center_line_sketch_creation(body_name)
        # creo la keel line
        # creo la deck line
        # creo la punteggiatura della parte posteriore
        rear_transom_creation(doc_name, body_name, hc_type)




        # sec_name = hull_section_name()
        # center_line_name = hull_center_line_name()
        # App.ActiveDocument=App.getDocument(doc_name)
        # App.ActiveDocument.recompute()
        # App.ActiveDocument=App.getDocument(doc_name)

        
        # App.ActiveDocument.recompute()
        # hull_center_line_sketch_creation(center_line_name,body_name)
        App.ActiveDocument.recompute()



def register():
    Gui.addCommand(
        "GHI_Doc_Sketch_Hull",
        DocSketchHullCmd()
    )
