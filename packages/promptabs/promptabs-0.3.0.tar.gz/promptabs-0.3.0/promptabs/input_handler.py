"""
Keyboard input handling module (cross-platform compatible)
"""

import sys
from typing import Optional
import readchar

# Try to import termios for error handling (only available on Unix/POSIX)
try:
    import termios
    TermiosError = termios.error
except ImportError:
    # Windows doesn't have termios, use OSError as fallback
    TermiosError = OSError

# Check if running on Windows
IS_WINDOWS = sys.platform == 'win32'


class InputHandler:
    """Handles raw keyboard input from terminal (Windows/macOS/Linux compatible)"""

    # Special key codes
    ARROW_UP = "UP"
    ARROW_DOWN = "DOWN"
    ARROW_LEFT = "LEFT"
    ARROW_RIGHT = "RIGHT"
    ENTER = "ENTER"
    ESC = "ESC"
    CTRL_C = "CTRL_C"
    SPACE = " "
    BACKSPACE = "\x08"  # Backspace character (0x08)

    # readchar special key mappings
    _READCHAR_ESCAPE = "\x1b"  # Escape character
    _READCHAR_ENTER_CR = "\r"  # Carriage return (macOS/Linux)
    _READCHAR_ENTER_LF = "\n"  # Line feed (some platforms in raw mode)
    _READCHAR_CTRL_C = "\x03"  # Ctrl+C

    # Windows special key indicators
    _WINDOWS_SPECIAL_KEY_1 = "\x00"  # First null byte (older Windows)
    _WINDOWS_SPECIAL_KEY_2 = "\xe0"  # Extended key code (modern Windows)

    # Windows arrow key codes (second byte after special key indicator)
    _WINDOWS_ARROW_UP = "H"
    _WINDOWS_ARROW_DOWN = "P"
    _WINDOWS_ARROW_LEFT = "K"
    _WINDOWS_ARROW_RIGHT = "M"

    @staticmethod
    def read_single_key() -> Optional[str]:
        """
        Read a single key press from the terminal (cross-platform)

        Works on Windows (cmd.exe), macOS, and Linux. Returns special key names for
        arrow keys, Enter, Escape, and Ctrl+C.

        Returns:
            Key name (for special keys) or character (for regular keys),
            or None if unable to read
        """
        try:
            # readchar.readchar() handles all platform-specific details
            ch = readchar.readchar()

            if ch == InputHandler._READCHAR_CTRL_C:  # Ctrl+C
                return InputHandler.CTRL_C
            elif ch == InputHandler._READCHAR_ENTER_CR or ch == InputHandler._READCHAR_ENTER_LF:  # Enter
                return InputHandler.ENTER
            elif IS_WINDOWS and (ch == InputHandler._WINDOWS_SPECIAL_KEY_1 or ch == InputHandler._WINDOWS_SPECIAL_KEY_2):
                # Windows special key (arrow keys, etc.)
                try:
                    ch2 = readchar.readchar()
                    if ch2 == InputHandler._WINDOWS_ARROW_UP:
                        return InputHandler.ARROW_UP
                    elif ch2 == InputHandler._WINDOWS_ARROW_DOWN:
                        return InputHandler.ARROW_DOWN
                    elif ch2 == InputHandler._WINDOWS_ARROW_LEFT:
                        return InputHandler.ARROW_LEFT
                    elif ch2 == InputHandler._WINDOWS_ARROW_RIGHT:
                        return InputHandler.ARROW_RIGHT
                except (OSError, EOFError, TermiosError):
                    # If we can't read the second byte, ignore
                    return None
                return None
            elif ch == InputHandler._READCHAR_ESCAPE:  # Escape sequence start (Unix/macOS)
                try:
                    # Try to read the rest of the escape sequence
                    ch2 = readchar.readchar()
                    if ch2 == "[":
                        ch3 = readchar.readchar()
                        if ch3 == "A":
                            return InputHandler.ARROW_UP
                        elif ch3 == "B":
                            return InputHandler.ARROW_DOWN
                        elif ch3 == "C":
                            return InputHandler.ARROW_RIGHT
                        elif ch3 == "D":
                            return InputHandler.ARROW_LEFT
                except (OSError, EOFError, TermiosError):
                    # If we can't read the full sequence, just return ESC
                    return InputHandler.ESC
                return InputHandler.ESC
            elif ord(ch) == 127 or ch == "\x08":  # Backspace (DEL or Ctrl+H)
                return InputHandler.BACKSPACE
            else:
                return ch

        except (OSError, EOFError, TermiosError):
            # Fallback if input reading fails
            return None
