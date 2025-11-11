"""
DataValidator - Stellt Datenintegrität sicher und verwaltet Validierungsregeln.
"""


class DataValidator:
    """Validiert Tabellendaten und stellt Integrität sicher."""
    
    def __init__(self):
        self._validation_rules = {}
        self._strict_mode = False
    
    def add_rule(self, column_index, rule_func, error_message=None):
        """
        Fügt eine Validierungsregel für eine Spalte hinzu.
        
        Args:
            column_index: Index der Spalte
            rule_func: Funktion, die True zurückgibt, wenn Wert gültig ist
            error_message: Optionale Fehlermeldung
        """
        if column_index not in self._validation_rules:
            self._validation_rules[column_index] = []
        
        self._validation_rules[column_index].append({
            'rule': rule_func,
            'message': error_message or "Validierungsfehler"
        })
    
    def validate_row(self, row):
        """
        Validiert eine einzelne Zeile.
        
        Args:
            row: Liste von Werten
        
        Returns:
            (is_valid, errors) - Tuple mit Validierungsstatus und Fehlerliste
        """
        errors = []
        
        for col_index, rules in self._validation_rules.items():
            if col_index >= len(row):
                continue
            
            value = row[col_index]
            
            for rule_info in rules:
                try:
                    if not rule_info['rule'](value):
                        errors.append({
                            'column': col_index,
                            'value': value,
                            'message': rule_info['message']
                        })
                except Exception as e:
                    errors.append({
                        'column': col_index,
                        'value': value,
                        'message': f"Validierungsfehler: {str(e)}"
                    })
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_all(self, rows):
        """
        Validiert alle Zeilen.
        
        Args:
            rows: Liste von Zeilen
        
        Returns:
            (is_valid, all_errors) - Tuple mit Validierungsstatus und allen Fehlern
        """
        all_errors = []
        
        for row_index, row in enumerate(rows):
            is_valid, errors = self.validate_row(row)
            if not is_valid:
                for error in errors:
                    error['row'] = row_index
                    all_errors.append(error)
        
        is_valid = len(all_errors) == 0
        return is_valid, all_errors
    
    def set_strict_mode(self, strict=True):
        """
        Aktiviert/deaktiviert den strikten Modus.
        
        Args:
            strict: Wenn True, werden Validierungsfehler als Exceptions geworfen
        """
        self._strict_mode = strict
    
    def ensure_consistent_columns(self, rows):
        """
        Stellt sicher, dass alle Zeilen die gleiche Anzahl von Spalten haben.
        
        Args:
            rows: Liste von Zeilen
        
        Returns:
            (is_consistent, max_columns) - Tuple mit Konsistenzstatus und max. Spaltenanzahl
        """
        if not rows:
            return True, 0
        
        lengths = [len(row) for row in rows]
        max_length = max(lengths)
        min_length = min(lengths)
        
        is_consistent = max_length == min_length
        return is_consistent, max_length


