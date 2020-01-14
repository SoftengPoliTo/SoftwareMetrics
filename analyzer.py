#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import sys
from exit_codes import ExitCode
import tools
import json

__DEBUG_F__ = True


# TODO: AGGIUNGI CONTROLLO: SE GLI PASSO UN PROGETTO NON DEVE NEMMENO PARTIRE
#  (FAI LA PROVA: passagli un progetto Java in input)
#  Controlla i files: se non c'è nessun .h, .c, .cpp, ... ALLORA deve dire "controlla che il path sia giusto"

#  SE c'è un file .java, TOKEI può analizzarlo... MA meglio che venga DROPPATO!!
# Dare in base al linguaggio la lista dei tools che si possono usare

def analyze(path_to_analyze=None, files_list=None, results_dir=".", tools_path="./CC++_Tools"):
    if path_to_analyze is None and files_list is None:
        print("ERROR:\teither a path to analyze, or a list of files must be passed to function 'analyze'.")
        sys.exit(ExitCode.PROGRAMMING_ERROR.value)

    if not os.path.isdir(results_dir):
        print("ERROR:\tthe results path (" + results_dir + ") does not exists.", file=sys.stderr)
        sys.exit(ExitCode.TARGET_DIR_NOT_FOUND.value)

    t = tools.Tools(tools_path)
    t.check_tools_existence()

    # Checking for analyzable files.
    if path_to_analyze is not None and len(tools.list_of_files(path_to_analyze, tools.ACCEPTED_EXTENSIONS)) == 0:
        print("ERROR:\tthe given path does not contain any of the supported files.\n"
              "\tBe sure to pass the right folder to analyze.")
        sys.exit(ExitCode.NO_SUPPORTED_FILES_FOUND.value)

    # The output folder in which all the output data will be placed
    output_name = datetime.datetime.now().strftime("results_%Y.%m.%d_%H.%M.%S")
    output_dir = os.path.join(results_dir, output_name)
    # In case of an already existing path, add trailing '_'
    while os.path.exists(output_dir):
        output_dir = output_dir + '_'
    os.mkdir(output_dir)

    if __DEBUG_F__:
        print("DEBUG:\tOK, in output dir: ", output_dir)
        if path_to_analyze is not None:
            print("DEBUG:\tpathToAnalyze: " + path_to_analyze)
        print()

    # RUNNING THE EXTERNAL TOOLS
    t.run_tools(path_to_analyze, files_list, output_dir)
    raw_outputs = t.get_raw_output()

    if __DEBUG_F__:
        print("\nDEBUG. RESULTS:")
        print("TOKEI")
        print(raw_outputs["tokei"])
        print("\nCCCC")
        print(raw_outputs["cccc"])
        print("\nMI")
        print(raw_outputs["mi"])
        print("\nHALSTEAD")
        print(raw_outputs["halstead"])
        print("\n")

    formatted_outputs = t.get_output()

    json_output = json.dumps(formatted_outputs, sort_keys=True, indent=4)
    # REMEMBER: Json output *must* be printed to be viewed correctly.

    with open(os.path.join(output_name, output_name + ".json"), 'w') as output_file:
        json.dump(formatted_outputs, output_file, sort_keys=True, indent=4)

    return json_output, raw_outputs     # TODO: Delete raw_output


def main():     # TODO: Test this!
    if 2 > len(sys.argv) > 3 or "--help" in sys.argv or "-help" in sys.argv or "-h" in sys.argv:
        print("USAGE:\t" + sys.argv[0] + "<path to analyze> [<results dir>]", file=sys.stderr)
        print("\tDefault results dir: current directory.", file=sys.stderr)
        sys.exit(ExitCode.USAGE_HELP.value)

    analyze(tools_path=sys.argv[0], path_to_analyze=sys.argv[1], results_dir=sys.argv[2])
