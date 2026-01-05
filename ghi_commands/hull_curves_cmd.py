import FreeCAD as App
import FreeCADGui as Gui


from ghi_cell_alias_utils.cam_hull_section import hull_section_value
from ghi_cell_alias_utils.cam_hull_section import hull_section_name
from ghi_cell_alias_utils.cam_hull_center_line import hull_center_line_value
from ghi_cell_alias_utils.cam_hull_center_line import hull_center_line_name

class DocCurvesHullCmd:

    def GetResources(self):
        return {
            "MenuText": "Generate Hull Curves",
            "ToolTip": "Genera curve carena",
        }

    def Activated(self):
        import Part
        import Curves
        doc = 'Hull'
        App.ActiveDocument=App.getDocument(doc)
        sk = App.ActiveDocument.getObject('Sk_C0')
        if not sk:
            App.Console.PrintError('Sketch Sk_C0 non trovato\n')
            return

        verts = sk.Shape.Vertexes
        n = len(verts)
        if n < 2:
            App.Console.PrintError('Sk_C0 non ha abbastanza vertici\n')
            return

        points = []
        # forward: take vertices starting from index 3, every 2 steps (odd indices)
        start = 3
        for i in range(start, n, 2):
            points.append(verts[i].Point)

        # reverse: take the last even index < n down to 1, step -2
        last_even = (n - 1) if ((n - 1) % 2 == 0) else (n - 2)
        if last_even >= 1:
            for i in range(last_even, 0, -2):
                points.append(verts[i].Point)
        # -----------------------------
        # PUNTI ORDINATI DI UNA SEZIONE
        # -----------------------------
        # points = [
        #     App.Vector(0.0, -1.5,  0.0),
        #     App.Vector(0.0, -1.2, -0.4),
        #     App.Vector(0.0, -0.8, -0.9),
        #     App.Vector(0.0,  0.0, -1.2),
        #     App.Vector(0.0,  0.8, -0.9),
        #     App.Vector(0.0,  1.2, -0.4),
        #     App.Vector(0.0,  1.5,  0.0),
        # ]

        # 3️⃣ Crea la BSpline
        curve = Part.BSplineCurve()
        curve.interpolate(points)

        # 4️⃣ Crea l’oggetto Part::Feature
        obj = App.ActiveDocument.addObject("Part::Feature", "InterpolatedSection")
        obj.Shape = curve.toShape()

        App.ActiveDocument.recompute()



def register():
    Gui.addCommand(
        "GHI_Doc_Curves_Hull",
        DocCurvesHullCmd()
    )
