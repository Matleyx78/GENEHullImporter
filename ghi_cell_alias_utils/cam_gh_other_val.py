#   Other values
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
def other_values_name():                # section name and column letter
    name ={}
    name['hard_chine_type'] = {'val' :'D'}
    return name

def other_values_rows():                         # row name and row number
    rows = {
        'D2': 2,
    }
    return rows

def other_values_cell_mapping():
    Sections = {}
    name = other_values_name()
    rows = other_values_rows()
    for key1 in name:
        Sections[key1] = {}
        for key2 in rows:
            Sections[key1][key2] = {}
            Sections[key1][key2]['val'] = name[key1]['val'] + str(rows[key2])
    return Sections

def other_values_value(spreadsheet):
    sec_value = {}
    section = other_values_cell_mapping()
    for key1 in section:
        sec_value[key1] = {}
        for key2 in section[key1]:
            sec_value[key1][key2] = {}
            for key3 in section[key1][key2]:
                # print(f'Getting value for {key1}_{key2}_{key3}')
                sec_value[key1][key2][key3] = spreadsheet.getContents(key1 + "_" + key2 + "_" + key3)
    return sec_value