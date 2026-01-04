import FreeCADGui as Gui

class GENEHullImporterWorkbench(Gui.Workbench):

    def __init__(self):
        self.MenuText = "GENEHullImporter"
        self.ToolTip = "Generatore parametri carena stile Gene-Hull"
        self.Icon = ""

    def Initialize(self):
        self.appendToolbar(
            "Set Alias",
            ["GHI_Set_Alias"]
        )
        self.appendToolbar(
            "Hull Doc and Sketch",
            ["GHI_Doc_Sketch_Hull"]
        )
        self.appendToolbar(
            "Hull Curves",
            ["GHI_Doc_Curves_Hull"]
        )
        self.appendMenu(
            "Set Alias",
            ["GHI_Set_Alias"]
        )
        self.appendMenu(
            "Hull Doc and Sketch",
            ["GHI_Doc_Sketch_Hull"]
        )
    def GetClassName(self):
        return "Gui::PythonWorkbench"
