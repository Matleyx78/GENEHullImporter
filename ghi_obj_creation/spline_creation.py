# -*- coding: utf-8 -*-
"""
Utility per creare una Sketcher BSpline (spline) in FreeCAD.

Funzione principale:
 - create_sketch_spline(points=None, sketch_name='SplineSketch', doc=None, open_in_gui=True)

Esempio d'uso nella console Python di FreeCAD:
>>> import GENEHullImporter.ghi_obj_creation.spline_creation as sc
>>> sc.create_sketch_spline()
"""
from __future__ import annotations

try:
    import FreeCAD as App
    import FreeCADGui as Gui
    import Part
    from FreeCAD import Vector
except Exception:  # pragma: no cover - executed only inside FreeCAD
    raise ImportError("Questo script deve essere eseguito all'interno di FreeCAD")


def _to_vector(p):
    if isinstance(p, Vector):
        return p
    return Vector(float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0)


def create_sketch_spline(points=None, sketch_name='SplineSketch', doc=None, open_in_gui=True, 
                         straight_ends=False):
    """Crea uno Sketcher e aggiunge una BSpline costruita sui punti passati.

    - points: lista di tuple o `FreeCAD.Vector`. Se None, vengono usati punti d'esempio.
    - sketch_name: nome dell'oggetto Sketcher.
    - doc: documento FreeCAD in cui creare lo sketch. Se None, usa o crea `SplineDoc`.
    - open_in_gui: se True e l'interfaccia GUI è disponibile, apre lo sketch in modalità modifica.
    - straight_ends: se True, forza i segmenti iniziali e finali ad essere retti.

    Restituisce l'oggetto Sketcher creato.
    """
    if doc is None:
        doc = App.ActiveDocument or App.newDocument('SplineDoc')
    # assicurarsi che il documento sia attivo
    App.setActiveDocument(doc.Name)

    if points is None:
        points = [(0, 0, 0), (50, 0, 0), (50, 30, 0), (0, 30, 0)]

    poles = [_to_vector(p) for p in points]

    sk = doc.addObject('Sketcher::SketchObject', sketch_name)

    # creare una BSpline che interpola i punti
    bs = Part.BSplineCurve()
    
    if straight_ends and len(poles) >= 3:
        # Calcola tangenti iniziali e finali per avere segmenti retti
        initial_tangent = poles[1] - poles[0]
        final_tangent = poles[-1] - poles[-2]
        bs.interpolate(poles, InitialTangent=initial_tangent, FinalTangent=final_tangent)
    else:
        bs.interpolate(poles)
    
    shape = bs.toShape()

    # aggiunge la geometria allo sketch (senza chiudere la forma)
    sk.addGeometry(shape, False)

    doc.recompute()

    if open_in_gui:
        try:
            if Gui.updatingDisabled():
                pass
        except Exception:
            pass
        # aprire lo sketch in modalita' edit (se la GUI è presente)
        try:
            if Gui.ActiveDocument:
                Gui.Selection.clearSelection()
                Gui.ActiveDocument.setEdit(sk.Name)
        except Exception:
            # se non siamo in GUI, ignoriamo
            pass

    return sk


if __name__ == '__main__':
    create_sketch_spline()
