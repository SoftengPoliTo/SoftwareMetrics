#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os.path
from typing import Dict, List, Any
from xml.dom import minidom

version = 1.2

def _mi_tool_output_reader(xml_doc: minidom):
    per_function_list = []
    per_function_res = []

    measures = xml_doc.getElementsByTagName('measure')

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
                file_in = name[name.find("(...) at ") + 9: name.rfind(':') - 1]

                per_function_res.append((file_in, func_name, line_number, per_function_values))

    return per_function_res


def mi_tool_output_reader(xml: str):
    return _mi_tool_output_reader(minidom.parseString(xml))


def mi_tool_output_reader_from_file(xml_file_path):
    return _mi_tool_output_reader(minidom.parse(xml_file_path))


def tokei_output_reader(json_output):
    inner = json.loads(json_output).get('inner')
    # TODO: da Finire
    return inner


def tokei_output_reader_from_file(json_output_file_path: str):
    with open(json_output_file_path, 'r') as tokei_json:
        tokei_out = json.load(tokei_json)
    inner = tokei_out.get('inner')

    # for language in inner.keys():
    #     inner[language]
    # TODO: da Finire
    return inner


def cccc_output_reader(cccc_xml_directory_path):
    base_dir = os.path.realpath(cccc_xml_directory_path)
    print("DEBUG: BASEDIR: " + base_dir)
    per_function_res = []

    with open( os.path.join(cccc_xml_directory_path,"cccc.xml"), 'r') as cccc_file:
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
        print("DEBUG: PATH: " + os.path.join(base_dir, module_name + ".xml")) # TODO

        with open(os.path.join(base_dir, module_name + ".xml"), 'r') as moduleFile:
            module_xml = minidom.parse(moduleFile)

        CC_module = \
            module_xml.getElementsByTagName("module_summary")[0].getElementsByTagName("McCabes_cyclomatic_complexity")[
                0].getAttribute("value")
        member_functions = module_xml.getElementsByTagName("procedural_detail")[0].getElementsByTagName('member_function')

        list_of_member_functions: List[Dict[str, Any]] = []
        file_in = ""
        for member_function in member_functions:
            member_function_name = member_function.getElementsByTagName("name")[0].firstChild.nodeValue
            file_in = member_function.getElementsByTagName("source_reference")[0].getAttribute("file")
            line_number = member_function.getElementsByTagName("source_reference")[0].getAttribute("line")
            member_function_cc = member_function.getElementsByTagName("McCabes_cyclomatic_complexity")[0].getAttribute(
                "value")

            per_function_values = {"functionName": member_function_name, "lineNumber": line_number,
                                   "functionCC": member_function_cc}
            list_of_member_functions.append(per_function_values)

        per_module_metrics = {"CC": CC_module, "WMC": WMC, "DIT": DIT, "NOC": NOC, "CBO": CBO}

        per_function_res.append((file_in, module_name, per_module_metrics, list_of_member_functions))

    return per_function_res

    # cccc.xml -> procedural_summary->module : prendi lista modules
    # carica ogni file *modulo*
    # Per Ogni modulo, prendere TUTTE le funzioni ==> Calcola WMC!x\
    # 
    #


def halstead_metric_tool_reader(json_output):
    return json.loads(json_output)
