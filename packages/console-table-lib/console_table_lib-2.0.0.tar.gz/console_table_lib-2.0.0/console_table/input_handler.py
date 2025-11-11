"""
InputHandler - Verarbeitet Benutzereingaben für interaktive Tabellenelemente.
"""

import sys
import select
import termios
import tty


class InputHandler:
    """Verarbeitet Benutzereingaben für interaktive Funktionen."""
    
    def __init__(self):
        self._old_settings = None
    
    def _setup_terminal(self):
        """Konfiguriert das Terminal für nicht-blockierende Eingabe."""
        try:
            self._old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        except (termios.error, AttributeError):
            # Fallback für Systeme ohne termios (z.B. Windows)
            pass
    
    def _restore_terminal(self):
        """Stellt die Terminal-Einstellungen wieder her."""
        try:
            if self._old_settings:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)
        except (termios.error, AttributeError):
            pass
    
    def get_key(self, timeout=0.1):
        """
        Liest eine einzelne Taste (nicht-blockierend).
        
        Args:
            timeout: Timeout in Sekunden
        
        Returns:
            Gelesene Taste oder None
        """
        try:
            if select.select([sys.stdin], [], [], timeout)[0]:
                return sys.stdin.read(1)
        except (select.error, AttributeError):
            # Fallback für Windows
            pass
        return None
    
    def wait_for_key(self, valid_keys=None):
        """
        Wartet auf eine Taste (blockierend).
        
        Args:
            valid_keys: Liste von gültigen Tasten (optional)
        
        Returns:
            Gelesene Taste
        """
        self._setup_terminal()
        try:
            while True:
                key = sys.stdin.read(1)
                if not valid_keys or key in valid_keys:
                    return key
        finally:
            self._restore_terminal()
    
    def get_input(self, prompt=""):
        """
        Liest eine Zeile Eingabe (blockierend).
        
        Args:
            prompt: Eingabeaufforderung
        
        Returns:
            Eingegebene Zeile
        """
        self._restore_terminal()
        try:
            return input(prompt)
        finally:
            self._setup_terminal()
    
    def confirm(self, message="Fortfahren? (j/n): "):
        """
        Fragt nach Bestätigung.
        
        Args:
            message: Bestätigungsnachricht
        
        Returns:
            True wenn bestätigt, False sonst
        """
        self._restore_terminal()
        try:
            response = input(message).lower().strip()
            return response in ['j', 'ja', 'y', 'yes']
        finally:
            self._setup_terminal()


