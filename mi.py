import json
import os
import subprocess
from xml.dom import minidom

from exit_codes import ExitCode, log_err

MI_EXTENSIONS = ["c", "cc", "cpp", "c++"]


class Mi:
    def __init__(self, path):
        self.mi_path = os.path.join(path, "Maintainability_Index", "lizard")

    def run_n_parse_mi(self, files_list: list, output_dir: os.path):
        mi_tool_res = self.run_tool_mi(files_list)
        return mi_tool_output_reader(mi_tool_res.decode())

    def run_tool_mi(self, files_list: list):
        try:
            args = [self.mi_path, "-X"]
            args.extend(files_list)
            results = subprocess.run(args, capture_output=True, check=True)
            return results.stdout

        except subprocess.CalledProcessError as ex:
            log_err(
                "\tMaintainability Index Tool exited with an error.\n{}\n{}\n",
                ExitCode.MI_TOOL_ERR,
                ex.stdout,
                ex.stderr,
            )


def mi_tool_output_reader(xml_str: str):
    xml = minidom.parseString(xml_str)

    global_metrics = {}

    per_function_res = []
    per_file_res = []

    def _get_label_list(measure_tag):
        label_list = []

        labels = measure_tag.getElementsByTagName("label")
        for label in labels:
            label_list.append(label.firstChild.nodeValue)

        return label_list

    def _get_values_object(item_tag, label_list):
        metrics_output = {}

        # Get metrics values of a file
        values = item_tag.getElementsByTagName("value")
        for label, value in zip(label_list, values):
            if label == "Maintainability":
                # To have the standard MI formula
                metrics_output[label] = int(
                    float(value.firstChild.nodeValue) * 171 / 100
                )
            else:
                metrics_output[label] = value.firstChild.nodeValue

        return metrics_output

    measures = xml.getElementsByTagName("measure")

    for measure in measures:
        if measure.getAttribute("type") == "Function":
            # Get metrics name
            per_function_list = _get_label_list(measure)

            items = measure.getElementsByTagName("item")
            for item in items:
                # Get name, start row and filename of a function
                name = item.getAttribute("name")
                func_name = name[0 : name.find("(...) at ")]
                line_number = name[name.rfind(":") + 1 :]
                file_in = name[name.find("(...) at ") + 9 : name.rfind(":")]

                # Get metrics values of a function
                per_function_values = _get_values_object(
                    item, per_function_list
                )

                per_function_res.append(
                    {
                        "filename": file_in,
                        "func_name": func_name,
                        "line_number": line_number,
                        "values": per_function_values,
                    }
                )
        elif measure.getAttribute("type") == "File":

            # Get global metrics for each file
            per_file_list = _get_label_list(measure)

            items = measure.getElementsByTagName("item")
            for item in items:

                # Get metrics values of a file
                metrics_output = _get_values_object(item, per_file_list)

                output = {
                    "filename": item.getAttribute("name"),
                    **metrics_output,
                }

                per_file_res.append(output)

            # Get global metrics computed using all files
            sum_tags = measure.getElementsByTagName("sum")
            for tag in sum_tags:
                global_metrics[tag.getAttribute("lable")] = tag.getAttribute(
                    "value"
                )

    global_metrics["files"] = []
    for global_file in per_file_res:

        global_file["functions"] = []
        for func_name in per_function_res:
            if func_name["filename"] == global_file["filename"]:
                global_file["functions"].append(func_name)

        global_metrics["files"].append(global_file)

    return global_metrics


def standardizer_mi(data):

    formatted_output = {}

    formatted_output["LOC"] = int(data["NCSS"])
    formatted_output["CC"] = float(data["CCN"])
    formatted_output["classes"] = []
    formatted_output["files"] = []

    for file in data["files"]:
        files = {}
        files["filename"] = file["filename"]
        files["LOC"] = int(file["NCSS"])
        files["CC"] = float(file["CCN"])
        files["MI"] = float(file["Maintainability"])

        files["functions"] = []
        for func_name in file["functions"]:
            funcs = {}
            funcs["function name"] = func_name["func_name"]
            funcs["line number"] = func_name["line_number"]

            funcs["LOC"] = int(func_name["values"]["NCSS"])
            funcs["CC"] = float(func_name["values"]["CCN"])
            funcs["MI"] = float(func_name["values"]["Maintainability"])
            files["functions"].append(funcs)

        formatted_output["files"].append(files)

    return formatted_output


def helper_test_mi(standardized_output: dict, output: dict):

    output["LOC"] = standardized_output["LOC"]
    output["CC"] = standardized_output["CC"]
    output["classes"] = standardized_output["classes"]
    output["files"] = []

    for file in standardized_output["files"]:
        file_metrics = {
            "filename": file["filename"],
            "LOC": file["LOC"],
            "CC": file["CC"],
            "MI": file["MI"],
            "functions": file["functions"],
        }
        output["files"].append(file_metrics)
