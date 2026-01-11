# ODS Analyzer

Questo strumento analizza un file `.ods` (OpenDocument Spreadsheet), prendendo in considerazione il primo foglio (input) e l'ultimo foglio (output), ed estrae:
- Valori di input (celle senza formula) dal primo foglio
- Valori e formule dal foglio di output
- Riferimenti nelle formule per spiegare come gli output dipendono dagli input

Genera un report TXT (di default) con spiegazione di input, output e riferimenti nelle formule. Opzionalmente può creare un PDF se `reportlab` è installato.

## Requisiti
- Python 3.9+
- Pacchetti: `odfpy` (lettura ODS), `reportlab` (PDF facoltativo)

Installazione:
```bash
pip install odfpy reportlab
```

## Uso
```bash
python ods_analysis/ods_analyzer.py "C:/path/al/file.ods" --txt "C:/path/al/report.txt"
```
Senza `--txt`, produrrà `analysis_report.txt` nella stessa cartella dello script. In alternativa è possibile richiedere un PDF con `--pdf`.

## Note
- Le formule ODF sono lette dall'attributo `table:formula` (prefisso tipico `of:=...`).
- I riferimenti di cella in ODF usano la sintassi tra parentesi quadre, es. `[.A1]`, `[Foglio1.A1]`. Questo strumento estrae e normalizza tali riferimenti.
- Il riconoscimento automatico di coppie etichetta/valore (input) è basilare; potete affinare le regole nel codice se necessario.
