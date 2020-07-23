import json
import os
import re
import subprocess

from typing import Any, Dict, List
from xml.dom import minidom

from exit_codes import ExitCode, log_debug, log_err

CCCC_EXTENSIONS = ["c", "cc", "cpp", "c++", "h", "hpp", "hh"]


class Cccc:
    def __init__(self, path):
        self.cccc_path = os.path.join(path, "CCCC", "cccc")

    def run_n_parse_cccc(self, files_list: list, output_dir: os.path):
        self.run_tool_cccc(files_list, output_dir)
        return cccc_output_reader(os.path.join(output_dir, "outputs"))

    def run_tool_cccc(self, files_list: list, output_dir: str):
        try:
            output_subdir = self._output_subdir(output_dir)
            args = [self.cccc_path, "--outdir=" + output_subdir]
            args.extend(files_list)
            return subprocess.run(args, capture_output=True, check=True)

        except subprocess.CalledProcessError as ex:
            log_err(
                "\tCCCC exited with an error.\n{}\n{}\n",
                ExitCode.CCCC_TOOL_ERR,
                ex.stdout,
                ex.stderr,
            )

    def _output_subdir(self, output_dir):
        output_subdir = os.path.join(output_dir, "outputs")
        if not os.path.exists(output_subdir):
            os.mkdir(output_subdir)
        return output_subdir


def cccc_output_reader(cccc_xml_directory_path: str):
    base_dir = os.path.realpath(cccc_xml_directory_path)
    per_function_res = []

    with open(
        os.path.join(cccc_xml_directory_path, "cccc.xml"), "r"
    ) as cccc_file:
        cccc_xml = minidom.parse(cccc_file)

    project = cccc_xml.getElementsByTagName("CCCC_Project")
    modules = (
        project[0]
        .getElementsByTagName("oo_design")[0]
        .getElementsByTagName("module")
    )
    for module in modules:
        module_name = module.getElementsByTagName("name")[
            0
        ].firstChild.nodeValue

        WMC = module.getElementsByTagName("weighted_methods_per_class_unity")[
            0
        ].getAttribute("value")
        DIT = module.getElementsByTagName("depth_of_inheritance_tree")[
            0
        ].getAttribute("value")
        NOC = module.getElementsByTagName("number_of_children")[
            0
        ].getAttribute("value")
        CBO = module.getElementsByTagName("coupling_between_objects")[
            0
        ].getAttribute("value")

        log_debug(
            "\tCCCC output reader. Reading path: {}",
            os.path.join(base_dir, module_name + ".xml"),
        )

        with open(
            os.path.join(base_dir, module_name + ".xml"), "r"
        ) as moduleFile:
            module_xml = minidom.parse(moduleFile)

        CC_module = (
            module_xml.getElementsByTagName("module_summary")[0]
            .getElementsByTagName("McCabes_cyclomatic_complexity")[0]
            .getAttribute("value")
        )
        member_functions = module_xml.getElementsByTagName(
            "procedural_detail"
        )[0].getElementsByTagName("member_function")

        list_of_member_functions: List[Dict[str, Any]] = []
        for member_function in member_functions:
            member_function_name = member_function.getElementsByTagName(
                "name"
            )[0].firstChild.nodeValue

            file_in = None
            line_number = None
            definition_only = True
            for extent in member_function.getElementsByTagName("extent"):
                if (
                    extent.getElementsByTagName("description")[
                        0
                    ].firstChild.nodeValue
                    == "definition"
                ):
                    definition_only = False
                    file_in = extent.getElementsByTagName("source_reference")[
                        0
                    ].getAttribute("file")
                    line_number = extent.getElementsByTagName(
                        "source_reference"
                    )[0].getAttribute("line")
            if definition_only:
                # If it is not the implementation of the function, we skip it
                continue

            member_function_cc = member_function.getElementsByTagName(
                "McCabes_cyclomatic_complexity"
            )[0].getAttribute("value")
            lines_of_code = member_function.getElementsByTagName(
                "lines_of_code"
            )[0].getAttribute("value")
            lines_of_comment = member_function.getElementsByTagName(
                "lines_of_comment"
            )[0].getAttribute("value")

            per_function_values = {
                "file": file_in,
                "line_number": line_number,
                "func_name": member_function_name,
                "functionCC": member_function_cc,
                "loc": lines_of_code,
                "cloc": lines_of_comment,
            }
            list_of_member_functions.append(per_function_values)

        per_module_metrics = {
            "CC": CC_module,
            "WMC": WMC,
            "DIT": DIT,
            "NOC": NOC,
            "CBO": CBO,
        }
        # {"filename": file_in, "func_name": func_name,
        # "line_number": line_number, "values": per_function_values}
        per_function_res.append(
            {
                "module_name": module_name,
                "per_module_metrics": per_module_metrics,
                "functions": list_of_member_functions,
            }
        )
    return per_function_res


def standardizer_cccc(data):
    # Support structures
    tmp_dict_files = {}
    tmp_dict_modules = {}

    # for d in data:
    #   for module in d:
    for module in data:
        # If there are no functions, the module represents a class which is not
        # defined in the files we analyzed.
        # Hence, all its stats are 0, and the other tools will not have those
        # entries, so we can omit it.

        # We could still put these in the 'global' section
        if len(module["functions"]) == 0:
            continue

        if module["module_name"] not in tmp_dict_modules:
            tmp_dict_modules[
                module["module_name"]
            ] = {  # It's going to be added in the 'global' section
                "class name": module["module_name"],
                "CC": module["per_module_metrics"]["CC"],
                "C&K": {
                    "WMC": module["per_module_metrics"]["WMC"],
                    "DIT": module["per_module_metrics"]["DIT"],
                    "NOC": module["per_module_metrics"]["NOC"],
                    "CBO": module["per_module_metrics"]["CBO"],
                },
            }

        for func in module["functions"]:
            if (
                func["file"] not in tmp_dict_files
            ):  # Create new per_file struct
                per_file = {"filename": func["file"], "functions": []}
                tmp_dict_files[func["file"]] = per_file
            else:
                per_file = tmp_dict_files[func["file"]]

            per_func = None
            for i in per_file["functions"]:
                if i["line number"] == func["line_number"]:
                    per_func = i
                    break

            if per_func is None:  # New function
                per_func = {
                    "function name": re.sub(
                        r"\([^)]*\)", "", func["func_name"]
                    ),
                    "line number": func["line_number"],
                    "LOC": int(func["loc"]),  # LOC
                    "CLOC": int(func["cloc"]),
                    "CC": float(func["functionCC"]),
                    "class name": module[
                        "module_name"
                    ],  # The function is part of this module
                }
                per_file["functions"].append(per_func)

            else:
                log_debug(
                    "\t_standardizer_cccc() warning: same function found twice."
                    "\n\tanalyzed function:"
                    "\n\t{}\n"
                    "\talready present function:\n\t{}",
                    func,
                    per_func,
                )

    formatted_output = {"classes": [], "files": []}

    for module in tmp_dict_modules:
        if (
            module != "anonymous"
        ):  # Do not add the per_module stats if in "anonymous"
            formatted_output["classes"].append(tmp_dict_modules[module])

    for file in tmp_dict_files.values():
        formatted_output["files"].append(file)

    return formatted_output


def helper_cccc(standardized_output: dict):
    """Calculate McCabe's Weighted Method Count metric.
    This version uses the McCabe's CC for calculating the weight of
    each method."""

    for module in standardized_output["classes"]:
        WMC = 0
        n_func = 0
        module_name = module["class name"]
        for file in standardized_output["files"]:
            for func in file["functions"]:
                if "class name" in func and func["class name"] == module_name:
                    WMC += func["CC"]
                    n_func += 1
        module["WMC"] = WMC
        module["no. functions"] = n_func


def helper_test_cccc(standardized_output: dict, output: dict):
    """Calculate McCabe's Weighted Method Count metric.
    This version uses the McCabe's CC for calculating the weight of
    each method."""

    tot_loc = 0
    tot_cloc = 0

    for file in standardized_output["files"]:
        for function in file["functions"]:
            tot_loc += function["LOC"]
            tot_cloc += function["CLOC"]

    output["LOC"] = tot_loc
    output["CLOC"] = tot_cloc
    output["classes"] = standardized_output["classes"]
    output["files"] = standardized_output["files"]

    for module in output["classes"]:
        WMC = 0
        n_func = 0
        module_name = module["class name"]
        for file in output["files"]:
            for func in file["functions"]:
                if "class name" in func and func["class name"] == module_name:
                    WMC += func["CC"]
                    n_func += 1
        module["WMC"] = WMC
        module["no. functions"] = n_func
