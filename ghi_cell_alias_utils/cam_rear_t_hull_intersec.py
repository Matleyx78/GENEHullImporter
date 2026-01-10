#   REAR TRANSOM HULL INTERSECTION
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
def rt_hull_inter_name():                         # section name and column letter
    name ={}
    for i in range(0,50):
        key = 'RT_HI_' + str(i)
        name[key] = {'x' :'A', 'y' : 'B', 'z' : 'C',}
    return name

def rt_hull_inter_rows():                         # row name and row number
    rows = {}
    for i in range(64,114):
        key = 'rw_' + str(i)
        rows[key] = i
    return rows

def rt_hull_inter_cell_mapping():
    Sections = {}
    name = rt_hull_inter_name()
    rows = rt_hull_inter_rows()
    for key1 in name:
        Sections[key1] = {}
        for key2 in rows:
            Sections[key1][key2] = {}
            Sections[key1][key2]['x'] = name[key1]['x'] + str(rows[key2])
            Sections[key1][key2]['y'] = name[key1]['y'] + str(rows[key2])
            Sections[key1][key2]['z'] = name[key1]['z'] + str(rows[key2])
    return Sections

def rt_hull_inter_value(spreadsheet):
    sec_value = {}
    section = rt_hull_inter_cell_mapping()
    for key1 in section:
        sec_value[key1] = {}
        for key2 in section[key1]:
            sec_value[key1][key2] = {}
            for key3 in section[key1][key2]:
                sec_value[key1][key2][key3] = spreadsheet.getContents(key1 + "_" + key2 + "_" + key3)
    return sec_value