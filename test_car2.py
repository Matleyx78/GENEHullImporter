from ghi_hull_calc.hull_calculator import HullCalculator
import csv

# Test Car2 generation
c = HullCalculator()
c.compute()
c.export_csv('test_car2.csv')

print(f'Generati {len(c.outputs)} punti totali')

# Count Car2 points
with open('test_car2.csv') as f:
    reader = csv.DictReader(f)
    car2_rows = [r for r in reader if r['Section'] == 'Car2']

print(f'\nPunti Car2: {len(car2_rows)}')
print('\nPrimi 5 punti Car2:')
for r in car2_rows[:5]:
    print(f"  {r['Section']}, X={r['X(cm)']}, Y={r['Y(cm)']}, Z={r['Z(cm)']}")

# Show all sections
with open('test_car2.csv') as f:
    reader = csv.DictReader(f)
    sections = set(r['Section'] for r in reader)

print(f'\nTutte le sezioni generate ({len(sections)}):')
print(', '.join(sorted(sections)))
