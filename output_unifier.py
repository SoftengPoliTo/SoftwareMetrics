""" Unifies the metrics produced by a tool on different files in a single
json file, then uses the retrieved data to compute the global metrics """

from cccc import helper_test_cccc, standardizer_cccc
from exit_codes import log_warn
from halstead import (
    helper_test_halstead,
    standardizer_halstead,
)
from mi import helper_test_mi, standardizer_mi
from rust_code_analysis import (
    helper_test_rust_code_analysis,
    standardizer_rust_code_analysis,
)
from tokei import helper_test_tokei, standardizer_tokei


def unifier(tool_manager, files_to_analyze, one_json_per_tool):
    outputs = {}
    for tool in tool_manager.get_enabled_tools():
        # Standardize the output of each tool
        standardized_output, files_nspace = globals()[
            "standardizer_" + tool.replace("-", "_")
        ](tool_manager.get_tool_output(tool))
        # Compute the final global metrics starting from the standardized
        # output of a tool
        if tool_manager.get_tool_output(tool):
            outputs[tool] = globals()["helper_test_" + tool.replace("-", "_")](
                standardized_output, files_nspace
            )

    return outputs
