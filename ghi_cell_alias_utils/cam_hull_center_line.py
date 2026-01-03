#   output:
#   list['name_section']['row_name_or_number']['coord'] = cell number and row
#
#   example:
#   list['C1']['l_15']['y'] = 'G15'
#   list['C1']['l_15']['z'] = 'H15'
#
#   Alias:
#       C1_l_15_y
#       C1_l_15_z
#   VarSet:
#      name: C1_Data
#        property:
#          l_15_y: value of G15
#          l_15_z: value of G15
def hull_center_line_name():                         # section name and column letter
    name ={}
    name['Cent_line'] = {'x' :'L', 'z' : 'M',}
    return name

def hull_center_line_rows():                         # row name and row number
    rows = {
        'X_p_ar': 118,
        'Car2': 119,
        'Car1': 120,
        'C0': 121,
        'C1': 122,
        'C2': 123,
        'C3': 124,
        'C4': 125,
        'C5': 126,
        'C6': 127,
        'C7': 128,
        'C8': 129,
        'C9': 130,
        'C95': 131,
        'C99': 132,
        'C10': 133,
        'Cav1': 134,
        'Cav2': 135,
        'Bow': 136,
    }
    return rows

def hull_center_line_cell_mapping():
    Sections = {}
    name = hull_center_line_name()
    rows = hull_center_line_rows()
    for key1 in name:
        Sections[key1] = {}
        for key2 in rows:
            Sections[key1][key2]['x'] = name[key1]['x'] + str(rows[key2])
            Sections[key1][key2]['z'] = name[key1]['z'] + str(rows[key2])
    return Sections

def hull_center_line_value(spreadsheet):
    sec_value = {}
    section = hull_center_line_cell_mapping()
    for key1 in section:
        sec_value[key1] = {}
        for key2 in section[key1]:
            sec_value[key1][key2] = {}
            for key3 in section[key1][key2]:
                sec_value[key1][key2][key3] = spreadsheet.getContents(key1 + "_" + key2 + "_" + key3)
    return sec_value