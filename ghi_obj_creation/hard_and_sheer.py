import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher


from ghi_cell_alias_utils.cam_utility import mirror_ord2_coord1
from ghi_cell_alias_utils.cam_utility import mirror_ord2_coord1_inv
from ghi_cell_alias_utils.cam_utility import ordina_per_due_coord
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

def hard_and_sheer_creation(doc_name, body_name, hc_type):
    # Raccolgo i dati dai varset
    doc = App.ActiveDocument
    sheer_pts =[]
    chine_pts = []
    sheer_points = {}
    sheer_points['Sheer_line'] = {}
    if hc_type == 1:        #if chine, make also the chine
        chine_points = {}
        chine_points['Chine_line'] = {}
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
    ordered_sheer_values['Sheer_line'] = mirror_ord2_coord1_inv(sheer_points['Sheer_line'], 'x', 'y', 'y')
    if hc_type == 1:
        ordered_chine_values['Chine_line'] = mirror_ord2_coord1_inv(chine_points['Chine_line'], 'x', 'y', 'y')

    for key in ordered_sheer_values['Sheer_line']:
        point = doc.addObject("Part::Vertex", "Sheer_L_" + str(key))
        point.X = ordered_sheer_values['Sheer_line'][key]['y']
        point.Y = ordered_sheer_values['Sheer_line'][key]['x']*(-1)
        point.Z = ordered_sheer_values['Sheer_line'][key]['z']
        App.activeDocument().getObject("Hull_Chine_and_Sheer").addObject(App.activeDocument().getObject("Sheer_L_" + str(key)))
        sheer_point = doc.getObject("Sheer_L_" + str(key))
        sheer_pts.append(sheer_point.Shape.Vertexes[0].Point)
    if hc_type == 1:
        for key in ordered_chine_values['Chine_line']:
            point = doc.addObject("Part::Vertex", "Chine_L_" + str(key))
            point.X = ordered_chine_values['Chine_line'][key]['y']
            point.Y = ordered_chine_values['Chine_line'][key]['x']*(-1)
            point.Z = ordered_chine_values['Chine_line'][key]['z']
            App.activeDocument().getObject("Hull_Chine_and_Sheer").addObject(App.activeDocument().getObject("Chine_L_" + str(key)))
            chine_point = doc.getObject("Chine_L_" + str(key))
            chine_pts.append(chine_point.Shape.Vertexes[0].Point)
    doc.recompute()
    sheer_before = len(sheer_pts)
    sheer_pts = _dedup_points(sheer_pts)
    if len(sheer_pts) < sheer_before:
        App.Console.PrintMessage(
            f"Rear transom hull: removed {sheer_before - len(sheer_pts)} duplicate points, now {len(sheer_pts)} points.\n"
        )
    if len(sheer_pts) < 2:
        App.Console.PrintError(
            f"Rear transom hull interpolation skipped: need at least 2 points, got {len(sheer_pts)}.\n"
        )
        return
    if hc_type == 1:
        chine_before = len(chine_pts)
        chine_pts = _dedup_points(chine_pts)
        if len(chine_pts) < chine_before:
            App.Console.PrintMessage(
                f"Rear transom chine: removed {chine_before - len(chine_pts)} duplicate points, now {len(chine_pts)} points.\n"
            )
        if len(chine_pts) < 2:
            App.Console.PrintError(
                f"Rear transom chine interpolation skipped: need at least 2 points, got {len(chine_pts)}.\n"
            )
            return
    # liste punti pronte

    #creazione linee interpolate

    # sheer curve
    sheer_curve = Part.BSplineCurve()
    try:
        sheer_curve.interpolate(sheer_pts)
    except Exception as exc:  # Standard_ConstructionError and similar
        App.Console.PrintError(
            f"Rear transom sheer interpolation failed: {exc}\nPoints: {sheer_pts}\n"
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
            chine_curve.interpolate(chine_pts)
        except Exception as exc:  # Standard_ConstructionError and similar
            App.Console.PrintError(
                f"Rear transom chine interpolation failed: {exc}\nPoints: {chine_pts}\n"
            )
            return
        S1 = Part.Shape([chine_curve])
        W = Part.Wire(S1.Edges)
        obj = App.ActiveDocument.addObject("Part::Feature", "Chine_L_Curve")
        obj.Shape = W
        App.activeDocument().getObject("Hull_Curves").addObject(App.activeDocument().getObject("Chine_L_Curve"))
