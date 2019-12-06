#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import subprocess
from enum import Enum
import output_unifier


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


def analyze_path(tool: Tools, path, accepted_extensions, run_tool_funct,
                 parse_results_funct, output_dir):  # throws FileNotFoundError if path is wrong
    results = []

    for f in os.listdir(path):
        ff = os.path.join(path, f)
        print("DEBUG: path: " + f)
        if os.path.isdir(ff):  # If path is a DIR, recurse.
            print("DEBUG: checkPath dir : " + f)
            res = analyze_path(tool, ff, accepted_extensions, run_tool_funct, parse_results_funct, output_dir)
            results.append(res)

        elif os.path.isfile(ff):  # If path is a FILE, check its extension
            base_name = os.path.basename(f)
            extension = base_name[base_name.rfind(".") + 1:]
            if extension in accepted_extensions:
                print("DEBUG: checkPath file: " + f)
                run_tool_funct(tool, ff, output_dir)
                parsed_result = parse_results_funct(
                    os.path.join(output_dir, "outputs"))  # TODO: Reformat and Delele this path.
                # parsed_result = output_unifier.cccc_output_reader(os.path.join(outputDir, "outputs", "cccc.xml"))
                results.append(parsed_result)
            # else:
            #    print("DEBUG:-checkPath file: " + f)
    return results


def run_CCCC_tool(tools: Tools, path_to_analyze, output_dir):   # TODO: try / catch!
    return subprocess.run([tools.CCCC, "--outdir=" + os.path.join(output_dir, "outputs"), path_to_analyze],
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
        print(ex.stdout)
        print(ex.stderr)
        print("")
        sys.exit(ExitCode.TOKEI_TOOL_ERR.value)


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

    os.mkdir(os.path.join(output_dir, "outputs"))

    # TODO: Cancellali
    print(" DEBUG: OK, in output dir: ", output_dir)
    print(" DEBUG: pathToAnalyze: " + path_to_analyze)
    print()

    # RUNNING THE EXTERNAL TOOLS

    print("Running Tokei...")
    # Here we can call "run_TOKEI_tool" directly because Tokei can analyze a whole directory.
    tokei_output_res = run_TOKEI_tool(tools, path_to_analyze, output_dir) #TODO: Check output
    tokei_output = output_unifier.tokei_output_reader(tokei_output_res)
    # output_unifier.tokei_output_reader( os.path.join(output_dir, ""))

    print("Running CCCC...")
    # Here we must call "analyze_path" to call CCCC for each file
    list_of_accepted_extensions = ["c","cc", "cpp", "h"]
    cccc_output = analyze_path(tools, path_to_analyze, list_of_accepted_extensions, run_CCCC_tool, output_unifier.cccc_output_reader, output_dir)
            # TODO: Li analizza i .h ? Ricontrolla nelle specs.

    print("Running M.I. Tool... TODO")
    mi_tool_res = run_MI_tool(tools, path_to_analyze)
    mi_output = output_unifier.mi_tool_output_reader(mi_tool_res)

    print("Running Halstead Metrics Tool... TODO")

    print("DEBUG. RESULTS:")
    print(tokei_output)
    print(cccc_output)
    print(mi_output)

def main():
    if len(sys.argv) != 2 or sys.argv[1] == "--help" or sys.argv[1] == "-help" or sys.argv[1] == "-h":
        print("USAGE: " + sys.argv[0] + "<path to analyze>", file=sys.stderr)
        sys.exit(ExitCode.USAGE_HELP.value)

    return analyze(tools_path=sys.argv[0], path_to_analyze=sys.argv[1])
