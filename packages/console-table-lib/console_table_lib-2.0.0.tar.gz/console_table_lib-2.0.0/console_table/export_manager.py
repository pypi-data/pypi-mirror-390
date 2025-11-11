"""
ExportManager - Verwaltet den Export von Tabellendaten in verschiedene Formate.
"""

import json
import csv
from typing import List, Optional


class ExportManager:
    """Verwaltet den Export von Tabellendaten."""
    
    def __init__(self):
        pass
    
    def to_csv(self, headers: Optional[List], rows: List[List], filepath: str, delimiter: str = ","):
        """
        Exportiert Daten als CSV-Datei.
        
        Args:
            headers: Liste von Headern (optional)
            rows: Liste von Zeilen
            filepath: Pfad zur Ausgabedatei
            delimiter: CSV-Trennzeichen
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=delimiter)
                
                if headers:
                    writer.writerow(headers)
                
                for row in rows:
                    writer.writerow(row)
        except Exception as e:
            raise IOError(f"Fehler beim CSV-Export: {str(e)}")
    
    def to_json(self, headers: Optional[List], rows: List[List], filepath: str, orient: str = "records"):
        """
        Exportiert Daten als JSON-Datei.
        
        Args:
            headers: Liste von Headern (optional)
            rows: Liste von Zeilen
            filepath: Pfad zur Ausgabedatei
            orient: JSON-Orientierung ("records", "values", "index")
        """
        try:
            data = []
            
            if headers:
                if orient == "records":
                    # Liste von Dictionaries
                    for row in rows:
                        record = {}
                        for i, header in enumerate(headers):
                            record[header] = row[i] if i < len(row) else None
                        data.append(record)
                elif orient == "values":
                    # Liste von Listen
                    data = {
                        "headers": headers,
                        "rows": rows
                    }
                else:  # index
                    # Dictionary mit Index als Key
                    for i, row in enumerate(rows):
                        record = {}
                        for j, header in enumerate(headers):
                            record[header] = row[j] if j < len(row) else None
                        data[i] = record
            else:
                data = rows
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        except Exception as e:
            raise IOError(f"Fehler beim JSON-Export: {str(e)}")
    
    def from_csv(self, filepath: str, delimiter: str = ",", has_header: bool = True):
        """
        Importiert Daten aus einer CSV-Datei.
        
        Args:
            filepath: Pfad zur CSV-Datei
            delimiter: CSV-Trennzeichen
            has_header: Ob die erste Zeile Header enthält
        
        Returns:
            (headers, rows) - Tuple mit Headern und Zeilen
        """
        try:
            headers = None
            rows = []
            
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter)
                
                if has_header:
                    headers = next(reader, None)
                
                for row in reader:
                    rows.append(row)
            
            return headers, rows
        except Exception as e:
            raise IOError(f"Fehler beim CSV-Import: {str(e)}")
    
    def from_json(self, filepath: str):
        """
        Importiert Daten aus einer JSON-Datei.
        
        Args:
            filepath: Pfad zur JSON-Datei
        
        Returns:
            (headers, rows) - Tuple mit Headern und Zeilen
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
            
            if isinstance(data, list):
                if data and isinstance(data[0], dict):
                    # Liste von Dictionaries
                    headers = list(data[0].keys())
                    rows = [[record.get(header) for header in headers] for record in data]
                    return headers, rows
                else:
                    # Liste von Listen
                    return None, data
            elif isinstance(data, dict):
                if "headers" in data and "rows" in data:
                    return data["headers"], data["rows"]
                else:
                    # Dictionary mit Index als Key
                    if data:
                        first_key = list(data.keys())[0]
                        headers = list(data[first_key].keys())
                        rows = [[data[key].get(header) for header in headers] for key in sorted(data.keys())]
                        return headers, rows
            
            return None, []
        except Exception as e:
            raise IOError(f"Fehler beim JSON-Import: {str(e)}")


