#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import datetime
import subprocess
from enum import Enum
import output_unifier

__DEBUG_F__  = True

class ExitCode(Enum):
    """Exit status codes."""
    USAGE_HELP = 1
    TOOLS_DIR_NOT_FOUND = 2
    TOOLS_NOT_FOUND = 3
    TARGET_DIR_NOT_FOUND = 4

    TOKEI_TOOL_ERR = 5
    CCCC_TOOL_ERR = 6
    MI_TOOL_ERR = 7
    HALSTEAD_TOOL_ERR = 8
###

# TODO: AGGIUNGI CONTROLLO: SE GLI PASSO UN PROGETTO NON DEVE NEMMENO PARTIRE (FAI LA PROVA: passagli un progetto Java in input)
#  Controlla i files: se non c'è nessun .h, .c, .cpp, ... ALLORA deve dire "controlla che il path sia giusto"

#  SE c'è un file .java, TOKEI può analizzarlo... MA meglio che venga DROPPATO!!
# Dare in base al linguaggio la lista dei tools che si possono usare
# TODO: OUTPUT Json deve essere standardizzato
# TOGLI NOME TOOL dall' output




class Tools:
    """Class containing all the available third-party tools, and their related information."""

    __toolsDir__ = "CC++_Tools"

    def __init__(self, wrapper_path=sys.argv[0]):
        self.directory = os.path.realpath(wrapper_path)
        self.baseDir = os.path.join(self.directory, self.__toolsDir__)

        # TOOLS
        self.CCCC = os.path.join(self.baseDir, "CCCC", "cccc")
        self.TOKEI = os.path.join(self.baseDir, "Tokei", "tokei")
        self.HALSTEAD_TOOL = os.path.join(self.baseDir, "Halstead_Metrics", "Halstead-Metrics.jar")
        self.MI_TOOL = os.path.join(self.baseDir, "Maintainability_Index", "lizard")

    def check_tools_existence(self):
        if not os.path.isdir(self.baseDir):
            print("ERROR: the directory containing the tools (" + self.__toolsDir__ + ") does not exists.", file=sys.stderr)
            sys.exit(ExitCode.TOOLS_DIR_NOT_FOUND.value)

        if os.path.isfile(self.CCCC) is False or os.path.isfile(self.TOKEI) is False or os.path.isfile(
                self.HALSTEAD_TOOL) is False or os.path.isfile(self.MI_TOOL) is False:
            print(
                "ERROR: one or more tools are missing.\nCheck the directory containing the tools (" + self.__toolsDir__ + ").",
                file=sys.stderr)
            sys.exit(ExitCode.EXIT_CODE__TOOLS_NOT_FOUND.value)

# End Class: Tools


def analyze_path(tool: Tools, path, accepted_extensions, run_n_parse_funct, # TODO: eliminalo.
                 output_dir):  # throws FileNotFoundError if path is wrong
    results = []

    for f in os.listdir(path):
        ff = os.path.join(path, f)
        if __DEBUG_F__:
            print("DEBUG: path: " + f)
        if os.path.isdir(ff):  # If path is a DIR, recurse.
            if __DEBUG_F__:
                print("DEBUG: checkPath dir : " + f)
            res = analyze_path(tool, ff, accepted_extensions, run_n_parse_funct, output_dir)
            results.append(res)

        elif os.path.isfile(ff):  # If path is a FILE, check its extension
            base_name = os.path.basename(f)
            extension = base_name[base_name.rfind(".") + 1:]
            if extension in accepted_extensions:
                if __DEBUG_F__:
                    print("DEBUG: checkPath file: " + f)
                parsed_result = run_n_parse_funct(tool, ff, output_dir)
                results.append(parsed_result)
            # else:
            #    print("DEBUG:-checkPath file: " + f)
    return results


def analyze_path_test(tool: Tools, path, accepted_extensions, run_n_parse_funct, output_dir):
    results = []
    _analyze_path_test(tool, path, accepted_extensions, run_n_parse_funct, output_dir, results )
    return results


def _analyze_path_test(tool: Tools, path, accepted_extensions, run_n_parse_funct,
                      output_dir, output_list: list):  # throws FileNotFoundError if path is wrong

    for f in os.listdir(path):
        ff = os.path.join(path, f)
        if __DEBUG_F__:
            print("DEBUG: path: " + f)
        if os.path.isdir(ff):  # If path is a DIR, recurse.
            if __DEBUG_F__:
                print("DEBUG: checkPath dir : " + f)
            _analyze_path_test(tool, ff, accepted_extensions, run_n_parse_funct, output_dir, output_list)

        elif os.path.isfile(ff):  # If path is a FILE, check its extension
            base_name = os.path.basename(f)
            extension = base_name[base_name.rfind(".") + 1:]
            if extension in accepted_extensions:
                if __DEBUG_F__:
                    print("DEBUG: checkPath file: " + f)
                parsed_result = run_n_parse_funct(tool, ff, output_dir)
                output_list.append(parsed_result)
            # else:
            #    print("DEBUG:-checkPath file: " + f)


def run_CCCC_tool(tools: Tools, path_to_analyze, output_dir):   # TODO: try / catch!
    outputs_subdir = os.path.join(output_dir, "outputs")
    if os.path.exists(outputs_subdir):  # Probably unnecessary, but it prevents the
        shutil.rmtree(outputs_subdir)
    os.mkdir(outputs_subdir)

    return subprocess.run([tools.CCCC, "--outdir=" + outputs_subdir, path_to_analyze],
                          capture_output=True, check=True)


def run_MI_tool(tools: Tools, path_to_analyze):   # TODO: try / catch!
    results = subprocess.run([tools.MI_TOOL, "-X", path_to_analyze], capture_output=True, check=True)
    return results.stdout


def run_TOKEI_tool(tools: Tools, path_to_analyze, output_dir):
    try:
        tokeiCommndOutput = subprocess.run([tools.TOKEI, "-o", "json", path_to_analyze], capture_output=True, check=True)
        return tokeiCommndOutput.stdout

    except subprocess.CalledProcessError as ex:
        print("Tokei exited with an error.", file=sys.stderr)
        print(ex.stdout, file=sys.stderr)
        print(ex.stderr, file=sys.stderr)
        print("", file=sys.stderr)
        sys.exit(ExitCode.TOKEI_TOOL_ERR.value)


def run_HALSTEAD_tool(tools: Tools, path_to_analyze, output_dir):  # TODO: try / catch
    #try:
    results = subprocess.run(["/usr/bin/java", "-Duser.country=US", "-Duser.language=en", "-jar", tools.HALSTEAD_TOOL, path_to_analyze], capture_output=True, check=True)
    return results.stdout
    #except subprocess.CalledProcessError as ex:
    #    if ex.returncode == 3:  # File extension not recognized


def run_n_parse_CCCC(tool: Tools, file: os.path, output_dir: str):
    run_CCCC_tool(tool, file, output_dir)
    return output_unifier.cccc_output_reader(os.path.join(output_dir, "outputs"))


def run_n_parse_TOKEI(tool: Tools, file: os.path, output_dir: str):
    tokei_output_res = run_TOKEI_tool(tool, file, output_dir)
    # TODO: Toglilo
    if __DEBUG_F__:
        print()
        print("\tTOKEI OUTPUT RAW:")
        print(tokei_output_res)
        print()
    return output_unifier.tokei_output_reader(tokei_output_res)


def run_n_parse_MI(tool: Tools, file: os.path, output_dir: str):
    mi_tool_res = run_MI_tool(tool, file)
    # TODO: Toglilo
    if __DEBUG_F__:
        print()
        print("\tMI OUTPUT RAW:")
        print(mi_tool_res)
        print()
    return output_unifier.mi_tool_output_reader(mi_tool_res)


def run_n_parse_HALSTEAD(tool: Tools, file: os.path, output_dir: str):
    hm_tool_res = run_HALSTEAD_tool(tool, file, output_dir)
    # TODO: Toglilo
    if __DEBUG_F__:
        print()
        print("\tHALSTEAD OUTPUT RAW:")
        print(hm_tool_res)
        print()
    return output_unifier.halstead_metric_tool_reader(hm_tool_res)


def analyze(path_to_analyze, tools_path="/home/diego/Development/TESI/2_SoftwareMetrics/"):  # TODO: Delete the def. path
    if not os.path.exists(path_to_analyze):
        print("ERROR: the given path (" + path_to_analyze + ") does not exists.", file=sys.stderr)
        sys.exit(ExitCode.TARGET_DIR_NOT_FOUND.value)

    tools = Tools(tools_path)
    tools.check_tools_existence()

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
    raw_outputs={}
    print("Running Tokei...")
    # Here we can call "run_n_parse_TOKEI" directly because Tokei can analyze a whole directory.
    raw_outputs["tokei"] = run_n_parse_TOKEI(tools, path_to_analyze, output_dir)

    print("Running CCCC...")
    # Here we must call "analyze_path" to call CCCC for each file
    #raw_outputs["cccc"] = analyze_path(tools, path_to_analyze, ["c", "cc", "cpp", "h"], run_n_parse_CCCC, output_dir)
    raw_outputs["cccc"] = analyze_path_test(tools, path_to_analyze, ["c", "cc", "cpp", "h"], run_n_parse_CCCC, output_dir)
    # TODO: Li analizza i .h ? Ricontrolla nelle specs.

    print("Running M.I. Tool...")
    raw_outputs["mi"] = run_n_parse_MI(tools, path_to_analyze, output_dir)

    print("Running Halstead Metrics Tool... TODO")
    # ".h" files are not analyzed by Halstead Metrics Tool
    raw_outputs["halstead"] = analyze_path_test(tools, path_to_analyze, ["c", "cc", "cpp"], run_n_parse_HALSTEAD, output_dir)

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
    return formatted_outputs,raw_outputs

def main():
    if len(sys.argv) != 2 or sys.argv[1] == "--help" or sys.argv[1] == "-help" or sys.argv[1] == "-h":
        print("USAGE: " + sys.argv[0] + "<path to analyze>", file=sys.stderr)
        sys.exit(ExitCode.USAGE_HELP.value)

    return analyze(tools_path=sys.argv[0], path_to_analyze=sys.argv[1])