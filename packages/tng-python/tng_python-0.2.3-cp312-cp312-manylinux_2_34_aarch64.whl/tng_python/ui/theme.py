"""
TNG Python UI Theme System
Centralized styling, colors, icons, and layout constants
"""

from rich.box import DOUBLE


class TngTheme:
    """Centralized theme configuration for TNG Python UI"""

    # ==================== COLORS ====================
    class Colors:
        # Primary colors
        PRIMARY = "cyan"
        SECONDARY = "green"
        ACCENT = "yellow"

        # Status colors
        SUCCESS = "bold green"
        WARNING = "bold yellow"
        ERROR = "bold red"
        INFO = "bold cyan"

        # Text colors
        TEXT_PRIMARY = "white"
        TEXT_SECONDARY = "dim"
        TEXT_HIGHLIGHT = "bold white"
        TEXT_MUTED = "dim white"
        TEXT_BOLD = "bold"
        TEXT_BOLD_PRIMARY = "bold white"
        TEXT_BOLD_SUCCESS = "bold green"
        TEXT_BOLD_WARNING = "bold yellow"
        TEXT_BOLD_ERROR = "bold red"
        TEXT_BOLD_INFO = "bold cyan"

        # UI element colors
        BORDER_DEFAULT = "cyan"
        BORDER_SUCCESS = "green"
        BORDER_WARNING = "yellow"
        BORDER_ERROR = "red"

        # Interactive elements
        SELECTED = "bold green"
        HIGHLIGHTED = "bold green"
        POINTER = "bold yellow"
        CHECKBOX = "yellow"
        CHECKBOX_SELECTED = "bold green"

        # Progress bar colors
        PROGRESS_BAR = "cyan"
        PROGRESS_TEXT = "cyan"
        PROGRESS_COMPLETE = "green"

    # ==================== ICONS ====================
    class Icons:
        # Navigation
        BACK = "←"
        EXIT = "🚪"
        CONTINUE = "➡️"

        # Actions
        GENERATE = "🧪"
        ANALYZE = "🔍"
        CONFIG = "⚙️"
        REGENERATE = "🔄"
        VIEW = "👀"
        EDIT = "✏️"
        FIX = "🔧"

        # Status
        SUCCESS = "✅"
        WARNING = "⚠️"
        ERROR = "❌"
        INFO = "ℹ️"
        LOADING = "🔄"
        COMPLETE = "🎉"

        # Files and code
        FILE = "📄"
        FOLDER = "📁"
        CODE = "💻"
        TEST = "🧪"
        METHOD = "🔧"
        CLASS = "🏗️"
        FUNCTION = "⚡"
        TERMINAL = "💻"

        # Statistics
        STATS = "📊"
        CHART = "📈"
        METRICS = "📏"
        TIME = "⏱️"

        # Communication
        EMAIL = "📧"
        LINK = "🌐"
        SUPPORT = "💬"
        STAR = "🌟"
        BUG = "🐛"

        # Progress and phases
        ROCKET = "🚀"
        SEARCH = "🔍"
        BRAIN = "🧠"
        WRITE = "📝"
        FINALIZE = "✅"

        # Menu items
        ABOUT = "ℹ️"
        HELP = "❓"
        WELCOME = "🚀"
        GOODBYE = "👋"

        # Special
        LIGHTBULB = "💡"
        CHECKBOX_EMPTY = "☐"
        CHECKBOX_FILLED = "☑️"
        ARROW_UP = "↑"
        ARROW_DOWN = "↓"
        ARROW_RIGHT = "→"
        BULLET = "•"

        # Service messages
        CLOCK = "⏰"
        CHECK = "✅"
        CROSS = "❌"
        INFORMATION = "ℹ️"

    # ==================== LAYOUT ====================
    class Layout:
        # Panel dimensions
        PANEL_PADDING = (1, 2)
        PANEL_MIN_WIDTH = 60
        PANEL_MAX_WIDTH = 100
        PANEL_BOX_STYLE = DOUBLE

        # Progress bar
        PROGRESS_BAR_WIDTH = 50

        # Table dimensions
        TABLE_COLUMN_WIDTH_SMALL = 15
        TABLE_COLUMN_WIDTH_MEDIUM = 25
        TABLE_COLUMN_WIDTH_LARGE = 40
        TABLE_PADDING = (0, 2)

        # Spacing
        SECTION_SPACING = 1
        ITEM_SPACING = 0

        # Content limits
        MAX_CONTENT_LENGTH = 1200
        MAX_PREVIEW_LENGTH = 1000
        TRUNCATE_SUFFIX = "\n\n... (truncated)"

    # ==================== TEXT STYLES ====================
    class TextStyles:
        # Titles and headers
        TITLE = "bold cyan"
        SUBTITLE = "bold blue"
        HEADER = "bold white"
        SUBHEADER = "bold dim"

        # Content
        BODY = "white"
        BODY_BOLD = "bold white"
        DESCRIPTION = "dim"
        EMPHASIS = "bold"
        STRONG = "bold white"

        # Interactive
        QUESTION = "bold cyan"
        ANSWER = "bold green"
        INSTRUCTION = "dim"
        PROMPT = "bold yellow"

        # Status messages
        SUCCESS_MESSAGE = "bold green"
        WARNING_MESSAGE = "bold yellow"
        ERROR_MESSAGE = "bold red"
        INFO_MESSAGE = "bold cyan"

        # Special emphasis
        HIGHLIGHT_BOLD = "bold yellow"
        IMPORTANT = "bold red"
        NOTE = "bold blue"

    # ==================== MESSAGES ====================
    class Messages:
        # Common prompts
        PRESS_ANY_KEY = "Press any key to continue..."
        SELECT_OPTION = "Select an option:"
        BACK_TO_MENU = "Back to Main Menu"

        # File operations
        NO_FILES_FOUND = "No user Python files found in current directory.\nMake sure you're in a Python project directory."
        NO_METHODS_FOUND = "No public methods found in {filename}"
        FILE_SELECTED = "Selected file: {filename}"

        # Generation messages
        GENERATION_START = "Starting test generation..."
        GENERATION_COMPLETE = "Test generation completed successfully!"
        GENERATION_PHASES = [
            "Analyzing method signature",
            "Generating test logic",
            "Writing test code",
            "Finalizing test"
        ]

        # Configuration messages
        CONFIG_MISSING = "No configuration file found"
        CONFIG_CREATED = "Configuration file created successfully!"
        CONFIG_ERROR = "Error creating config: {error}"

        # Navigation
        TYPE_TO_FILTER = "type to filter"
        ARROW_TO_NAVIGATE = "arrows to navigate"
        SPACE_TO_SELECT = "space to select"
        ENTER_TO_CONFIRM = "enter to confirm"
        TAB_TO_SELECT = "tab to select"

    # ==================== PANEL TITLES ====================
    class Titles:
        # Main sections
        WELCOME = "🚀  Welcome"
        GENERATE_TESTS = "🧪  Generate Tests"
        PROJECT_STATS = "📊  Statistics"
        ABOUT = "ℹ️  About TNG Python"
        HELP = "❓  Help"
        CONFIGURATION = "⚙️  Configuration"
        GOODBYE = "👋  Goodbye!"

        # Sub-sections
        FILE_SELECTION = "File Selection"
        METHOD_SELECTION = "Method Selection"
        GENERATION_COMPLETE = "✅  Generation Complete"
        GENERATION_STATS = "📊  Generation Stats"
        READY_TO_GENERATE = "✅  Ready to Generate Tests"
        TEST_GENERATION = "Test Generation"
        GENERATION_FAILED = "❌  Generation Failed"

        # Status and warnings
        ATTENTION_REQUIRED = "⚠️  Attention Required"
        NO_FILES_FOUND = "❌  No Files Found"
        NO_METHODS_FOUND = "⚠️  No Methods Found"
        FILE_SELECTED = "File Selected"

        # Configuration
        CURRENT_STATUS = "Current Status"
        CONFIGURATION_MISSING = "Configuration Missing"
        SUCCESS = "Success"
        ERROR = "Error"

    # ==================== MENU OPTIONS ====================
    class MenuOptions:
        # Main menu
        MAIN_MENU = [
            "🧪 Generate Tests",
            "📊 Project Stats",
            "🌐 Show All Options",
            "ℹ️  About",
            "❓ Help",
            "⚙️  Configuration",
            "🔙 Exit"
        ]

        # Configuration menu
        CONFIG_ACTIONS = [
            "👀 View current configuration",
            "🔄 Regenerate configuration",
            "🔙 Back to Main Menu"
        ]

        WARNING_ACTIONS = [
            "🔧  Fix Configuration Issues",
            "🚪  Exit Application"
        ]

    # ==================== HELPER METHODS ====================
    @classmethod
    def format_file_display(cls, filename, parent_dir):
        """Format file display with icon"""
        return f"{cls.Icons.FILE}  {filename} ({parent_dir})"

    @classmethod
    def format_method_display(cls, method_name, class_name=None):
        """Format method display"""
        if class_name:
            return f"{class_name}.{method_name}"
        return method_name

    @classmethod
    def format_back_option(cls, destination="Main Menu"):
        """Format back option with icon"""
        return f"{cls.Icons.BACK}  Back to {destination}"

    @classmethod
    def format_status_message(cls, icon, message, style=None):
        """Format status message with icon"""
        return f"{icon}  {message}"

    @classmethod
    def get_progress_phases(cls):
        """Get progress phases with icons"""
        return [
            (f"{cls.Icons.SEARCH} {cls.Messages.GENERATION_PHASES[0]}", 0.3),
            (f"{cls.Icons.BRAIN} {cls.Messages.GENERATION_PHASES[1]}", 0.8),
            (f"{cls.Icons.WRITE} {cls.Messages.GENERATION_PHASES[2]}", 0.4),
            (f"{cls.Icons.FINALIZE} {cls.Messages.GENERATION_PHASES[3]}", 0.2)
        ]

    @classmethod
    def bold_text(cls, text, color=None):
        """Create bold text with optional color"""
        if color:
            return f"bold {color}"
        return "bold"

    @classmethod
    def format_bold_message(cls, message, style_type="primary"):
        """Format message with bold styling"""
        style_map = {
            "primary": cls.TextStyles.BODY_BOLD,
            "success": cls.TextStyles.SUCCESS_MESSAGE,
            "warning": cls.TextStyles.WARNING_MESSAGE,
            "error": cls.TextStyles.ERROR_MESSAGE,
            "info": cls.TextStyles.INFO_MESSAGE,
            "highlight": cls.TextStyles.HIGHLIGHT_BOLD,
            "important": cls.TextStyles.IMPORTANT,
            "note": cls.TextStyles.NOTE
        }
        return style_map.get(style_type, cls.TextStyles.BODY_BOLD)

    # ==================== TEXT ALIGNMENT ====================
    @classmethod
    def center_text(cls, text: str, terminal_width: int = 80) -> str:
        """Center text within terminal width"""
        # Remove rich markup for length calculation
        import re
        clean_text = re.sub(r'\[/?[^\]]*\]', '', text)
        padding = (terminal_width - len(clean_text)) // 2
        padding = max(0, padding)
        return " " * padding + text

    @classmethod
    def center_box(cls, box_content: str, box_width: int, terminal_width: int = 80) -> str:
        """Center box content within terminal width"""
        lines = box_content.split("\n")
        padding = (terminal_width - box_width) // 2
        padding = max(0, padding)
        return "\n".join(" " * padding + line for line in lines)

    @classmethod
    def calculate_box_width(cls, terminal_width: int = 80) -> int:
        """Calculate optimal box width for terminal"""
        return min(terminal_width - 4, cls.Layout.PANEL_MAX_WIDTH)

    @classmethod
    def get_terminal_width(cls) -> int:
        """Get current terminal width with fallback"""
        try:
            import shutil
            return shutil.get_terminal_size().columns
        except:
            return 80
