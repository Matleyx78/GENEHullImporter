lista = {}
lista['punto1'] ={'x': 12, 'y': 32, 'z': 47}
lista['punto2'] ={'x': 5, 'y': 16, 'z': 77}
lista['punto3'] ={'x': 2, 'y': 95, 'z': 310}
lista['punto4'] ={'x': 5, 'y': 15, 'z': 27}
lista['punto5'] ={'x': 0, 'y': 15, 'z': 27}


print('Ordino in base al valore di x:')
sorted_lista = dict(sorted(lista.items(), key=lambda item: item[1]['x']))
for key, value in sorted_lista.items():
    print(f'{key}: {value}')

print('Ordino in base al valore di y:')
sorted_lista = dict(sorted(lista.items(), key=lambda item: item[1]['y']))  
for key, value in sorted_lista.items():
    print(f'{key}: {value}')

print('Ordino in base al valore di z:')
sorted_lista = dict(sorted(lista.items(), key=lambda item: item[1]['z']))
for key, value in sorted_lista.items():
    print(f'{key}: {value}')

print('Ordino in base al valore di x. se è ugule, lo ordino in base al valore di y:')
sorted_lista = dict(sorted(lista.items(), key=lambda item: (item[1]['x'], item[1]['y'])))
nuova_lista={}
i=1
for key, value in sorted_lista.items():
    value['name'] = key
    nuova_lista[i]=value
    i += 1    
    print(f'{key}: {value}')


print('Ordino inverso in base al valore di x . se è ugule, lo ordino in base al valore di y:')
sorted_lista = dict(sorted(lista.items(), key=lambda item: (item[1]['x'], item[1]['y']), reverse=True))
nuova_lista={}
i=1
for key, value in sorted_lista.items():
    value['name'] = key
    nuova_lista[i]=value
    i += 1    
    print(f'{key}: {value}')

print('Aggiungo il mirror dei punti con x diversa da zero e poi li ordino in base a x dal piu grande al piu piccolo. se è uguale, lo ordindo in base a y dal piu piccolo al piu grande:')
sorted_lista = dict(sorted(lista.items(), key=lambda item: ( -item[1]['x'], -item[1]['y'])))
nuova_lista={}
i=1
for key, value in sorted_lista.items():
    value['name'] = key
    nuova_lista[i]=value
    i += 1    
    print(f'{key}: {value}')
totale_punti = len(nuova_lista)
# i è già il nuovo punto per continuare la lista, j è l'indice all'indietro per la lista precedente
j = totale_punti -1 # -1 perche salto il punto 0 che è lo zero
for j in range(totale_punti, 0, -1):
    # mirror di j su x
    if nuova_lista[j]['x'] != 0:
        mirrored_value = {'x': -nuova_lista[j]['x'], 'y': nuova_lista[j]['y'], 'z': nuova_lista[j]['z']}
        nuova_lista[i]=mirrored_value
        i += 1    
        # print(f'{j}_mirrored: {mirrored_value}')
for key, value in nuova_lista.items():
    print(f'{key}: {value}')

