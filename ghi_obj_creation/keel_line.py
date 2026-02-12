import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher

from ghi_cell_alias_utils.cam_utility import ordina_per_due_coord
from ghi_cell_alias_utils.cam_keel_line import keel_line_cell_mapping
from ghi_varset_utils.ghi_varset_creation import varset_validate

def _dedup_points(points, tol=1e-6):
    # Drop consecutive duplicates that can break BSpline interpolation
    cleaned = []
    for pt in points:
        if not cleaned or not pt.isEqual(cleaned[-1], tol):
            cleaned.append(pt)
        else:
            App.Console.PrintMessage(
                f"Removed duplicate point at {pt} within tolerance {tol}\n"
            )
    return cleaned

def keel_line_creation(doc_name, body_name):
    # Raccolgo i dati dai varset
    doc = App.ActiveDocument
    kl_points = []
    kl_valid_values = varset_validate(keel_line_cell_mapping(), doc_name, body_name)
    ordered_kl_values = {}
    ordered_kl_values['keel_line'] = ordina_per_due_coord(kl_valid_values['keel_line'], 'x', 'z')
    kl_valid_values = ordered_kl_values
    for key in kl_valid_values['keel_line']:
        point = doc.addObject("Part::Vertex", "KL_" + str(key))
        point.X = 0
        point.Y = kl_valid_values['keel_line'][key]['x']*(-1)
        point.Z = kl_valid_values['keel_line'][key]['z']
        App.activeDocument().getObject("Hull_KeelLine").addObject(App.activeDocument().getObject("KL_" + str(key)))
        kl_point = doc.getObject("KL_" + str(key))
        kl_points.append(kl_point.Shape.Vertexes[0].Point)
    doc.recompute()
    kl_before = len(kl_points)
    kl_points = _dedup_points(kl_points)
    if len(kl_points) < kl_before:
        App.Console.PrintMessage(
            f"Removed {kl_before - len(kl_points)} duplicate points from keel line\n"
        )
    if len(kl_points) < 2:
        App.Console.PrintError(
            "Not enough unique points to create keel line. Need at least 2.\n"
        )
        return
    kl_curve = Part.BSplineCurve()
    try:
        kl_curve.interpolate(kl_points)
    except Exception as e:
        App.Console.PrintError(f"Error creating keel line BSpline: {e}\n")
        return
    S1 = Part.Shape([kl_curve])
    W = Part.Wire(S1.Edges)
    obj = doc.addObject("Part::Feature", "KeelLine_Curve")
    obj.Shape = W
    App.activeDocument().getObject("Hull_Curves").addObject(App.activeDocument().getObject("KeelLine_Curve"))
    doc.recompute()