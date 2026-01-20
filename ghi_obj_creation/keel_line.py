import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher

from ghi_cell_alias_utils.cam_hull_section import hull_section_name

def keel_line_point():
    lista_sezioni = hull_section_name()
    for key in lista_sezioni:
        #controllo se esiste il varset associato e, se esiste prendo i dati cor_x
        print(f'Creating keel line point for section: {key}')
        varset = App.ActiveDocument.getObject(key + '_Data')
        if varset:
            x_value = varset.getPropertyByName('cor_x_x')
            ky_value = varset.getPropertyByName('keel_y')
            kz_value = varset.getPropertyByName('keel_z')
            sy_value = varset.getPropertyByName('sheer_y')
            sz_value = varset.getPropertyByName('sheer_z')
            hy_value = varset.getPropertyByName('hard_y')
            hz_value = varset.getPropertyByName('hard_z')
