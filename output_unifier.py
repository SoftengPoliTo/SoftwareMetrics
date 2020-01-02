#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os.path
from typing import Dict, List, Any
from xml.dom import minidom
import metrics

__DEBUG_F__ = True

version = 1.2


def _mi_tool_output_reader(xml: minidom):
    per_function_list = []
    per_function_res = []

    measures = xml.getElementsByTagName('measure')

    for measure in measures:
        if measure.getAttribute('type') == "Function":
            labels = measure.getElementsByTagName("label")
            for label in labels:
                per_function_list.append(label.firstChild.nodeValue)

            items = measure.getElementsByTagName("item")
            for item in items:
                values = item.getElementsByTagName("value")
                i = 0
                per_function_values = {}
                for value in values:
                    if per_function_list[i] == "Maintainability":
                        # To have the standard MI formula
                        per_function_values[per_function_list[i]] = str(
                            int(int(value.firstChild.nodeValue) * 171 / 100))
                    else:
                        per_function_values[per_function_list[i]] = value.firstChild.nodeValue
                    i += 1

                name = item.getAttribute("name")
                func_name = name[0: name.find("(...) at ")] + "(...)"
                line_number = name[name.rfind(':') + 1:]
                file_in = name[name.find("(...) at ") + 9: name.rfind(':')]

                per_function_res.append(
                    {"filename": file_in, "func_name": func_name,
                     "line_number": line_number, "values": per_function_values})

    return per_function_res


def mi_tool_output_reader(xml: str):
    return _mi_tool_output_reader(minidom.parseString(xml))


def mi_tool_output_reader_from_file(xml_file_path: os.path):
    return _mi_tool_output_reader(minidom.parse(xml_file_path))


def _tokei_output_reader(tokei: json):
    inner = tokei.get("inner")
    return inner


def tokei_output_reader(json_output: str):
    return _tokei_output_reader(json.loads(json_output))


def tokei_output_reader_from_file(json_output_file_path: os.path):
    with open(json_output_file_path, 'r') as tokei_json:
        tokei_out = json.load(tokei_json)
    return _tokei_output_reader(tokei_out)


def cccc_output_reader(cccc_xml_directory_path: str):
    base_dir = os.path.realpath(cccc_xml_directory_path)
    # print("DEBUG: BASEDIR: " + base_dir)
    per_function_res = []

    with open(os.path.join(cccc_xml_directory_path, "cccc.xml"), 'r') as cccc_file:
        cccc_xml = minidom.parse(cccc_file)

    project = cccc_xml.getElementsByTagName("CCCC_Project")
    modules = project[0].getElementsByTagName("oo_design")[0].getElementsByTagName("module")
    for module in modules:
        module_name = module.getElementsByTagName("name")[0].firstChild.nodeValue

        WMC = module.getElementsByTagName("weighted_methods_per_class_unity")[0].getAttribute("value")
        DIT = module.getElementsByTagName("depth_of_inheritance_tree")[0].getAttribute("value")
        NOC = module.getElementsByTagName("number_of_children")[0].getAttribute("value")
        CBO = module.getElementsByTagName("coupling_between_objects")[0].getAttribute("value")

        # TODO: Mancanti:
        # RFC = module.getElementsByTagName("")[0].getAttribute("value")
        # LCOM= module.getElementsByTagName("")[0].getAttribute("value")
        ####
        # CC = module.getElementsByTagName("McCabes_cyclomatic_complexity")[0].firstChild.nodeValue
        # LOC = module.getElementsByTagName("lines_of_code")[0].firstChild.nodeValue
        # CLOC =module.getElementsByTagName("lines_of_comment")[0].firstChild.nodeValue
        if __DEBUG_F__:
            print("DEBUG:\tPATH: " + os.path.join(base_dir, module_name + ".xml"))  # TODO

        with open(os.path.join(base_dir, module_name + ".xml"), 'r') as moduleFile:
            module_xml = minidom.parse(moduleFile)

        CC_module = \
            module_xml.getElementsByTagName("module_summary")[0].getElementsByTagName("McCabes_cyclomatic_complexity")[
                0].getAttribute("value")
        member_functions = module_xml.getElementsByTagName("procedural_detail")[0].getElementsByTagName(
            'member_function')

        list_of_member_functions: List[Dict[str, Any]] = []
        file_in = ""
        for member_function in member_functions:
            member_function_name = member_function.getElementsByTagName("name")[0].firstChild.nodeValue
            file_in = member_function.getElementsByTagName("source_reference")[0].getAttribute("file")
            line_number = member_function.getElementsByTagName("source_reference")[0].getAttribute("line")
            member_function_cc = member_function.getElementsByTagName("McCabes_cyclomatic_complexity")[0].getAttribute(
                "value")

            per_function_values = {"func_name": member_function_name, "line_number": line_number,
                                   "functionCC": member_function_cc}
            list_of_member_functions.append(per_function_values)

        per_module_metrics = {"CC": CC_module, "WMC": WMC, "DIT": DIT, "NOC": NOC, "CBO": CBO}
        # {"filename": file_in, "func_name": func_name,
        # "line_number": line_number, "values": per_function_values}
        per_function_res.append({"filename": file_in, "module_name": module_name,
                                 "per_module_metrics": per_module_metrics, "functions": list_of_member_functions})

    return per_function_res


def halstead_metric_tool_reader(json_output):
    return json.loads(json_output)


def unifier_merger(data: dict, tool_output: dict):
    # # # formatted_output = { "files": [...] }

    # BEGIN Merging global metrics...
    for stat in tool_output:
        if stat == "files":
            continue

        if stat not in data:    # TODO: The default behaviour is to write ONLY the new values.
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

                if stat not in file:    # TODO: The default behaviour is to copy ONLY the new values.
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
                    if __DEBUG_F__:
                        print("DEBUG:\tline number and function name not found!")
                        print("\tCaused by file:", file_tool)
                    continue
                    # TODO: what should we do in this case?

                funct_found = False
                i = 0
                for f in file["functions"]:
                    if int(f["line number"]) == func_line_number_tool:
                        funct_found = True
                        break
                    i += 1

                if not funct_found:     # Not found => Add it!
                    file["functions"].append(per_func_tool)
                    file["functions"][-1]["line number"] = int(per_func_tool["line number"])

                else:   # Found => Merging...
                    for stat in per_func_tool:
                        if stat == "line number":
                            continue
                        if stat == "function name":    # Copy function name if possible
                            if "function name" not in file["functions"][i]:
                                file["functions"][i]["function name"] = per_func_tool["function name"]
                        else:   # Copy the stats.
                            if stat not in file["functions"][i]:     # Copy only the new ones
                                file["functions"][i][stat] = per_func_tool[stat]
                        # TODO: Cover the case where line number is not present.
            #  END  Merging per-function metrics...

            # The inner cycle can be interrupted to save time
            break

    return


def _standardizer_tokei(data):
    formatted_output = {
        "files": []
    }

    for d in data:
        # TODO: spostare questo controllo a monte? ↓
        if d not in ["C", "Cpp", "CHeader", "CppHeader"]:   # FILTER: Only prints these types.
            if __DEBUG_F__:
                print("DEBUG:\t(unifier_tokei) Skipping type " + d)
            continue

        for s in data[d]["stats"]:
            if __DEBUG_F__:
                print(s)

            per_file = {
                "filename": s["name"],
                "LOC": s["code"],
                "CLOC": s["comments"],
                "Lines": s["lines"],
                "functions": [],    # Tokei do not gives per-function information.
            }

            if d in ["CHeader", "CppHeader"]:  # Tokei distinguish CHeaders from CppHeaders from the extension only!
                per_file["type"] = "C/CppHeader"
            else:
                per_file["type"] = d

            formatted_output["files"].append(per_file)
    return formatted_output


def _standardizer_cccc(data):     # TODO: Consider merging this into cccc_output_reader
    formatted_output = {
        "files": []
    }

    print("CCCC raw:\n")     # TODO: RIMUOVILO
    print(data)
    print("\n")

    # for d in data:
    #   for module in d:
    for module in data:
        per_file = {
            "filename": module["filename"],
            "module_name": module["module_name"],   # TODO: Delete this! DEBUG only.
            "CC": module["per_module_metrics"]["CC"],
            "C&K": {
                "WMC": module["per_module_metrics"]["WMC"],
                "DIT": module["per_module_metrics"]["DIT"],
                "NOC": module["per_module_metrics"]["NOC"],
                "CBO": module["per_module_metrics"]["CBO"],
            }
        }
        per_function = []
        for f in module["functions"]:
            per_function.append({
                "line number": f["line_number"],
                "CC": f["functionCC"]
            })
        per_file["functions"] = per_function

        formatted_output["files"].append(per_file)

    # TODO: Can we calculate the global C&K?
    return formatted_output


def _standardizer_mi(data):   # TODO: Consider merging this into mi_output_reader
    formatted_output = {
        "files": []
    }

    list_of_filenames = []
    for d in data:
        new_func = {
            "function name": d["func_name"],
            "line number": d["line_number"],

            "NCSS": d["values"]["NCSS"],        # TODO: Che sono? Non è chiaro
            "CCN": d["values"]["CCN"],          # TODO: Che sono? Non è chiaro
            "MI": d["values"]["Maintainability"]
        }

        if d["filename"] not in list_of_filenames:
            list_of_filenames.append(d["filename"])
            formatted_output["files"].append({
                "filename": d["filename"],
                "functions": [new_func]
            })
        else:
            for i in formatted_output["files"]:
                if i["filename"] == d["filename"]:
                    i["functions"].append(new_func)
    return formatted_output


# TODO: Halstead Operators and Operands should be changed to "int"
def _standardizer_halstead(data):    # TODO: Consider merging this into halstead_output_reader
    formatted_output = {
        "files": []
    }

    # To calculate the global stats:
    all_operands = {}
    all_operators = {}

    for d in data:
        h = d["Halstead"]
        per_file = {
            "_Operators": h["_Operators"],
            "_Operands": h["_Operands"],
            "n1": h["n1"],
            "n2": h["n2"],
            "N1": h["N1"],
            "N2": h["N2"],
            "Vocabulary": h["Vocabulary"],
            "Length": h["Length"],
            "Volume": h["Volume"],
            "Difficulty": h["Difficlty"],   # TODO: fix the typo
            "Effort": h["Effort"],
            "Programming time": h["Programming time"],
            "Estimated program length": h["Estimated program length"],
            "Purity ratio": h["Purity ratio"],
        }
        formatted_output["files"].append({
            "filename": d["filename"],
            "Halstead": per_file,
            "functions": []     # No per_function data from this tool
        })

        for i in h["_Operators"]:
            if i not in all_operators:
                all_operators[i] = int(h["_Operators"][i])
            else:
                all_operators[i] += int(h["_Operators"][i])

        for i in h["_Operands"]:
            if i not in all_operands:
                all_operands[i] = int(h["_Operands"][i])
            else:
                all_operands[i] += int(h["_Operands"][i])
    formatted_output["Halstead"] = metrics.helper_halstead(all_operators, all_operands)

    return formatted_output


def _find_by_filename(tool_output, name):
    i = 0
    for f in tool_output["files"]:
        if f["filename"] == name:
            return i
        i += 1
    return None


def unifier(outputs, files_to_analyze):
    # Preparing global output structure.
    global_merged_output = {
        "files": []
    }

    for f in files_to_analyze:
        global_merged_output["files"].append({
            "filename": f,
            "functions": []
        })

    # The outputs must be standardized to be merged together.
    mi = _standardizer_mi(outputs["mi"])
    tokei = _standardizer_tokei(outputs["tokei"])
    cccc = _standardizer_cccc(outputs["cccc"])
    halstead = _standardizer_halstead(outputs["halstead"])

    # The data are merged with the complete output
    unifier_merger(global_merged_output, mi)
    unifier_merger(global_merged_output, cccc)
    unifier_merger(global_merged_output, tokei)
    unifier_merger(global_merged_output, halstead)

    return global_merged_output
