from cccc import helper_cccc, helper_test_cccc, standardizer_cccc
from exit_codes import log_warn
from halstead import (
    helper_halstead,
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
    # Standardize the output of each tool and
    # compute the final global metrics
    outputs = {}
    for tool in tool_manager.get_enabled_tools():
        standardized_output = globals()[
            "standardizer_" + tool.replace("-", "_")
        ](tool_manager.get_tool_output(tool))
        if tool_manager.get_tool_output(tool):
            outputs[tool] = globals()["helper_test_" + tool.replace("-", "_")](
                standardized_output
            )

    return outputs
