# GeneHull Logic Module

Replica Python del foglio di calcolo **Gene-Hull ODS** (file Sailboat 3.4).

## Overview

Questo modulo fornisce strumenti per:
- **Leggere** il file Gene-Hull ODS (input + output sheets)
- **Replicare** i calcoli geometrici e idrostatici della carena
- **Esportare** i risultati in JSON o CSV

## Struttura

- `gene_hull_calculator.py`: Core module con parser ODS, formula evaluator, e calculator
- `ods_formula_extractor.py`: Strumento di analisi per estrarre e comprendere le formule
- `__init__.py`: Package init file

## Uso

### Lettura e calcolo

```python
from ghi_logic import GeneHullCalculator

ods_path = "path/to/Gene-Hull Sailboat 3.4_2025 02.ods"
calc = GeneHullCalculator(ods_path)

# Compute all offsets
offsets = calc.compute_offsets()

# Export to JSON
calc.export_offsets("offsets.json", format_type="json")

# Or CSV
calc.export_offsets("offsets.csv", format_type="csv")
```

### Analisi delle formule

```python
python ods_formula_extractor.py "path/to/Gene-Hull Sailboat 3.4_2025 02.ods"
```

Questo produce un report con:
- Numero di formule totali
- Tipi di formule (ARITHMETIC, MULTIPLY/DIVIDE, OTHER)
- Esempi di primi riferimenti

## Valutazione Fattibilità

**STATUS: ALTAMENTE REPLICABILE** ✓

- **4.234 formule** nel foglio "Offsets x,y,z"
- **99% sono ARITHMETIC** (4.117 formule)
- Le formule sono principalmente **riferimenti diretti** da celle del foglio input "Gene-Hull"
- Esempi: `of:=['Gene-Hull'.B715]`, `of:=['Gene-Hull'.B714]+5`, etc.

**NO formule complesse:**
- No `SUM` di range
- No `IF` condizionali complesse
- No `AVERAGE`, `MAX`, `MIN`
- No `VLOOKUP`, `INDEX`, `MATCH`

**Conseguenza:** La replica in Python è diretta. Il calcolatore semplicemente:
1. Legge il foglio input (Gene-Hull)
2. Estrae ogni formula dal foglio output (Offsets x,y,z)
3. Sostituisce i riferimenti `[Sheet.Cell]` con i valori dalle celle input
4. Valuta l'espressione aritmetica risultante
5. Salva il risultato

## Dipendenze

```
odfpy>=1.4.1
```

## Note di Implementazione

1. **Parsing formula ODF**: Le formule ODF usano la sintassi `[Sheet.Cell]` per i riferimenti. Sono estratte via regex.
2. **Valutazione sicura**: `eval()` è usata con un contesto vuoto per sicurezza (produzione dovrebbe usare `ast.literal_eval` o un parser custom).
3. **Cache**: I valori computati sono messi in cache per evitare ricalcoli.
4. **Cross-sheet**: I riferimenti tra fogli ("Gene-Hull" → "Offsets x,y,z") sono risolti automaticamente.

## Prossimi step

- Aggiungere supporto per range (e.g., `SUM([Gene-Hull.A1:A10])`)
- Implementare funzioni ODF standard (SUM, AVERAGE, IF, etc.)
- Validazione e test contro valori noti dal foglio
- Caching e optimizzazione per performance

---

**Author:** GeneHull Python Replica  
**Version:** 0.1.0  
**Status:** Early Development
