import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher


from ghi_cell_alias_utils.cam_utility import mirror_ord2_coord1
from ghi_cell_alias_utils.cam_rear_t_hull_intersec import rt_hull_inter_cell_mapping
from ghi_cell_alias_utils.cam_rear_t_deck_intersec import rt_deck_inter_cell_mapping
from ghi_cell_alias_utils.cam_chine_and_sheer_line import chine_and_sheer_line_cell_mapping
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

def rear_transom_creation(doc_name, body_name, hc_type):
    # Raccolgo i dati dai varset
    doc = App.ActiveDocument
    sheer_points = {}
    sheer_points['Sheer_line'] = []
    if hc_type == 1:        #if chine, make also the chine
        chine_points = {}
        chine_points['Chine_line'] = []
    all_valid_values = varset_validate(chine_and_sheer_line_cell_mapping(), doc_name, body_name)
    for row_name in all_valid_values['Chine_and_Sheer_line']:
        sheer_points['Sheer_line'][row_name] = {}
        sheer_points['Sheer_line'][row_name]['x'] = all_valid_values['Chine_and_Sheer_line'][row_name]['x']
        sheer_points['Sheer_line'][row_name]['y'] = all_valid_values['Chine_and_Sheer_line'][row_name]['y']
        sheer_points['Sheer_line'][row_name]['z'] = all_valid_values['Chine_and_Sheer_line'][row_name]['z_s']
        if hc_type == 1:
            chine_points['Chine_line'][row_name] = {}
            chine_points['Chine_line'][row_name]['x'] = all_valid_values['Chine_and_Sheer_line'][row_name]['x']
            chine_points['Chine_line'][row_name]['y'] = all_valid_values['Chine_and_Sheer_line'][row_name]['y']
            chine_points['Chine_line'][row_name]['z'] = all_valid_values['Chine_and_Sheer_line'][row_name]['z_c']
    #   chine_points and sheer_points are VALID VALUES

    ordered_sheer_values = {}
    ordered_chine_values = {}
    ordered_sheer_values['Sheer_line'] = mirror_ord2_coord1(sheer_points['Sheer_line'], 'y', 'x', 'y')
    if hc_type == 1:
        ordered_chine_values['Chine_line'] = mirror_ord2_coord1(chine_points['Chine_line'], 'y', 'x', 'y')

    for key in ordered_sheer_values['Sheer_line']:
        point = doc.addObject("Part::Vertex", "Sheer_L_" + str(key))
        point.X = ordered_sheer_values['Sheer_line'][key]['y']
        point.Y = ordered_sheer_values['Sheer_line'][key]['x']*(-1)
        point.Z = ordered_sheer_values['Sheer_line'][key]['z']
        App.activeDocument().getObject("Hull_Chine_and_Sheer").addObject(App.activeDocument().getObject("Sheer_L_" + str(key)))
        sheer_point = doc.getObject("Sheer_L_" + str(key))
        sheer_points.append(sheer_point.Shape.Vertexes[0].Point)
    if hc_type == 1:
        for key in ordered_chine_values['Chine_line']:
            point = doc.addObject("Part::Vertex", "Chine_L_" + str(key))
            point.X = ordered_chine_values['Chine_line'][key]['y']
            point.Y = ordered_chine_values['Chine_line'][key]['x']*(-1)
            point.Z = ordered_chine_values['Chine_line'][key]['z']
            App.activeDocument().getObject("Hull_Chine_and_Sheer").addObject(App.activeDocument().getObject("Chine_L_" + str(key)))
            chine_point = doc.getObject("Chine_L_" + str(key))
            chine_points.append(chine_point.Shape.Vertexes[0].Point)
    doc.recompute()
    sheer_before = len(sheer_points)
    sheer_points = _dedup_points(sheer_points)
    if len(sheer_points) < sheer_before:
        App.Console.PrintMessage(
            f"Rear transom hull: removed {sheer_before - len(sheer_points)} duplicate points, now {len(sheer_points)} points.\n"
        )
    if len(sheer_points) < 2:
        App.Console.PrintError(
            f"Rear transom hull interpolation skipped: need at least 2 points, got {len(rthi_points)}.\n"
        )
        return
    if hc_type == 1:
        chine_before = len(chine_points)
        chine_points = _dedup_points(chine_points)
        if len(chine_points) < chine_before:
            App.Console.PrintMessage(
                f"Rear transom chine: removed {chine_before - len(chine_points)} duplicate points, now {len(chine_points)} points.\n"
            )
        if len(chine_points) < 2:
            App.Console.PrintError(
                f"Rear transom chine interpolation skipped: need at least 2 points, got {len(chine_points)}.\n"
            )
            return
    # liste punti pronte

    #creazione linee interpolate

    # sheer curve
    sheer_curve = Part.BSplineCurve()
    try:
        sheer_curve.interpolate(sheer_points)
    except Exception as exc:  # Standard_ConstructionError and similar
        App.Console.PrintError(
            f"Rear transom sheer interpolation failed: {exc}\nPoints: {sheer_points}\n"
        )
        return
    S1 = Part.Shape([sheer_curve])
    W = Part.Wire(S1.Edges)
    obj = App.ActiveDocument.addObject("Part::Feature", "Sheer_L_Curve")
    obj.Shape = W
    App.activeDocument().getObject("Hull_Curves").addObject(App.activeDocument().getObject("Sheer_L_Curve"))

    if hc_type == 1:
        chine_curve = Part.BSplineCurve()
        try:
            chine_curve.interpolate(chine_points)
        except Exception as exc:  # Standard_ConstructionError and similar
            App.Console.PrintError(
                f"Rear transom chine interpolation failed: {exc}\nPoints: {chine_points}\n"
            )
            return
        S1 = Part.Shape([chine_curve])
        W = Part.Wire(S1.Edges)
        obj = App.ActiveDocument.addObject("Part::Feature", "Chine_L_Curve")
        obj.Shape = W
        App.activeDocument().getObject("Hull_Curves").addObject(App.activeDocument().getObject("Chine_L_Curve"))
