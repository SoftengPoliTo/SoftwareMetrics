#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os.path
from typing import Dict, List, Any
from xml.dom import minidom

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


def mi_tool_output_reader_from_file(xml_file_path: str):
    return _mi_tool_output_reader(minidom.parse(xml_file_path))


def _tokei_output_reader(tokei: json):
    # TODO: do we want to add something more?
    inner = tokei.get("inner")
    return inner


def tokei_output_reader(json_output: str):
    return _tokei_output_reader(json.loads(json_output))


def tokei_output_reader_from_file(json_output_file_path: str):
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
            print("DEBUG: PATH: " + os.path.join(base_dir, module_name + ".xml"))  # TODO

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


# def _flatten_list(data):    # It is used to remove the nested lists created by "analyze_path".
#    l=[]
#    for x in data:
#        if type(x) is list:


def unifier_tokei(data):    # TODO: Consider merging this into tokei_output_reader
    list_of_formatted_outputs = []
    for d in data:
        if d not in ["C", "Cpp", "CHeader", "CppHeader"]:   # FILTER: Only prints these types.
            if __DEBUG_F__:
                print("DEBUG: (unifier_tokei) Skipping type " + d)
            continue

        for s in data[d]["stats"]:
            if __DEBUG_F__:
                print(s)
            formatted_outputs = {
                "filename": s["name"],
                "values": {
                    "loc": s["code"],
                    "cloc": s["comments"],
                    "tot_lines": s["lines"]
                }
            }

            # formatted_outputs["blank_lines"] = s["blanks"]
            if d in ["CHeader", "CppHeader"]: # Tokei distinguish CHeaders from CppHeaders from the extension only!
                formatted_outputs["values"]["type_of_file"] = "C/CppHeader"
            else:
                formatted_outputs["values"]["type_of_file"] = d
            list_of_formatted_outputs.append(formatted_outputs)
    return list_of_formatted_outputs


def unifier_cccc(data):     # TODO: Consider merging this into cccc_output_reader
    list_of_formatted_outputs = []
    for d in data:
        for module in d:
            list_of_formatted_outputs.append({
                "filename": module["filename"],
                "values": {
                    "module_name": module["module_name"],
                    "per_module_metrics": module["per_module_metrics"],
                    "functions": module["functions"]
                }
            })

    return list_of_formatted_outputs


def unifier_mi(data):   # TODO: Consider merging this into mi_output_reader
    list_of_formatted_outputs = []
    list_of_filenames = []
    for d in data:
        new_func = {
            "func_name": d["func_name"],
            "line_number": d["line_number"],
            "values": d["values"]
        }
        if d["filename"] not in list_of_filenames:
            list_of_filenames.append(d["filename"])
            list_of_formatted_outputs.append({
                "filename": d["filename"],
                "functions": [new_func]
            })
        else:
            for i in list_of_formatted_outputs:
                if i["filename"] == d["filename"]:
                    i["functions"].append(new_func)
    return list_of_formatted_outputs


def unifier_halstead(data):    # TODO: Consider merging this into halstead_output_reader
    return data


def _find_filename(tool_output: list, name: str) -> int:
    i = 0
    for f in tool_output:
        if f["filename"] == name:
            return i
        i += 1
    return -1


def unifier(outputs):
    tokei = unifier_tokei(outputs["tokei"])
    cccc = unifier_cccc(outputs["cccc"])
    mi = unifier_mi(outputs["mi"])
    halstead = unifier_halstead(outputs["halstead"])
    complete_list = []

    if __DEBUG_F__:
        print("\n\tCLEANED:\n")
        print(tokei)
        print()
        print(cccc)
        print()
        print(mi)
        print()
        print(halstead)
        print()

    for file in tokei:
        filename = file["filename"]
        item = {
            "filename": filename,
            "TOKEI": file["values"]
        }

        i = _find_filename(cccc, filename)
        if i == -1:
            item["CCCC"] = "ERROR"  # TODO: Find a better way to signal something went wrong
        else:
            item["CCCC"] = cccc[i]["values"]   # TODO : completare!
            # del item["CCCC"]["filename"] NO!

        i = _find_filename(mi, filename)
        if i == -1:
            item["MI"] = "ERROR"    # TODO: Find a better way to signal something went wrong || Con .h nn deve stamparlo
        else:
            item["MI"] = mi[i]["functions"]   # TODO : completare!
            # del item["MI"]["filename"]

        i = _find_filename(halstead, filename)
        if i == -1:
            item["HALSTEAD"] = "ERROR"    # TODO: Find a better way to signal something went wrong
        else:
            item["HALSTEAD"] = halstead[i]["Halstead"]   # TODO : completare!
        complete_list.append(item)

    return complete_list
