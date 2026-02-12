import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher


from ghi_cell_alias_utils.cam_utility import mirror_ord2_coord1
from ghi_cell_alias_utils.cam_rear_t_hull_intersec import rt_hull_inter_cell_mapping
from ghi_cell_alias_utils.cam_rear_t_deck_intersec import rt_deck_inter_cell_mapping
from ghi_varset_utils.ghi_varset_creation import varset_validate



def rear_transom_creation(doc_name, body_name, hc_type):
    # Raccolgo i dati dai varset
    doc = App.ActiveDocument
    rthi_points = []
    rtdi_points = []

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

    rthi_valid_values = varset_validate(rt_hull_inter_cell_mapping(), doc_name, body_name)
    rtdi_valid_values = varset_validate(rt_deck_inter_cell_mapping(), doc_name, body_name)
    
    ordered_rthi_values = {}
    ordered_rtdi_values = {}
    ordered_rthi_values['RT_HI'] = mirror_ord2_coord1(rthi_valid_values['RT_HI'], 'y', 'x', 'y')
    ordered_rtdi_values['RT_DI'] = mirror_ord2_coord1(rtdi_valid_values['RT_DI'], 'y', 'x', 'y')
    rthi_valid_values = ordered_rthi_values
    rtdi_valid_values = ordered_rtdi_values
    for key in rthi_valid_values['RT_HI']:
        point = doc.addObject("Part::Vertex", "RT_HI_" + str(key))
        point.X = rthi_valid_values['RT_HI'][key]['y']
        point.Y = rthi_valid_values['RT_HI'][key]['x']*(-1)
        point.Z = rthi_valid_values['RT_HI'][key]['z']
        App.activeDocument().getObject("Hull_RearTransom").addObject(App.activeDocument().getObject("RT_HI_" + str(key)))
        rthi_point = doc.getObject("RT_HI_" + str(key))
        rthi_points.append(rthi_point.Shape.Vertexes[0].Point)
    for key in rtdi_valid_values['RT_DI']:
        point = doc.addObject("Part::Vertex", "RT_DI_" + str(key))
        point.X = rtdi_valid_values['RT_DI'][key]['y']
        point.Y = rtdi_valid_values['RT_DI'][key]['x']*(-1)
        point.Z = rtdi_valid_values['RT_DI'][key]['z']
        App.activeDocument().getObject("Hull_RearTransom").addObject(App.activeDocument().getObject("RT_DI_" + str(key)))
        rtdi_point = doc.getObject("RT_DI_" + str(key))
        rtdi_points.append(rtdi_point.Shape.Vertexes[0].Point)
    doc.recompute()
    rthi_before = len(rthi_points)
    rthi_points = _dedup_points(rthi_points)
    if len(rthi_points) < rthi_before:
        App.Console.PrintMessage(
            f"Rear transom hull: removed {rthi_before - len(rthi_points)} duplicate points, now {len(rthi_points)} points.\n"
        )
    if len(rthi_points) < 2:
        App.Console.PrintError(
            f"Rear transom hull interpolation skipped: need at least 2 points, got {len(rthi_points)}.\n"
        )
        return
    rtdi_before = len(rtdi_points)
    rtdi_points = _dedup_points(rtdi_points)
    if len(rtdi_points) < rtdi_before:
        App.Console.PrintMessage(
            f"Rear transom deck: removed {rtdi_before - len(rtdi_points)} duplicate points, now {len(rtdi_points)} points.\n"
        )
    if len(rtdi_points) < 2:
        App.Console.PrintError(
            f"Rear transom deck interpolation skipped: need at least 2 points, got {len(rtdi_points)}.\n"
        )
        return
    # liste punti pronte

    #creazione linee interpolate

    #hull intersection curve
    if hc_type == 0:    # non dritto ma stondato
        rthi_curve = Part.BSplineCurve()
        try:
            rthi_curve.interpolate(rthi_points)
        except Exception as exc:  # Standard_ConstructionError and similar
            App.Console.PrintError(
                f"Rear transom hull interpolation failed: {exc}\nPoints: {rthi_points}\n"
            )
            return
        S1 = Part.Shape([rthi_curve])
        W = Part.Wire(S1.Edges)
        obj = App.ActiveDocument.addObject("Part::Feature", "RT_HI_Curve")
        obj.Shape = W            
        App.activeDocument().getObject("Hull_Curves").addObject(App.activeDocument().getObject("RT_HI_Curve"))
    else:
        # tolgo il primo e l'ultio punto dalla lista
        if len(rthi_points) > 2:
            rthi_points_base = rthi_points[1:-1]
        line_1 = Part.LineSegment(rthi_points[0], rthi_points[1])
        line_2 = Part.LineSegment(rthi_points[-2], rthi_points[-1])
        curva = Part.BSplineCurve()
        try:
            curva.interpolate(rthi_points_base)
        except Exception as exc:  # Standard_ConstructionError and similar
            App.Console.PrintError(
                f"Rear transom hull interpolation failed: {exc}\nPoints: {rthi_points_base}\n"
            )
            return
        S1 = Part.Shape([line_1, curva, line_2])
        W = Part.Wire(S1.Edges)
        obj = App.ActiveDocument.addObject("Part::Feature", "RT_HI_Curve")
        obj.Shape = W
        App.activeDocument().getObject("Hull_Curves").addObject(App.activeDocument().getObject("RT_HI_Curve"))
    # deck intersection curve
    rtdi_curve = Part.BSplineCurve()
    try:
        rtdi_curve.interpolate(rtdi_points)
    except Exception as exc:  # Standard_ConstructionError and similar
        App.Console.PrintError(
            f"Rear transom deck interpolation failed: {exc}\nPoints: {rtdi_points}\n"
        )
        return
    S1 = Part.Shape([rtdi_curve])
    W = Part.Wire(S1.Edges)
    obj = App.ActiveDocument.addObject("Part::Feature", "RT_DI_Curve")
    obj.Shape = W
    App.activeDocument().getObject("Hull_Curves").addObject(App.activeDocument().getObject("RT_DI_Curve"))

