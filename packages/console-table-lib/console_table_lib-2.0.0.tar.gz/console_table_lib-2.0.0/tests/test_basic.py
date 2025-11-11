"""
Basis-Tests für Console Table Library
"""

import pytest
from console_table import create, Table


def test_create_table():
    """Test: Tabelle erstellen"""
    table = create(["Name", "Alter"])
    assert table._created is True
    assert table._headers == ["Name", "Alter"]


def test_add_row():
    """Test: Zeile hinzufügen"""
    table = create(["Name", "Alter"])
    table.add_row("Max", 28)
    assert len(table._rows) == 1
    assert table._rows[0] == ["Max", 28]


def test_display():
    """Test: Tabelle anzeigen"""
    table = create(["Name", "Alter"])
    table.add_row("Max", 28)
    # Sollte keine Exception werfen
    table.display()


def test_footer():
    """Test: Footer hinzufügen"""
    table = create(["Name", "Alter"])
    table.set_footer("Gesamt", 100)
    assert table._footer == ["Gesamt", 100]


def test_border_styles():
    """Test: Border-Stile"""
    table = create(["Test"])
    for style in ["single", "double", "rounded", "minimal", "none"]:
        table.set_border_style(style)
        assert table._style_manager._border_style == style


def test_alignment():
    """Test: Textausrichtung"""
    table = create(["Test"])
    for alignment in ["left", "center", "right"]:
        table.set_alignment(alignment)
        assert table._style_manager._alignment == alignment


def test_sort():
    """Test: Sortierung"""
    table = create(["Name", "Wert"])
    table.add_row("B", 2)
    table.add_row("A", 1)
    table.add_row("C", 3)
    table.sort(0)  # Sortiere nach Name
    table.display()  # Sollte keine Exception werfen


def test_filter():
    """Test: Filterung"""
    table = create(["Name", "Wert"])
    table.add_row("A", 1)
    table.add_row("B", 2)
    table.add_row("C", 3)
    table.filter(lambda row: row[1] > 1)
    table.display()  # Sollte keine Exception werfen


def test_csv_export_import(tmp_path):
    """Test: CSV Export/Import"""
    csv_file = tmp_path / "test.csv"
    
    # Export
    table = create(["Name", "Alter"])
    table.add_row("Max", 28)
    table.to_csv(str(csv_file))
    
    # Import
    table2 = create().from_csv(str(csv_file))
    assert table2._headers == ["Name", "Alter"]
    assert len(table2._rows) == 1


def test_json_export_import(tmp_path):
    """Test: JSON Export/Import"""
    json_file = tmp_path / "test.json"
    
    # Export
    table = create(["Name", "Alter"])
    table.add_row("Max", 28)
    table.to_json(str(json_file))
    
    # Import
    table2 = create().from_json(str(json_file))
    assert table2._headers == ["Name", "Alter"]
    assert len(table2._rows) == 1

