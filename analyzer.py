#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import sys
from exit_codes import ExitCode
import output_unifier
import tools

__DEBUG_F__ = True


# TODO: AGGIUNGI CONTROLLO: SE GLI PASSO UN PROGETTO NON DEVE NEMMENO PARTIRE
#  (FAI LA PROVA: passagli un progetto Java in input)
#  Controlla i files: se non c'è nessun .h, .c, .cpp, ... ALLORA deve dire "controlla che il path sia giusto"

#  SE c'è un file .java, TOKEI può analizzarlo... MA meglio che venga DROPPATO!!
# Dare in base al linguaggio la lista dei tools che si possono usare
# TODO: OUTPUT Json deve essere standardizzato


def analyze(path_to_analyze, tools_path="/home/diego/Development/TESI/2_SoftwareMetrics/"):  # TODO: Delete the def path
    if not os.path.exists(path_to_analyze):
        print("ERROR:\tthe given path (" + path_to_analyze + ") does not exists.", file=sys.stderr)
        sys.exit(ExitCode.TARGET_DIR_NOT_FOUND.value)
    t = tools.Tools(tools_path)
    t.check_tools_existence()

    # Checking for analyzable files.
    if len(tools.list_of_files(path_to_analyze, tools.ACCEPTED_EXTENSIONS)) == 0:
        print("ERROR:\tthe given path does not contain any of the supported files.\n"
              "\tBe sure to pass the right folder to analyze.")
        sys.exit(ExitCode.NO_SUPPORTED_FILES_FOUND)

    # The output folder in which all the output data will be placed
    output_dir = datetime.datetime.now().strftime("results_%Y.%m.%d_%H.%M.%S")

    # In case of an already existing path, add trailing '_'
    while os.path.exists(output_dir):
        output_dir = output_dir + '_'
    os.mkdir(output_dir)

    if __DEBUG_F__:
        print(" DEBUG:\tOK, in output dir: ", output_dir)
        print(" DEBUG:\tpathToAnalyze: " + path_to_analyze)
        print()

    # RUNNING THE EXTERNAL TOOLS
    raw_outputs = t.run_tools(path_to_analyze, output_dir)

    if __DEBUG_F__:
        print("DEBUG. RESULTS:")
        print(raw_outputs["tokei"])
        print("\n")
        print(raw_outputs["cccc"])
        print("\n")
        print(raw_outputs["mi"])
        print("\n")
        print(raw_outputs["halstead"])
        print("\n")

    formatted_outputs = output_unifier.unifier(raw_outputs,
                                               tools.list_of_files(path_to_analyze, tools.ACCEPTED_EXTENSIONS))
    # TODO:↑ Move "list_of_tools(...)" from this point.

    return formatted_outputs, raw_outputs


def main():
    if len(sys.argv) != 2 or sys.argv[1] == "--help" or sys.argv[1] == "-help" or sys.argv[1] == "-h":
        print("USAGE: " + sys.argv[0] + "<path to analyze>", file=sys.stderr)
        sys.exit(ExitCode.USAGE_HELP.value)

    return analyze(tools_path=sys.argv[0], path_to_analyze=sys.argv[1])
