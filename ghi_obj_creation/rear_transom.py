import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher

from ghi_cell_alias_utils.cam_rear_t_hull_intersec import rt_hull_inter_cell_mapping
from ghi_cell_alias_utils.cam_rear_t_deck_intersec import rt_deck_inter_cell_mapping
from ghi_varset_utils.ghi_varset_creation import varset_validate



def rear_transom_creation(doc_name, body_name):
    # Raccolgo i dati dai varset
    doc = App.ActiveDocument
    rthi_points = []
    rtdi_points = []
    rthi_valid_values = varset_validate(rt_hull_inter_cell_mapping(), doc_name, body_name)
    rtdi_valid_values = varset_validate(rt_deck_inter_cell_mapping(), doc_name, body_name)
    print (rthi_valid_values)
    for key in rthi_valid_values['RT_HI']:
        point = doc.addObject("Part::Vertex", "RT_HI_" + key)
        point.X = rthi_valid_values['RT_HI'][key]['y']
        point.Y = rthi_valid_values['RT_HI'][key]['x']*(-1)
        point.Z = rthi_valid_values['RT_HI'][key]['z']
        App.activeDocument().getObject("Hull_RearTransom").addObject(App.activeDocument().getObject("RT_HI_" + key))
        rthi_point = doc.getObject("RT_HI_" + key)
        rthi_points.append(rthi_point.Shape.Vertexes[0].Point)
        if rthi_valid_values['RT_HI'][key]['y'] != 0:
            point_mirror = doc.addObject("Part::Vertex", "RT_HI_Mirror_" + key)
            point_mirror.X = rthi_valid_values['RT_HI'][key]['y'] * (-1)
            point_mirror.Y = rthi_valid_values['RT_HI'][key]['x']*(-1)
            point_mirror.Z = rthi_valid_values['RT_HI'][key]['z']
            App.activeDocument().getObject("Hull_RearTransom").addObject(App.activeDocument().getObject("RT_HI_Mirror_" + key))
            rthi_point = doc.getObject("RT_HI_" + key)
            rthi_points.append(rthi_point.Shape.Vertexes[0].Point)
    for key in rtdi_valid_values['RT_DI']:
        point = doc.addObject("Part::Vertex", "RT_DI_" + key)
        point.X = rtdi_valid_values['RT_DI'][key]['y']
        point.Y = rtdi_valid_values['RT_DI'][key]['x']*(-1)
        point.Z = rtdi_valid_values['RT_DI'][key]['z']
        App.activeDocument().getObject("Hull_RearTransom").addObject(App.activeDocument().getObject("RT_DI_" + key))
        rtdi_point = doc.getObject("RT_DI_" + key)
        rtdi_points.append(rtdi_point.Shape.Vertexes[0].Point)
        if rtdi_valid_values['RT_DI'][key]['y'] != 0:
            point_mirror = doc.addObject("Part::Vertex", "RT_DI_Mirror_" + key)
            point_mirror.X = rtdi_valid_values['RT_DI'][key]['y'] * (-1)
            point_mirror.Y = rtdi_valid_values['RT_DI'][key]['x']*(-1)
            point_mirror.Z = rtdi_valid_values['RT_DI'][key]['z']
            App.activeDocument().getObject("Hull_RearTransom").addObject(App.activeDocument().getObject("RT_DI_Mirror_" + key))
            rtdi_point = doc.getObject("RT_DI_" + key)
            rtdi_points.append(rtdi_point.Shape.Vertexes[0].Point)
    doc.recompute()

    rthi_curve = Part.BSplineCurve()
    rthi_curve.interpolate(rthi_points)
    S1 = Part.Shape([rthi_curve])
    W = Part.Wire(S1.Edges)
    obj = App.ActiveDocument.addObject("Part::Feature", "RT_HI_Curve")
    obj.Shape = W            
    App.activeDocument().getObject("Hull_Curves").addObject(App.activeDocument().getObject("RT_HI_Curve"))

    rtdi_curve = Part.BSplineCurve()
    rtdi_curve.interpolate(rtdi_points) 
    S2 = Part.Shape([rtdi_curve])
    W2 = Part.Wire(S2.Edges)
    obj2 = App.ActiveDocument.addObject("Part::Feature", "RT_DI_Curve")
    obj2.Shape = W2
    App.activeDocument().getObject("Hull_Curves").addObject(App.activeDocument().getObject("RT_DI_Curve"))
    doc.recompute()