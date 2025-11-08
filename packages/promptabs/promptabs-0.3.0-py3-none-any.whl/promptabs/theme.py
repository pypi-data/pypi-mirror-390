"""
Color theme configuration for terminal rendering
"""


class ColorTheme:
    """
    ANSI color theme configuration.

    Centralizes all color codes for consistent theming and easier customization.
    """

    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Colors
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"

    # Semantic colors (for easier customization)
    PRIMARY = BLUE          # Active tab, highlighted option
    SUCCESS = GREEN         # Selected/confirmed option
    WARNING = YELLOW        # Warning messages
    INFO = CYAN            # Navigation hints
    TEXT = RESET           # Default text

    @classmethod
    def set_primary(cls, color: str):
        """Set primary color (used for active elements)"""
        cls.PRIMARY = color

    @classmethod
    def set_success(cls, color: str):
        """Set success color (used for selected elements)"""
        cls.SUCCESS = color

    @classmethod
    def set_warning(cls, color: str):
        """Set warning color (used for warnings)"""
        cls.WARNING = color

    @classmethod
    def set_info(cls, color: str):
        """Set info color (used for navigation hints)"""
        cls.INFO = color

    def __init__(self):
        """Initialize with default theme"""
        pass
