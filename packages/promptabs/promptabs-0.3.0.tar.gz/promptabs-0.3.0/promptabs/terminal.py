"""
Terminal rendering and control module
"""

import sys
import os
from typing import Tuple, List, Optional, Set

from .theme import ColorTheme

class TerminalRenderer:
    """Handles terminal rendering and ANSI escape sequences"""

    # ANSI color codes (use theme constants)
    RESET = ColorTheme.RESET
    BOLD = ColorTheme.BOLD
    DIM = ColorTheme.DIM
    BLUE = ColorTheme.BLUE
    GREEN = ColorTheme.GREEN
    YELLOW = ColorTheme.YELLOW
    RED = ColorTheme.RED
    CYAN = ColorTheme.CYAN

    @staticmethod
    def clear_screen():
        """Clear the terminal screen using ANSI escape sequences

        Works on macOS, Linux, and Windows 10+ (ANSI mode enabled)
        No external OS commands are called.
        """
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    @staticmethod
    def move_cursor(row: int, col: int):
        """Move cursor to specific position"""
        sys.stdout.write(f"\033[{row};{col}H")
        sys.stdout.flush()

    @staticmethod
    def hide_cursor():
        """Hide the cursor"""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    @staticmethod
    def show_cursor():
        """Show the cursor"""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    @staticmethod
    def get_terminal_size() -> Tuple[int, int]:
        """Get terminal width and height (cross-platform)

        Works on Windows (Python 3.3+), macOS, and Linux.
        Returns (width, height) tuple.
        """
        try:
            size = os.get_terminal_size()
            return (size.columns, size.lines)
        except (AttributeError, ValueError, OSError):
            # Fallback for edge cases
            return (80, 24)

    @staticmethod
    def render_text(text: str, color: str = "", bold: bool = False) -> str:
        """Render text with optional color and bold"""
        prefix = ""
        if bold:
            prefix += TerminalRenderer.BOLD
        if color:
            prefix += color

        if prefix:
            return prefix + text + TerminalRenderer.RESET
        return text


class TabRenderer(TerminalRenderer):
    """Renders tab headers and content"""

    def __init__(self, renderer: TerminalRenderer):
        self.renderer = renderer

    def render_tab_header(
        self,
        tabs: List[str],
        active_index: int,
        max_width: int = 80,
    ) -> str:
        """
        Render tab header with active tab highlighted

        Args:
            tabs: List of tab titles
            active_index: Index of currently active tab
            max_width: Maximum width for tab header

        Returns:
            Rendered tab header string
        """
        tab_elements = []

        for i, tab in enumerate(tabs):
            if i == active_index:
                # Active tab with checkbox
                styled = self.render_text(
                    f"☑ {tab}",
                    color=self.BLUE,
                    bold=True,
                )
            else:
                # Inactive tab with unchecked checkbox
                styled = self.render_text(f"☐ {tab}", color=self.DIM)

            tab_elements.append(styled)

        # Join tabs with separators
        header = "  ".join(tab_elements)

        # Add navigation hint
        nav_hint = self.render_text(" → ", color=self.YELLOW)
        header += nav_hint

        return header

    def render_options(
        self,
        options: List[str],
        current_index: int,
        selected_indexes: Optional[Set[int]] = None,
        multiple: bool = False
    ) -> str:
        """
        Render question options with selection indicator

        Args:
            options: List of option strings
            current_index: Index of currently focused option
            selected_indexes: Set of selected option indexes (for multiple choice)
            multiple: Whether this is a multiple choice question

        Returns:
            Rendered options string
        """
        if selected_indexes is None:
            selected_indexes = set()

        lines = []
        for i, option in enumerate(options):
            if i == current_index:
                # Currently focused option
                indicator = self.render_text("❯ ", color=self.GREEN, bold=True)
                styled = self.render_text(option, color=self.GREEN, bold=True)

                # For multiple choice, add checkbox
                if multiple:
                    checkbox = "☑ " if i in selected_indexes else "☐ "
                    lines.append(f"{indicator}{checkbox}{styled}")
                else:
                    lines.append(f"{indicator}{styled}")
            else:
                # Unfocused option
                if multiple:
                    # Multiple choice - show checkbox
                    checkbox = "☑ " if i in selected_indexes else "☐ "
                    lines.append(f"  {checkbox}{option}")
                else:
                    # Single choice - no checkbox
                    lines.append(f"  {option}")

        return "\n".join(lines)

