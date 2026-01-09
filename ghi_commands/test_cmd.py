import FreeCAD
import FreeCADGui
import Part

from ghi_topol_map.test_topol import topot_test

class TestCmd:

    def GetResources(self):
        return {
            "MenuText": "Test Command",
            "ToolTip": "This is a test command",
        }

    def Activated(self):

        topot_test()
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
            topot_test(30)
        doc.recompute()

def register():
    FreeCADGui.addCommand(
        "Topological test",
        TestCmd()
    )