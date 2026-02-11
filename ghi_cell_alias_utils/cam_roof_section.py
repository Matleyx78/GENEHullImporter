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
def roof_section_name():                         # section name and column letter
    name ={}
    name['rs_C3'] = {'y' :'A', 'z' : 'B',}
    name['rs_C4'] = {'y' :'C', 'z' : 'D',}
    name['rs_C5'] = {'y' :'E', 'z' : 'F',}
    name['rs_C6'] = {'y' :'G', 'z' : 'H',}
    name['rs_C7'] = {'y' :'I', 'z' : 'J',}
    name['rs_C8'] = {'y' :'K', 'z' : 'L',}
    return name

def roof_section_rows():                         # row name and row number
    rows = {
        'l_250': 250,
        'l_251': 251,
        'l_252': 252,
        'l_253': 253,
        'l_254': 254,
        'l_255': 255,
        'l_256': 256,
        'l_257': 257,
        'l_258': 258,
        'l_259': 259,
        'l_260': 260,
    }
    return rows

def roof_section_cell_mapping():
    Sections = {}
    name = roof_section_name()
    rows = roof_section_rows()
    for key1 in name:
        Sections[key1] = {}
        Sections[key1]['cor_x'] = {}
        Sections[key1]['cor_x']['x'] = name[key1]['z'] + '248'
        for key2 in rows:
            Sections[key1][key2] = {}
            Sections[key1][key2]['y'] = name[key1]['y'] + str(rows[key2])
            Sections[key1][key2]['z'] = name[key1]['z'] + str(rows[key2])
    return Sections

def roof_section_value(spreadsheet):
    sec_value = {}
    section = roof_section_cell_mapping()
    for key1 in section:
        sec_value[key1] = {}
        for key2 in section[key1]:
            sec_value[key1][key2] = {}
            for key3 in section[key1][key2]:
                sec_value[key1][key2][key3] = spreadsheet.getContents(key1 + "_" + key2 + "_" + key3)   # getContents(C0_sheer_y)
    return sec_value