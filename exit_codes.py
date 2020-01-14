from enum import Enum


class ExitCode(Enum):
    """Exit status codes."""
    USAGE_HELP = 1
    PROGRAMMING_ERROR = 2   # It should never happen.

    TOOLS_DIR_NOT_FOUND = 3
    TOOLS_NOT_FOUND = 4
    TARGET_DIR_NOT_FOUND = 5

    NO_SUPPORTED_FILES_FOUND = 6

    TOKEI_TOOL_ERR = 7
    CCCC_TOOL_ERR = 8
    MI_TOOL_ERR = 9
    HALSTEAD_TOOL_ERR = 10
