import FreeCAD as App

#   ALL SECTION NAME
from ghi_cell_alias_utils.cam_hull_section import hull_section_cell_mapping
from ghi_cell_alias_utils.cam_hull_center_line import hull_center_line_cell_mapping
from ghi_cell_alias_utils.cam_rear_t_deck_intersec import rt_deck_inter_cell_mapping
from ghi_cell_alias_utils.cam_rear_t_hull_intersec import rt_hull_inter_cell_mapping
#   ALL SECTION VALUE
from ghi_cell_alias_utils.cam_hull_section import hull_section_value
from ghi_cell_alias_utils.cam_hull_center_line import hull_center_line_value
from ghi_cell_alias_utils.cam_rear_t_deck_intersec import rt_deck_inter_value
from ghi_cell_alias_utils.cam_rear_t_hull_intersec import rt_hull_inter_value

def varset_creation(sheet):
    all_section_data = {}
    all_section_data['hs'] = {}
    all_section_data['hs']['cel_map'] = hull_section_cell_mapping()
    all_section_data['hs']['cel_val'] = hull_section_value(sheet)
    all_section_data['hcl'] = {}
    all_section_data['hcl']['cel_map'] = hull_center_line_cell_mapping()
    all_section_data['hcl']['cel_val'] = hull_center_line_value(sheet)
    all_section_data['rthi'] = {}
    all_section_data['rthi']['cel_map'] = rt_hull_inter_cell_mapping()
    all_section_data['rthi']['cel_val'] = rt_hull_inter_value(sheet)
    all_section_data['rtde'] = {}
    all_section_data['rtde']['cel_map'] = rt_deck_inter_cell_mapping()
    all_section_data['rtde']['cel_val'] = rt_deck_inter_value(sheet)
    valid_sec = {}
    # per ogni sezione verifico che i dati siano numerici
    for gruppo in all_section_data:     # es. 'hs', 'hcl', 'rtde', 'rthi'
        cel_map = all_section_data[gruppo]['cel_map']
        cel_val = all_section_data[gruppo]['cel_val']
        for sec_name in cel_map:    # es. 'C0', 'C1', 'Cent_line', 'RT_Deck_Int', 'RT_Hull_Int'
            valid_sec[sec_name] = {}
            for row_name in cel_map[sec_name]:   # es. 'sheer',
                row_valid = True
                for coord in cel_map[sec_name][row_name]:   # es. 'x', 'y', 'z'
                    val = cel_val[sec_name][row_name][coord]
                    try:
                        float(val)
                    except ValueError:
                        row_valid = False
                        print(f'Skipping section {sec_name} due to non-numeric value at {sec_name}_{row_name}_{coord}: {val}')
                if row_valid:   
                    valid_sec[sec_name][row_name] = {}             
                    for coord in cel_map[sec_name][row_name]:   # es. 'x', 'y', 'z'
                        valid_sec[sec_name][row_name][coord] = cel_val[sec_name][row_name][coord]
    # crazione di due varset per ogni sezione: uno con solo i nomi, uno con i valori
    for sec_name in valid_sec:        
        varset_name = App.activeDocument().addObject('App::VarSet',sec_name + '_name')
        App.activeDocument().getObject("Hull_Varset").addObject(App.activeDocument().getObject(sec_name + '_name'))
        varset_data = App.activeDocument().addObject('App::VarSet',sec_name + '_data')
        App.activeDocument().getObject("Hull_Varset").addObject(App.activeDocument().getObject(sec_name + '_data'))
        for row_name in valid_sec[sec_name]:                 # Example: valid_sec['C0']
            varset_name.addProperty('App::PropertyString', row_name, 'Sections', '')
            setattr(varset_name, row_name, str(row_name))
            for key3, value in valid_sec[sec_name][row_name].items():
                App.Console.PrintMessage(f'Impostazione {sec_name}_{row_name}_{key3} a {value}\n')
                varset_data.addProperty('App::PropertyFloat', row_name + '_' + key3, 'Sections', '')
                # assegna la proprietà dinamicamente usando setattr
                setattr(varset_data, row_name + '_' + key3, float(value) * 10)  # moltiplica per 10 per convertire da cm a mm

