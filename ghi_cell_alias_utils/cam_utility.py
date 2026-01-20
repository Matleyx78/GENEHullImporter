
def ordina_per_una_coord(lista = list, coord = str):
    sorted_lista = dict(sorted(lista.items(), key=lambda item: item[1][coord]))
    nuova_lista={}
    i=1
    for key, value in sorted_lista.items():
        value['name'] = key
        nuova_lista[i]=value
        i += 1
    return nuova_lista

def ordina_per_due_coord(lista = list, coord1 = str, coord2 = str):
    sorted_lista = dict(sorted(lista.items(), key=lambda item: (-item[1][coord1], -item[1][coord2])))
    nuova_lista={}
    i=1
    for key, value in sorted_lista.items():
        value['name'] = key
        nuova_lista[i]=value
        i += 1
    return nuova_lista

def mirror_ord2_coord1(lista = list, coord1 = str, coord2 = str, coord_m = str):
    ordinata = ordina_per_due_coord(lista, coord1, coord2)
    totale_punti = len(ordinata)
    i = totale_punti + 1
    j = totale_punti -1 # -1 perche salto il punto 0 che è lo zero
    for j in range(totale_punti, 0, -1):
    # mirror di j su coord_m
        if ordinata[j][coord_m] != 0:
            mirrored_val ={}
            for key, value in ordinata[j].items():
                if key == coord_m:
                    mirrored_val[key] = float(value) * (-1)
                else:
                    if isinstance(value, float):
                        mirrored_val[key] = float(value)
                    else:
                        mirrored_val[key] = '-' + str(value)
            
            ordinata[i]=mirrored_val
            i += 1
    return ordinata