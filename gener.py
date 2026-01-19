lista = {}
lista['punto1'] ={'x': 12, 'y': 32, 'z': 47}
lista['punto2'] ={'x': 5, 'y': 16, 'z': 77}
lista['punto3'] ={'x': 2, 'y': 95, 'z': 310}

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