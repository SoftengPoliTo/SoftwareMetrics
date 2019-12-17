#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import sys
from exit_codes import ExitCode
import output_unifier
import tools

__DEBUG_F__ = True


# TODO: AGGIUNGI CONTROLLO: SE GLI PASSO UN PROGETTO NON DEVE NEMMENO PARTIRE (FAI LA PROVA: passagli un progetto Java in input)
#  Controlla i files: se non c'è nessun .h, .c, .cpp, ... ALLORA deve dire "controlla che il path sia giusto"

#  SE c'è un file .java, TOKEI può analizzarlo... MA meglio che venga DROPPATO!!
# Dare in base al linguaggio la lista dei tools che si possono usare
# TODO: OUTPUT Json deve essere standardizzato
# TOGLI NOME TOOL dall' output


def list_of_files(path: os.path, accepted_extensions: list) -> list:
    """It returns a list containing all the files inside the given subdirectory that have a supported extension."""
    all_files = []
    _list_of_files(path, accepted_extensions, all_files)
    return all_files


def _list_of_files(path: os.path, accepted_extensions: list, output_list: list):
    for f in os.listdir(path):
        ff = os.path.join(path, f)
        if os.path.isdir(ff):  # If path is a DIR, recurse.
            _list_of_files(ff, accepted_extensions, output_list)

        elif os.path.isfile(ff):  # If path is a FILE, check its extension
            base_name = os.path.basename(f)
            extension = base_name[base_name.rfind(".") + 1:]
            if extension in accepted_extensions:
                output_list.append(ff)


def analyze(path_to_analyze, tools_path="/home/diego/Development/TESI/2_SoftwareMetrics/"):  # TODO: Delete the def. path
    if not os.path.exists(path_to_analyze):
        print("ERROR: the given path (" + path_to_analyze + ") does not exists.", file=sys.stderr)
        sys.exit(ExitCode.TARGET_DIR_NOT_FOUND.value)
    t = tools.Tools(tools_path)
    t.check_tools_existence()

    # Checking for analyzable files.
    supported_extensions = ["c", "cc", "cpp", "c++", "h", "hpp", "h++"]
    analyzable_files = list_of_files(path_to_analyze, supported_extensions)

    if len(analyzable_files) == 0:
        print("ERROR:\tthe given path does not contain any of the supported files.\n"
              "\tBe sure to pass the right folder to analyze.")
        sys.exit(ExitCode.NO_SUPPORTED_FILES_FOUND)

    # The output folder in which all the output data will be placed
    output_dir = datetime.datetime.now().strftime("results_%Y.%m.%d_%H.%M.%S")

    # In case of an already existing path, add trailing '_'
    while os.path.exists(output_dir):
        output_dir = output_dir + '_'
    os.mkdir(output_dir)

    # os.chdir(output_dir)
    # os.mkdir(os.path.join(output_dir, "outputs"))

    if __DEBUG_F__:
        print(" DEBUG: OK, in output dir: ", output_dir)
        print(" DEBUG: pathToAnalyze: " + path_to_analyze)
        print()

    # RUNNING THE EXTERNAL TOOLS
    raw_outputs = {}
    print("Running Tokei...")
    # Here we can call "run_n_parse_TOKEI" directly because Tokei can analyze a whole directory.
    raw_outputs["tokei"] = tools.run_n_parse_TOKEI(t, path_to_analyze, output_dir)

    print("Running CCCC...")
    # Here we must call "analyze_path" to call CCCC for each file
    raw_outputs["cccc"] = tools.analyze_path(tools, path_to_analyze, ["c", "cc", "cpp", "h"], tools.run_n_parse_CCCC, output_dir)
    # TODO: Li analizza i .h ? Ricontrolla nelle specs.

    print("Running M.I. Tool...")
    raw_outputs["mi"] = tools.run_n_parse_MI(t, path_to_analyze, output_dir)

    print("Running Halstead Metrics Tool... TODO")
    # ".h" files are not analyzed by Halstead Metrics Tool
    raw_outputs["halstead"] = tools.analyze_path(tools, path_to_analyze, ["c", "cc", "cpp"], tools.run_n_parse_HALSTEAD, output_dir)

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

    formatted_outputs = output_unifier.unifier(raw_outputs)
    return formatted_outputs, raw_outputs


def main():
    if len(sys.argv) != 2 or sys.argv[1] == "--help" or sys.argv[1] == "-help" or sys.argv[1] == "-h":
        print("USAGE: " + sys.argv[0] + "<path to analyze>", file=sys.stderr)
        sys.exit(ExitCode.USAGE_HELP.value)

    return analyze(tools_path=sys.argv[0], path_to_analyze=sys.argv[1])