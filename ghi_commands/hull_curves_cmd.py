import FreeCAD as App
import FreeCADGui as Gui

import Sketcher
import Part
import Curves
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
    def part_creation(self, name, points):
        import Part
        # 3️⃣ Crea la BSpline
        curve = Part.BSplineCurve()
        curve.interpolate(points)

        # 4️⃣ Crea l’oggetto Part::Feature
        obj = App.ActiveDocument.addObject("Part::Feature", name)
        obj.Shape = curve.toShape()

    def Activated(self):
        from Curves import Sketch_on_Surface
        from Curves import Interpolate
        # -----------------------------
        # PUNTI ORDINATI DI UNA SEZIONE
        # -----------------------------
        points = [
            App.Vector(0.0, -1.5,  0.0),
            App.Vector(0.0, -1.2, -0.4),
            App.Vector(0.0, -0.8, -0.9),
            App.Vector(0.0,  0.0, -1.2),
            App.Vector(0.0,  0.8, -0.9),
            App.Vector(0.0,  1.2, -0.4),
            App.Vector(0.0,  1.5,  0.0),
        ]

        # -----------------------------
        # CREA CURVA INTERPOLATA (CURVES)
        # -----------------------------
        curve_obj = Interpolate.makeInterpolatedCurve(
            points,
            False   # periodic = False
        )

        curve_obj.Label = "Curves_Section"

        App.ActiveDocument.recompute()


    def Activated_OLD(self):
        
        from App.Parts import BSplineCurve
        from Curves import Sketch_On_Surface
        b39 = 1    # Hardchine value in GeneHull sheet in b39
        sec_name = hull_section_name()
        doc = 'Hull'
        App.ActiveDocument=App.getDocument(doc)
        
        keel_point = []
        deck_line_1 = []
        deck_line_2 = []
        name_sk = 'Sk_Cent_line'
        sk = App.ActiveDocument.getObject(name_sk)
        verts_of_center_line = sk.Shape.Vertexes

        for key in sec_name: 
            name_sk = 'Sk_' + key           
            sk = App.ActiveDocument.getObject(name_sk)
            if not sk:
                App.Console.PrintError('Sketch non trovato\n')
                return

            verts = sk.Shape.Vertexes
            n = len(verts)
            if n < 2:
                App.Console.PrintError('Sk_C0 non ha abbastanza vertici\n')
                return
            
            keel_point.append(verts[44].Point)
            deck_line_1.append(verts[0].Point)
            deck_line_2.append(verts[1].Point)

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
            
            name_part = "InterpolatedSection" + name_sk

            self.part_creation(name_part, points)
            
            # -----------------------------
            # PUNTI ORDINATI DI UNA SEZIONE
            # -----------------------------
            points_line_1 = []
            points_line_2 = []
            points_line_1.append(verts[0].Point)
            points_line_1.append(verts[2].Point)
            points_line_2.append(verts[1].Point)
            points_line_2.append(verts[3].Point)

            line1 = Part.LineSegment()
            line1.StartPoint = points_line_1[0]
            line1.EndPoint = points_line_1[1]
            line2 = Part.LineSegment()
            line2.StartPoint = points_line_2[0]
            line2.EndPoint = points_line_2[1]
            obj_line1 = App.ActiveDocument.addObject("Part::Feature", "Line1_Section" + name_sk)
            obj_line1.Shape = line1.toShape()
            obj_line2 = App.ActiveDocument.addObject("Part::Feature", "Line2_Section" + name_sk)
            obj_line2.Shape = line2.toShape()

            App.ActiveDocument.recompute()

        # finish keel
        keel_point.append(verts_of_center_line[18].Point)
        keel_name = 'Keel_Line'
        self.part_creation(keel_name, keel_point)
        # finish deck line
        # print(deck_line_2)
        App.Console.PrintMessage('Indice: ' + str(deck_line_2[0]) + "\n")
        App.Console.PrintMessage('Indice: ' + str(deck_line_2[10]) + "\n")
        App.Console.PrintMessage('Indice: ' + str(len(deck_line_2)) + "\n")
        deck_line_1.append(verts_of_center_line[18].Point)
        for i in range(len(deck_line_2)-1,-1,-1):
            
            App.Console.PrintMessage('Indice: ' + str(i) + "\n")
            deck_line_1.append(deck_line_2[i])
        deck_name = 'Deck_Line'
        self.part_creation(deck_name, deck_line_1)
        
        App.ActiveDocument.recompute()


def register():
    Gui.addCommand(
        "GHI_Doc_Curves_Hull",
        DocCurvesHullCmd()
    )
