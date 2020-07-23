import copy

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
from tokei import helper_test_tokei, helper_tokei, standardizer_tokei


def unifier_merger(data: dict, tool_output: dict):
    """
    This function automatically merges the already present data structures
    with the standardized output from the new tool
    """
    # # # formatted_output = { "files": [...] }

    # BEGIN Merging global metrics...
    for stat in tool_output:
        if stat == "files":
            continue

        if (
            stat not in data
        ):  # The default behaviour is to write ONLY the new values.
            data[stat] = tool_output[stat]
    #  END  Merging global metrics.

    # BEGIN Merging per-file metrics...
    for file_tool in tool_output["files"]:
        for file in data["files"]:
            if file["filename"] != file_tool["filename"]:
                continue

            for stat in file_tool:
                if stat in ["functions", "filename"]:
                    continue

                if (
                    stat not in file
                ):  # The default behaviour is to copy ONLY the new values.
                    file[stat] = file_tool[stat]
            # END Merging per-file metrics.

            # BEGIN Merging per-function metrics...
            for per_func_tool in file_tool["functions"]:
                # check if the function is already present

                # func_name_tool = None
                func_line_number_tool = None
                # if "function name" in per_func_tool:
                #     func_name_tool = per_func_tool["function name"]
                if "line number" in per_func_tool:
                    func_line_number_tool = int(per_func_tool["line number"])

                # if func_name_tool is None and func_line_number_tool is None:
                if func_line_number_tool is None:
                    log_warn(
                        "\tline number and function name not found!"
                        "\tCaused by file: {}",
                        file_tool,
                    )
                    continue

                funct_found = False
                i = 0
                for f in file["functions"]:
                    if int(f["line number"]) == func_line_number_tool:
                        funct_found = True
                        break
                    i += 1

                if not funct_found:  # Not found => Add it!
                    file["functions"].append(per_func_tool)
                    file["functions"][-1]["line number"] = int(
                        per_func_tool["line number"]
                    )

                else:  # Found => Merging...
                    for stat in per_func_tool:
                        if stat == "line number":
                            continue
                        if (
                            stat == "function name"
                        ):  # Copy function name if possible
                            if "function name" not in file["functions"][i]:
                                file["functions"][i][
                                    "function name"
                                ] = per_func_tool["function name"]
                        else:  # Copy the stats.
                            if (
                                stat not in file["functions"][i]
                            ):  # Copy only the new ones
                                file["functions"][i][stat] = per_func_tool[
                                    stat
                                ]
            # We are assuming that every tool also includes the line number of
            # the function.
            #  END  Merging per-function metrics...

            # The inner cycle can be interrupted to save time
            break

    return


def _test_mode(
    standardized_outputs, global_merged_output, tool_manager, outputs
):
    for tool, standardized_output in standardized_outputs.items():
        global_merged_output_copy = copy.deepcopy(global_merged_output)
        unifier_merger(global_merged_output_copy, standardized_output)
        outputs[tool] = global_merged_output_copy

    for tool in tool_manager.get_enabled_tools():
        if tool_manager.get_tool_output(tool):
            output = {}
            globals()["helper_test_" + tool.replace("-", "_")](
                outputs[tool], output
            )
            outputs[tool] = output


def _producer_mode(
    standardized_outputs, global_merged_output, tool_manager, outputs
):
    # The data are merged with the complete output
    standardized_outputs.pop("rust-code-analysis", None)
    for standardized_output in standardized_outputs.values():
        unifier_merger(global_merged_output, standardized_output)

    # Additional metrics, calculated using the available data, can be added here
    for tool in ["halstead", "tokei", "cccc"]:
        if tool_manager.get_tool_output(tool):
            globals()["helper_" + tool.replace("-", "_")](global_merged_output)

    outputs["all"] = global_merged_output


def unifier(tool_manager, files_to_analyze, one_json_per_tool):
    # Preparing global output structure.
    global_merged_output = {"files": []}

    for f in files_to_analyze:
        global_merged_output["files"].append({"filename": f, "functions": []})

    # The outputs must be standardized to be merged together.
    standardized_outputs = {}
    for tool in tool_manager.get_enabled_tools():
        standardized_output = globals()[
            "standardizer_" + tool.replace("-", "_")
        ](tool_manager.get_tool_output(tool))
        standardized_outputs[tool] = standardized_output

    outputs = {}
    if one_json_per_tool:
        _test_mode(
            standardized_outputs, global_merged_output, tool_manager, outputs
        )
    else:
        _producer_mode(
            standardized_outputs, global_merged_output, tool_manager, outputs
        )

    return outputs
