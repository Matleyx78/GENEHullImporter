import FreeCAD as App
import Part

def topot_test(offset = 0):
    V1 = App.Vector(0 + offset, 10 + offset, 0)
    V2 = App.Vector(30 + offset, 10 + offset, 0)
    V3 = App.Vector(30 + offset, -10 + offset, 0)
    V4 = App.Vector(0 + offset, -10 + offset, 0)

    VC1 = App.Vector(-10 + offset, 0 + offset, 0)
    C1 = Part.Arc(V1, VC1, V4)
    VC2 = App.Vector(40 + offset, 0 + offset, 0)
    C2 = Part.Arc(V2, VC2, V3)

    L1 = Part.LineSegment(V1, V2)
    L2 = Part.LineSegment(V3, V4)

    S1 = Part.Shape([C1, L1, C2, L2])

    W = Part.Wire(S1.Edges)
    P = W.extrude(App.Vector(0, 0, 10))

    Part.show(P)