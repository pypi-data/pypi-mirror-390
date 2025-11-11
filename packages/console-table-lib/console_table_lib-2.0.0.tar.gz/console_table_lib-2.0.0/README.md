# Console Table Library

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Eine umfassende und dennoch **verdammt einfache** Python-Bibliothek zur Erstellung von gut formatierten Tabellen in der Konsole.

## ✨ Features

### 🎯 Kern-Features
- **Verdammt einfache API**: Minimalistisches Interface mit Method-Chaining
- **Automatische Spaltenbreiten**: Optimale Anpassung für beste Lesbarkeit
- **Verschiedene Border-Stile**: Single, Double, Rounded, Minimal, None
- **Textausrichtung**: Left, Center, Right
- **Sensible Defaults**: Funktioniert sofort ohne Konfiguration

### 🚀 Erweiterte Features
- **Farben & Themes**: Unterstützung für Rich-Farben und vordefinierte Themes
- **Footer**: Unterstützung für Tabellen-Footer
- **Sortierung**: Sortierung nach Spalten
- **Filterung**: Flexible Filterung von Zeilen
- **Pagination**: Seitennavigation für große Datensätze
- **Import/Export**: CSV und JSON Import/Export
- **Validierung**: Datenvalidierung (DataValidator)
- **Interaktivität**: Input-Handler für interaktive Features

## 📦 Installation

### Via pip (empfohlen)

```bash
pip install console-table
```

### Aus dem Quellcode

```bash
git clone https://github.com/yourusername/console-table.git
cd console-table
pip install -e .
```

### Dependencies

- Python 3.7+
- rich >= 13.0.0
- pandas >= 2.0.0

## 🚀 Schnellstart

### Einfachste Verwendung

```python
from console_table import create

# Einfachste Verwendung
create(["Name", "Alter", "Stadt"]) \
    .add_row("Max Mustermann", 28, "Berlin") \
    .add_row("Anna Schmidt", 32, "München") \
    .display()
```

**Ausgabe:**
```
┌────────────────┬───────┬─────────┐
│ Name           │ Alter │ Stadt   │
├────────────────┼───────┼─────────┤
│ Max Mustermann │ 28    │ Berlin  │
│ Anna Schmidt   │ 32    │ München │
└────────────────┴───────┴─────────┘
```

### Mit erweiterten Features

```python
from console_table import create

create(["Monat", "Umsatz", "Gewinn"]) \
    .set_colors(True) \
    .set_theme("colorful") \
    .add_row("Januar", 50000, 12000) \
    .add_row("Februar", 55000, 13500) \
    .add_row("März", 60000, 15000) \
    .set_footer("Gesamt", 165000, 40500) \
    .sort(1, reverse=True) \
    .display()
```

## 📚 Dokumentation

### Basis-Methoden

#### `create(headers=None)`
Erstellt eine neue Tabelle.

```python
table = create(["Spalte 1", "Spalte 2"])
# oder
table = create()  # ohne Header
```

#### `add_row(*args)`
Fügt eine Zeile zur Tabelle hinzu.

```python
table.add_row("Wert 1", "Wert 2", "Wert 3")
```

#### `set_footer(*args)`
Setzt einen Footer für die Tabelle.

```python
table.set_footer("Gesamt", 1000, 500)
```

#### `display()`
Zeigt die Tabelle in der Konsole an.

```python
table.display()
```

### Styling-Methoden

#### `set_border_style(style)`
Setzt den Border-Stil.

```python
table.set_border_style("single")   # Standard
table.set_border_style("double")   # Doppelte Linien
table.set_border_style("rounded")  # Abgerundete Ecken
table.set_border_style("minimal")  # Minimaler Stil
table.set_border_style("none")     # Keine Borders
```

#### `set_alignment(alignment)`
Setzt die Textausrichtung.

```python
table.set_alignment("left")    # Links (Standard)
table.set_alignment("center")  # Zentriert
table.set_alignment("right")   # Rechts
```

#### `set_colors(enabled=True)`
Aktiviert/deaktiviert Farben (benötigt `rich`).

```python
table.set_colors(True)   # Farben aktivieren
table.set_colors(False)  # Farben deaktivieren
```

#### `set_theme(theme_name)`
Setzt ein vordefiniertes Theme.

```python
table.set_theme("default")   # Standard-Theme
table.set_theme("dark")      # Dunkles Theme
table.set_theme("light")     # Helles Theme
table.set_theme("colorful")   # Buntes Theme
```

#### `color_row(row_index, color)`
Färbt eine bestimmte Zeile ein.

```python
table.color_row(0, "green")
table.color_row(1, "yellow")
```

#### `color_cell(row_index, col_index, color)`
Färbt eine bestimmte Zelle ein.

```python
table.color_cell(0, 2, "red")
```

### Datenmanipulation

#### `sort(column_index, reverse=False)`
Sortiert die Tabelle nach einer Spalte.

```python
table.sort(1)              # Sortiert nach Spalte 1 (aufsteigend)
table.sort(1, reverse=True) # Sortiert nach Spalte 1 (absteigend)
```

#### `filter(filter_func)`
Filtert Zeilen basierend auf einer Funktion.

```python
# Nur Zeilen mit "Berlin" in Spalte 2
table.filter(lambda row: row[2] == "Berlin")

# Nur Zeilen mit Wert > 100 in Spalte 1
table.filter(lambda row: row[1] > 100)
```

#### `clear_filter()`
Entfernt alle Filter.

```python
table.clear_filter()
```

#### `page(page_size)`
Aktiviert Pagination.

```python
table.page(10)  # Zeigt 10 Zeilen pro Seite
```

#### `next_page()` / `prev_page()`
Navigation zwischen Seiten.

```python
table.next_page()  # Nächste Seite
table.prev_page()  # Vorherige Seite
```

### Import/Export

#### `from_csv(filepath, has_header=True)`
Lädt Daten aus einer CSV-Datei.

```python
table = create().from_csv("data.csv")
```

#### `from_json(filepath)`
Lädt Daten aus einer JSON-Datei.

```python
table = create().from_json("data.json")
```

#### `to_csv(filepath)`
Exportiert die Tabelle nach CSV.

```python
table.to_csv("output.csv")
```

#### `to_json(filepath)`
Exportiert die Tabelle nach JSON.

```python
table.to_json("output.json")
```

## 📖 Beispiele

Siehe `example_advanced.py` für umfassende Beispiele aller Features.

## 🏗️ Projekt-Struktur

```
console-table/
├── console_table/          # Hauptpaket
│   ├── __init__.py         # Haupt-API
│   ├── table_generator.py  # Tabellengenerierung
│   ├── style_manager.py    # Styling-Verwaltung
│   ├── export_manager.py   # Import/Export
│   ├── data_validator.py   # Datenvalidierung
│   └── input_handler.py    # Eingabe-Verarbeitung
├── tests/                  # Tests
├── examples/               # Beispiel-Skripte
├── setup.py                # Setup-Konfiguration
├── pyproject.toml          # Modernes Python-Projekt
├── requirements.txt       # Dependencies
├── LICENSE                 # MIT License
└── README.md              # Diese Datei
```

## 🤝 Beitragen

Beiträge sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## 📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

## 🙏 Danksagungen

- [Rich](https://github.com/Textualize/rich) für die Farb-Unterstützung
- [Pandas](https://pandas.pydata.org/) für die Datenverarbeitung

## 📧 Kontakt

Bei Fragen oder Anregungen öffne bitte ein [Issue](https://github.com/yourusername/console-table/issues).

---

**Die Verwendung ist verdammt einfach!** 🚀
