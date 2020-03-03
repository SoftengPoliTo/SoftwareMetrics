import enum
import logging
import sys
import typing as T


class ExitCode(enum.IntEnum):
    """Exit status codes."""

    # Internal error
    PROGRAMMING_ERROR = 1

    # 2 is used by argparse

    # Input errors
    TOOLS_DIR_NOT_FOUND = 3
    TOOLS_NOT_FOUND = 4
    TARGET_DIR_NOT_FOUND = 5
    COMPILE_COMMAND_FILE_ERROR = 6

    NO_SUPPORTED_FILES_FOUND = 7

    # Errors raised by tools
    TOKEI_TOOL_ERR = 8
    RUST_CODE_ANALYSIS_TOOL_ERR = 9
    CCCC_TOOL_ERR = 10
    MI_TOOL_ERR = 11
    HALSTEAD_TOOL_ERR = 12


def log_conf(verbose: bool) -> None:
    """Configure logging."""

    if verbose:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)


def log_debug(msg: str, *args: T.Any) -> None:
    """Log debug."""

    logging.debug(msg.format(*args))


def log_info(msg: str, *args: T.Any) -> None:
    """Log info."""

    logging.info(msg.format(*args))


def log_warn(msg: str, *args: T.Any) -> None:
    """Log warning."""

    logging.warning(msg.format(*args))


def log_err(msg: str, error: ExitCode, *args: T.Any) -> None:
    """Log error."""

    logging.error(msg.format(*args))
    sys.exit(error.value)
