import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher

from ghi_cell_alias_utils.cam_utility import ordina_per_due_coord
from ghi_cell_alias_utils.cam_hull_center_line import hull_center_line_cell_mapping
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

def center_line_creation(doc_name, body_name):
    # Raccolgo i dati dai varset
    doc = App.ActiveDocument
    cl_points = []
    cl_valid_values = varset_validate(hull_center_line_cell_mapping(), doc_name, body_name)
    ordered_cl_values = {}
    ordered_cl_values['Cent_line'] = ordina_per_due_coord(cl_valid_values['Cent_line'], 'x', 'z')
    cl_valid_values = ordered_cl_values
    for key in cl_valid_values['Cent_line']:
        point = doc.addObject("Part::Vertex", "CL_" + str(key))
        point.X = 0
        point.Y = cl_valid_values['Cent_line'][key]['x']*(-1)
        point.Z = cl_valid_values['Cent_line'][key]['z']
        App.activeDocument().getObject("Hull_CenterLine").addObject(App.activeDocument().getObject("CL_" + str(key)))
        cl_point = doc.getObject("CL_" + str(key))
        cl_points.append(cl_point.Shape.Vertexes[0].Point)
    doc.recompute()
    cl_before = len(cl_points)
    cl_points = _dedup_points(cl_points)
    if len(cl_points) < cl_before:
        App.Console.PrintMessage(
            f"Removed {cl_before - len(cl_points)} duplicate points from center line\n"
        )
    if len(cl_points) < 2:
        App.Console.PrintError(
            "Not enough unique points to create center line. Need at least 2.\n"
        )
        return
    cl_curve = Part.BSplineCurve()
    try:
        cl_curve.interpolate(cl_points)
    except Exception as e:
        App.Console.PrintError(f"Error creating center line BSpline: {e}\n")
        return
    S1 = Part.Shape([cl_curve])
    W = Part.Wire(S1.Edges)
    obj = doc.addObject("Part::Feature", "CenterLine_Curve")
    obj.Shape = W
    App.activeDocument().getObject("Hull_Curves").addObject(App.activeDocument().getObject("CenterLine_Curve"))
    doc.recompute()