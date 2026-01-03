import FreeCAD as App
import FreeCADGui as Gui

from ghi_cell_alias_utils.cam_hull_section import hull_section_cell_mapping
from ghi_cell_alias_utils.cam_hull_center_line import hull_center_line_cell_mapping

class SetAliasCmd:

    def GetResources(self):
        return {
            "MenuText": "Set Alias in spreadsheet",
            "ToolTip": "Setta alias nelle celle utili",
        }

    def Activated(self):

        doc = App.getDocument('GH_Import_Doc')
        sect = {}
        sect['hull'] = hull_section_cell_mapping()
        sect['cen_line'] = hull_center_line_cell_mapping()
        # App.Console.PrintMessage(sect)
        for key1 in sect:
            for key2 in sect[key1]:
                for key3 in sect[key1][key2]:
                    for key4 in sect[key1][key2][key3]:
                        doc.getObjectsByLabel("GH_Offset_Sheet")[0].setAlias(sect[key1][key2][key3][key4], key2 + "_" + key3 + "_" + key4)
        doc.recompute()


def register():
    Gui.addCommand(
        "GHI_Set_Alias",
        SetAliasCmd()
    )
