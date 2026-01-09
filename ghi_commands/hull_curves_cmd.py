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
        doc = 'Hull'
        App.ActiveDocument=App.getDocument(doc)
        lista_sezioni = hull_section_name()  # lista dei nomi delle sezioni
        chiglia = hull_center_line_name()
        for key in lista_sezioni:
            sk = App.ActiveDocument.getObject('Sk_' + key)
            if not sk:
                App.Console.PrintError(f'Sketch Sk_{key} non trovato\n')
                return

            verts = sk.Shape.Vertexes
            n = len(verts)
            if n < 2:
                App.Console.PrintError(f'Sketch Sk_{key} non ha abbastanza vertici\n')
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


            # 3️⃣ Crea la BSpline di carena
            curve = Part.BSplineCurve()
            curve.interpolate(points)

            # linee laterali
            L1 = verts[1].Point
            L2 = verts[3].Point
            R1 = verts[0].Point
            R2 = verts[2].Point
            Line_r = Part.LineSegment(R1, R2)
            Line_l = Part.LineSegment(L2, L1)

            # S1 = Part.Shape([curve.toShape(), Line_r.toShape(), Line_l.toShape()])
            S1 = Part.Shape([Line_l,curve, Line_r])
            W = Part.Wire(S1.Edges)
            

            # 4️⃣ Crea l’oggetto Part::Feature
            obj = App.ActiveDocument.addObject("Part::Feature", key + "_Curve")
            # obj.Shape = curve.toShape()
            # Part.show(W)
            obj.Shape = W            
            App.activeDocument().getObject("Hull_Curves").addObject(App.activeDocument().getObject(key + "_Curve"))

        App.ActiveDocument.recompute()



def register():
    Gui.addCommand(
        "GHI_Doc_Curves_Hull",
        DocCurvesHullCmd()
    )
