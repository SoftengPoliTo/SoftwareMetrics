from enum import Enum


class ExitCode(Enum):
    """Exit status codes."""
    USAGE_HELP = 1
    TOOLS_DIR_NOT_FOUND = 2
    TOOLS_NOT_FOUND = 3
    TARGET_DIR_NOT_FOUND = 4

    NO_SUPPORTED_FILES_FOUND = 5

    TOKEI_TOOL_ERR = 6
    CCCC_TOOL_ERR = 7
    MI_TOOL_ERR = 8
    HALSTEAD_TOOL_ERR = 9
