import FreeCAD as App
import FreeCADGui as Gui

from ghi_utils.cell_alias_mapping import section_cell_mapping

class SetAliasCmd:

    def GetResources(self):
        return {
            "MenuText": "Set Alias in spreadsheet",
            "ToolTip": "Setta alias nelle celle utili",
        }

    def Activated(self):

        doc = App.getDocument('GH_Import_Doc')
        sect = section_cell_mapping()
        # App.Console.PrintMessage(sect)
        for key1 in sect:
            for key2 in sect[key1]:
                App.Console.PrintMessage(key1 + " " + key2 + " " + sect[key1][key2] + "\n")
                doc.getObjectsByLabel("GH_Offset_Sheet")[0].setAlias(sect[key1][key2], key1 + "_" + key2)
        doc.recompute()


def register():
    Gui.addCommand(
        "GHI_Set_Alias",
        SetAliasCmd()
    )
