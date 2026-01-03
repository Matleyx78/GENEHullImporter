def section_cell_mapping():
    Sezioni = {}
    name = section_name()
    rows = row_sheet()
    for key1 in name:
        Sezioni[key1] = {}
        Sezioni[key1]['x'] = name[key1]['z'] + '10'
        for key2 in rows:
            Sezioni[key1][key2 + '_y'] = name[key1]['y'] + str(rows[key2])
            Sezioni[key1][key2 + '_z'] = name[key1]['z'] + str(rows[key2])
    return Sezioni

def section_name():
    name ={}
    name['Car2'] = {'y' :'C', 'z' : 'D',}
    name['C0'] = {'y' :'E', 'z' : 'F',}
    name['C1'] = {'y' :'G', 'z' : 'H',}
    name['C2'] = {'y' :'I', 'z' : 'J',}
    name['C3'] = {'y' :'K', 'z' : 'L',}
    name['C4'] = {'y' :'M', 'z' : 'N',}
    name['C5'] = {'y' :'O', 'z' : 'P',}
    name['C6'] = {'y' :'Q', 'z' : 'R',}
    name['C7'] = {'y' :'S', 'z' : 'T',}
    name['C8'] = {'y' :'U', 'z' : 'V',}
    name['C9'] = {'y' :'W', 'z' : 'X',}
    name['C95'] = {'y' :'Y', 'z' : 'Z',}
    name['C99'] = {'y' :'AA', 'z' : 'AB',}
    name['C10'] = {'y' :'AC', 'z' : 'AD',}
    name['Cav1'] = {'y' :'AE', 'z' : 'AF',}
    name['Cav2'] = {'y' :'AG', 'z' : 'AH',}
    return name

def row_sheet():
    rows = {
        'sheer': 13,
        'hard': 14,
        'l_15': 15,
        'l_16': 16,
        'l_17': 17,
        'l_18': 18,
        'l_19': 19,
        'l_20': 20,
        'l_21': 21,
        'l_22': 22,
        'l_23': 23,
        'l_24': 24,
        'l_25': 25,
        'l_26': 26,
        'l_27': 27,
        'l_28': 28,
        'l_29': 29,
        'l_30': 30,
        'l_31': 31,
        'l_32': 32,
        'l_33': 33,
        'l_34': 34,
        'keel': 35,
    }
    return rows

def section_value(spreadsheet):
    sec_value = {}
    section = section_cell_mapping()
    for key1 in section:
        sec_value[key1] = {}
        for key2 in section[key1]:
            sec_value[key1][key2] = spreadsheet.getContents(key1 + "_" + key2)
    return sec_value