import FreeCAD
import FreeCADGui
import Part

class TestCmd:

    def GetResources(self):
        return {
            "MenuText": "Test Command",
            "ToolTip": "This is a test command",
        }

    def Activated(self):

        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument("TestDocument")

        body = None
        for obj in doc.Objects:
            if obj.TypeId == "PartDesign::Body":
                body = obj
                break

        if body is None:
            body = doc.addObject("PartDesign::Body", "TestBody")
            doc.recompute()

        doc.recompute()

def register():
    FreeCADGui.addCommand(
        "GHI_Test_Command",
        TestCmd()
    )