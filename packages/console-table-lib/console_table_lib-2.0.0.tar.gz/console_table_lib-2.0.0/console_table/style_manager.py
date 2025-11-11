"""
StyleManager - Verwaltet die visuellen Eigenschaften und das Styling von Tabellen.
"""

try:
    from rich.console import Console
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class StyleManager:
    """Verwaltet Styling-Optionen für Tabellen."""
    
    # Border-Stile Definitionen
    BORDER_STYLES = {
        "single": {
            "horizontal": "─",
            "vertical": "│",
            "top_left": "┌",
            "top_right": "┐",
            "bottom_left": "└",
            "bottom_right": "┘",
            "top_tee": "┬",
            "bottom_tee": "┴",
            "left_tee": "├",
            "right_tee": "┤",
            "cross": "┼"
        },
        "double": {
            "horizontal": "═",
            "vertical": "║",
            "top_left": "╔",
            "top_right": "╗",
            "bottom_left": "╚",
            "bottom_right": "╝",
            "top_tee": "╦",
            "bottom_tee": "╩",
            "left_tee": "╠",
            "right_tee": "╣",
            "cross": "╬"
        },
        "rounded": {
            "horizontal": "─",
            "vertical": "│",
            "top_left": "╭",
            "top_right": "╮",
            "bottom_left": "╰",
            "bottom_right": "╯",
            "top_tee": "┬",
            "bottom_tee": "┴",
            "left_tee": "├",
            "right_tee": "┤",
            "cross": "┼"
        },
        "minimal": {
            "horizontal": " ",
            "vertical": "│",
            "top_left": " ",
            "top_right": " ",
            "bottom_left": " ",
            "bottom_right": " ",
            "top_tee": " ",
            "bottom_tee": " ",
            "left_tee": "│",
            "right_tee": "│",
            "cross": " "
        },
        "none": {
            "horizontal": " ",
            "vertical": " ",
            "top_left": " ",
            "top_right": " ",
            "bottom_left": " ",
            "bottom_right": " ",
            "top_tee": " ",
            "bottom_tee": " ",
            "left_tee": " ",
            "right_tee": " ",
            "cross": " "
        }
    }
    
    def __init__(self):
        self._border_style = "single"
        self._alignment = "left"
        self._padding = 1
        self._use_colors = RICH_AVAILABLE
        self._header_color = "bold cyan"
        self._footer_color = "bold yellow"
        self._row_colors = None  # Liste von Farben für Zeilen
        self._cell_colors = {}  # Dict: (row, col) -> Farbe
        self._theme = "default"
        self._console = Console() if RICH_AVAILABLE else None
    
    def set_border_style(self, style):
        """
        Setzt den Border-Stil.
        
        Args:
            style: Einer der verfügbaren Stile ("single", "double", "rounded", "minimal", "none")
        """
        if style not in self.BORDER_STYLES:
            raise ValueError(f"Ungültiger Border-Stil: {style}. Verfügbar: {list(self.BORDER_STYLES.keys())}")
        self._border_style = style
    
    def set_alignment(self, alignment):
        """
        Setzt die Textausrichtung.
        
        Args:
            alignment: "left", "center", oder "right"
        """
        if alignment not in ["left", "center", "right"]:
            raise ValueError(f"Ungültige Ausrichtung: {alignment}. Verfügbar: left, center, right")
        self._alignment = alignment
    
    def set_padding(self, padding):
        """
        Setzt den Padding-Wert.
        
        Args:
            padding: Anzahl der Leerzeichen auf jeder Seite
        """
        self._padding = max(0, int(padding))
    
    def get_border_chars(self):
        """Gibt die Border-Zeichen für den aktuellen Stil zurück."""
        return self.BORDER_STYLES[self._border_style]
    
    def get_alignment(self):
        """Gibt die aktuelle Textausrichtung zurück."""
        return self._alignment
    
    def get_padding(self):
        """Gibt den aktuellen Padding-Wert zurück."""
        return self._padding
    
    def align_text(self, text, width):
        """
        Richtet Text entsprechend der eingestellten Ausrichtung aus.
        
        Args:
            text: Der zu formatierende Text
            width: Die Zielbreite
        
        Returns:
            Formatierter Text
        """
        text = str(text)
        padding = self._padding
        available_width = width - (2 * padding)
        
        if len(text) > available_width:
            text = text[:available_width-3] + "..."
        
        if self._alignment == "left":
            return text.ljust(available_width)
        elif self._alignment == "right":
            return text.rjust(available_width)
        elif self._alignment == "center":
            return text.center(available_width)
        else:
            return text.ljust(available_width)
    
    def set_colors(self, enabled=True):
        """
        Aktiviert/deaktiviert Farben.
        
        Args:
            enabled: True um Farben zu aktivieren
        """
        self._use_colors = enabled and RICH_AVAILABLE
    
    def set_header_color(self, color):
        """
        Setzt die Farbe für Header.
        
        Args:
            color: Rich-Farbstring (z.B. "bold cyan", "red", "green")
        """
        self._header_color = color
    
    def set_footer_color(self, color):
        """
        Setzt die Farbe für Footer.
        
        Args:
            color: Rich-Farbstring
        """
        self._footer_color = color
    
    def set_row_color(self, row_index, color):
        """
        Setzt die Farbe für eine bestimmte Zeile.
        
        Args:
            row_index: Index der Zeile
            color: Rich-Farbstring
        """
        if self._row_colors is None:
            self._row_colors = {}
        self._row_colors[row_index] = color
    
    def set_cell_color(self, row_index, col_index, color):
        """
        Setzt die Farbe für eine bestimmte Zelle.
        
        Args:
            row_index: Index der Zeile
            col_index: Index der Spalte
            color: Rich-Farbstring
        """
        self._cell_colors[(row_index, col_index)] = color
    
    def set_theme(self, theme_name):
        """
        Setzt ein vordefiniertes Theme.
        
        Args:
            theme_name: "default", "dark", "light", "colorful"
        """
        self._theme = theme_name
        themes = {
            "default": {"header": "bold cyan", "footer": "bold yellow"},
            "dark": {"header": "bold white", "footer": "bold white"},
            "light": {"header": "bold blue", "footer": "bold magenta"},
            "colorful": {"header": "bold bright_cyan", "footer": "bold bright_yellow"}
        }
        if theme_name in themes:
            self._header_color = themes[theme_name]["header"]
            self._footer_color = themes[theme_name]["footer"]
    
    def format_text(self, text, color=None, is_header=False, is_footer=False, row_index=None, col_index=None):
        """
        Formatiert Text mit Farben (falls aktiviert).
        
        Args:
            text: Der zu formatierende Text
            color: Optionale Farbe
            is_header: Ob es ein Header ist
            is_footer: Ob es ein Footer ist
            row_index: Zeilenindex (für Zellfarben)
            col_index: Spaltenindex (für Zellfarben)
        
        Returns:
            Formatierter Text (String oder Rich Text)
        """
        if not self._use_colors:
            return str(text)
        
        if color:
            return f"[{color}]{text}[/{color}]"
        elif is_header:
            return f"[{self._header_color}]{text}[/{self._header_color}]"
        elif is_footer:
            return f"[{self._footer_color}]{text}[/{self._footer_color}]"
        elif row_index is not None and col_index is not None:
            cell_color = self._cell_colors.get((row_index, col_index))
            if cell_color:
                return f"[{cell_color}]{text}[/{cell_color}]"
        elif row_index is not None and self._row_colors:
            row_color = self._row_colors.get(row_index)
            if row_color:
                return f"[{row_color}]{text}[/{row_color}]"
        
        return str(text)
    
    def get_row_color(self, row_index):
        """Gibt die Farbe für eine Zeile zurück."""
        if self._row_colors:
            return self._row_colors.get(row_index)
        return None

