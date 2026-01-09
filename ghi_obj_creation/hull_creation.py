import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher

from ghi_cell_alias_utils.cam_hull_section import hull_section_rows
from ghi_cell_alias_utils.cam_hull_center_line import hull_center_line_rows

def hull_doc_creation(section_data):
    name = 'Hull'
    Hull = App.newDocument(name)
    App.setActiveDocument(name)       
    App.activeDocument().addObject("App::DocumentObjectGroup","Hull_Varset").Label="Hull_Varset" 
    App.activeDocument().addObject("App::DocumentObjectGroup","Hull_Sketch").Label="Hull_Sketch" 
    App.activeDocument().addObject("App::DocumentObjectGroup","Hull_Curves").Label="Hull_Curves" 
    for key1 in section_data:
        varset = App.activeDocument().addObject('App::VarSet',key1 + '_Data')
        App.activeDocument().getObject("Hull_Varset").addObject(App.activeDocument().getObject(key1 + '_Data'))
        for key2 in section_data[key1]:
            for key3, value in section_data[key1][key2].items():
                App.Console.PrintMessage(f'Impostazione {key1}_{key2}_{key3} a {value}\n')
                varset.addProperty('App::PropertyFloat', key2 + '_' + key3, 'Sections', '')
                # assegna la proprietà dinamicamente usando setattr
                setattr(varset, key2 + '_' + key3, float(value) * 10)  # moltiplica per 10 per convertire da cm a mm
    App.ActiveDocument=App.getDocument(name)
    Gui.ActiveDocument=Gui.getDocument(name)
    return name

def hull_body_creation():
    name = 'Carena'
    # Inizio Parte
    App.activeDocument().addObject('PartDesign::Body',name)
    App.ActiveDocument.getObject(name).Label = name
    App.ActiveDocument.getObject(name).AllowCompound = True
    # FineParte
    return name

def hull_section_sketch_creation(section, body_name):
    doc = App.ActiveDocument
    body = doc.getObject(body_name)
    if body is None:
        raise RuntimeError(f"Body '{body_name}' non trovato")

    for key1 in section:
        varset = doc.getObject(key1 + '_Data')

        sk_name = 'Sk_' + key1
        sketch = App.ActiveDocument.addObject('Sketcher::SketchObject', sk_name)

        try:
            body.addObject(sketch)
        except Exception:
            pass

        origin = body.getObject('Origin') or getattr(body, 'Origin', None)
        if origin:
            sketch.AttachmentSupport = (origin, ['XZ_Plane'])
            sketch.AttachmentOffset = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,0,0),0))
            sketch.setExpression('.AttachmentOffset.Base.z', key1 + '_Data.cor_x_x')
        sketch.MapMode = 'FlatFace'
        point_creation_sketch_section(sketch,body.Name,varset)
        App.activeDocument().getObject("Hull_Sketch").addObject(App.activeDocument().getObject(sk_name))

def hull_center_line_sketch_creation(section, body_name):
    doc = App.ActiveDocument
    body = doc.getObject(body_name)
    if body is None:
        raise RuntimeError(f"Body '{body_name}' non trovato")

    for key1 in section:
        varset = doc.getObject(key1 + '_Data')

        sk_name = 'Sk_' + key1
        sketch = App.ActiveDocument.addObject('Sketcher::SketchObject', sk_name)

        try:
            body.addObject(sketch)
        except Exception:
            pass

        origin = body.getObject('Origin') or getattr(body, 'Origin', None)
        if origin:
            sketch.AttachmentSupport = (origin, ['YZ_Plane'])
            sketch.AttachmentOffset = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,1,0),180))
        sketch.MapMode = 'FlatFace'
        point_creation_sketch_center_line(sketch,body.Name,varset)
        App.activeDocument().getObject("Hull_Sketch").addObject(App.activeDocument().getObject(sk_name))

def point_creation_sketch_section(sketch,body,varset):    
    body = App.ActiveDocument.getObject(body)
    ActiveSketch = body.getObject(sketch.Name)
    punto = 1
    lastGeoId = len(ActiveSketch.Geometry)    
    geoList = []
    for punto in range(1,23,1):
        coord = punto * 10
        geoList.append(Part.Point(App.Vector(coord,coord,0)))
        geoList.append(Part.Point(App.Vector(-coord,coord,0)))    
    geoList.append(Part.Point(App.Vector(5,5,0)))
    ActiveSketch.addGeometry(geoList,False)
    del geoList

    rows = hull_section_rows()
    index_point = 0
    
    constraintList = []
    
    for key in rows:
        prop = key
        next_constraint_id = len(ActiveSketch.Constraints)
        ActiveSketch.addConstraint(Sketcher.Constraint('DistanceX', -1, 1, index_point, 1, 250))  # -1,1 è l'origine, 0,1  è il punto geolist0 tuttobordo(1)
        ActiveSketch.setExpression(f'Constraints[{next_constraint_id}]', varset.Name + '.' + prop + '_y')
        next_constraint_id = len(ActiveSketch.Constraints)
        ActiveSketch.addConstraint(Sketcher.Constraint('DistanceY', -1, 1, index_point, 1, -250))
        ActiveSketch.setExpression(f'Constraints[{next_constraint_id}]', varset.Name + '.' + prop + '_z')
        index_point = index_point + 1
        if index_point != 45:
            next_constraint_id = len(ActiveSketch.Constraints)
            ActiveSketch.addConstraint(Sketcher.Constraint('DistanceX', -1, 1, index_point, 1, 250))  # -1,1 è l'origine, 0,1  è il punto geolist0 tuttobordo(1)
            ActiveSketch.setExpression(f'Constraints[{next_constraint_id}]', '-' + varset.Name + '.' + prop + '_y')
            next_constraint_id = len(ActiveSketch.Constraints)
            ActiveSketch.addConstraint(Sketcher.Constraint('DistanceY', -1, 1, index_point, 1, -250))
            ActiveSketch.setExpression(f'Constraints[{next_constraint_id}]', varset.Name + '.' + prop + '_z')
            index_point = index_point + 1

def point_creation_sketch_center_line(sketch,body,varset):    
    body = App.ActiveDocument.getObject(body)
    ActiveSketch = body.getObject(sketch.Name)
    punto = 1
    lastGeoId = len(ActiveSketch.Geometry)    
    geoList = []
    for punto in range(1,20,1):
        coord = punto * 10
        geoList.append(Part.Point(App.Vector(coord,coord,0)))
    ActiveSketch.addGeometry(geoList,False)
    del geoList

    rows = hull_center_line_rows()
    index_point = 0
    
    constraintList = []
    
    for key in rows:
        prop = key
        next_constraint_id = len(ActiveSketch.Constraints)
        ActiveSketch.addConstraint(Sketcher.Constraint('DistanceX', -1, 1, index_point, 1, index_point * 100))  # -1,1 è l'origine, 0,1  è il punto geolist0 tuttobordo(1)
        ActiveSketch.setExpression(f'Constraints[{next_constraint_id}]', varset.Name + '.' + prop + '_x')
        next_constraint_id = len(ActiveSketch.Constraints)
        ActiveSketch.addConstraint(Sketcher.Constraint('DistanceY', -1, 1, index_point, 1, index_point * 100 * -1))
        ActiveSketch.setExpression(f'Constraints[{next_constraint_id}]', varset.Name + '.' + prop + '_z')
        index_point = index_point + 1