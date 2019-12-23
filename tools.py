#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import sys
from exit_codes import ExitCode
import output_unifier

__DEBUG_F__ = True
ACCEPTED_EXTENSIONS = ["c", "cc", "cpp", "c++", "h", "hpp", "h++"]


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
            print("ERROR:\tthe directory containing the tools ("
                  + self.__toolsDir__ + ") does not exists.", file=sys.stderr)
            sys.exit(ExitCode.TOOLS_DIR_NOT_FOUND.value)

        if os.path.isfile(self.CCCC) is False or os.path.isfile(self.TOKEI) is False or os.path.isfile(
                self.HALSTEAD_TOOL) is False or os.path.isfile(self.MI_TOOL) is False:
            print(
                "ERROR:\tone or more tools are missing.\nCheck the directory containing the tools ("
                + self.__toolsDir__ + ").", file=sys.stderr)
            sys.exit(ExitCode.EXIT_CODE__TOOLS_NOT_FOUND.value)

    def _run_tool_CCCC(self, path_to_analyze, output_dir):  # TODO: try / catch!
        outputs_subdir = os.path.join(output_dir, "outputs")
        if os.path.exists(outputs_subdir):  # Probably unnecessary, but it prevents the
            shutil.rmtree(outputs_subdir)
        os.mkdir(outputs_subdir)

        return subprocess.run([self.CCCC, "--outdir=" + outputs_subdir, path_to_analyze], capture_output=True,
                              check=True)

    def _run_tool_MI(self, path_to_analyze):  # TODO: try / catch!
        results = subprocess.run([self.MI_TOOL, "-X", path_to_analyze], capture_output=True, check=True)
        return results.stdout

    def _run_tool_TOKEI(self, path_to_analyze, output_dir):
        try:
            tokei_commnd_output = subprocess.run([self.TOKEI, "-o", "json", path_to_analyze], capture_output=True,
                                                 check=True)
            return tokei_commnd_output.stdout

        except subprocess.CalledProcessError as ex:
            print("ERROR:\tTokei exited with an error.", file=sys.stderr)
            print(ex.stdout, file=sys.stderr)
            print(ex.stderr, file=sys.stderr)
            print("", file=sys.stderr)
            sys.exit(ExitCode.TOKEI_TOOL_ERR.value)

    def _run_tool_HALSTEAD(self, path_to_analyze, output_dir):  # TODO: try / catch
        # try:
        results = subprocess.run(
            ["/usr/bin/java", "-Duser.country=US", "-Duser.language=en", "-jar", self.HALSTEAD_TOOL, path_to_analyze],
            capture_output=True, check=True)
        return results.stdout
        # except subprocess.CalledProcessError as ex:
        #    if ex.returncode == 3:  # File extension not recognized

    def run_n_parse_CCCC(self, file: os.path, output_dir: str):
        self._run_tool_CCCC(file, output_dir)
        return output_unifier.cccc_output_reader(os.path.join(output_dir, "outputs"))

    def run_n_parse_TOKEI(self, file: os.path, output_dir: str):
        tokei_output_res = self._run_tool_TOKEI(file, output_dir)
        return output_unifier.tokei_output_reader(tokei_output_res.decode())

    def run_n_parse_MI(self, file: os.path, output_dir: str):
        mi_tool_res = self._run_tool_MI(file)
        return output_unifier.mi_tool_output_reader(mi_tool_res.decode())

    def run_n_parse_HALSTEAD(self, file: os.path, output_dir: str):
        hm_tool_res = self._run_tool_HALSTEAD(file, output_dir)
        return output_unifier.halstead_metric_tool_reader(hm_tool_res)

    def run_tools(self, path_to_analyze, output_dir):   # TODO: path_to_analyze should be changed with the list of files / or it should go side to side.
        outputs = {}
        print("Running Tokei...")
        # Here we can call "run_n_parse_TOKEI" directly because Tokei can analyze a whole directory.
        outputs["tokei"] = self.run_n_parse_TOKEI(path_to_analyze, output_dir)

        print("Running CCCC...")
        # Here we must call "analyze_path" to call CCCC for each file
        outputs["cccc"] = analyze_path(self, path_to_analyze, ["c", "cc", "cpp", "h"],
                                       self.run_n_parse_CCCC, output_dir)
        # TODO: Li analizza i .h ? Ricontrolla nelle specs.

        print("Running M.I. Tool...")
        outputs["mi"] = self.run_n_parse_MI(path_to_analyze, output_dir)

        print("Running Halstead Metrics Tool... TODO")
        # ".h" files are not analyzed by Halstead Metrics Tool
        outputs["halstead"] = analyze_path(self, path_to_analyze, ["c", "cc", "cpp"],
                                           self.run_n_parse_HALSTEAD, output_dir)
        return outputs


# End Class: Tools


def analyze_path(tool: Tools, path, accepted_extensions, run_n_parse_funct, output_dir):
    results = []
    _analyze_path(tool, path, accepted_extensions, run_n_parse_funct, output_dir, results)
    return results


def _analyze_path(tool: Tools, path, accepted_extensions, run_n_parse_funct,
                  output_dir, output_list: list):  # throws FileNotFoundError if path is wrong

    for f in os.listdir(path):
        ff = os.path.join(path, f)
        if __DEBUG_F__:
            print("DEBUG:\tpath: " + f)
        if os.path.isdir(ff):  # If path is a DIR, recurse.
            if __DEBUG_F__:
                print("DEBUG:\tcheckPath dir : " + f)
            _analyze_path(tool, ff, accepted_extensions, run_n_parse_funct, output_dir, output_list)

        elif os.path.isfile(ff):  # If path is a FILE, check its extension
            base_name = os.path.basename(f)
            extension = base_name[base_name.rfind(".") + 1:]
            if extension in accepted_extensions:
                if __DEBUG_F__:
                    print("DEBUG:\tcheckPath file: " + f)
                parsed_result = run_n_parse_funct(ff, output_dir)
                output_list.append(parsed_result)
            # else:
            #    print("DEBUG:-checkPath file: " + f)


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