from enum import Enum


class ExitCode(Enum):
    """Exit status codes."""

    PROGRAMMING_ERROR = 1  # It should never happen.
    # 2 is used by argparse
    TOOLS_DIR_NOT_FOUND = 3
    TOOLS_NOT_FOUND = 4
    TARGET_DIR_NOT_FOUND = 5
    COMPILE_COMMAND_FILE_ERROR = 6

    NO_SUPPORTED_FILES_FOUND = 7

    TOKEI_TOOL_ERR = 8
    RUST_CODE_ANALYSIS_TOOL_ERR = 9
    CCCC_TOOL_ERR = 10
    MI_TOOL_ERR = 11
    HALSTEAD_TOOL_ERR = 12
