#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import sys
from exit_codes import ExitCode
import output_unifier
import logging

ACCEPTED_EXTENSIONS = ["c", "cc", "cpp", "c++", "h", "hpp", "hh"]

_SUPPORTED_EXTENSIONS_CCCC_ = ["c", "cc", "cpp", "c++", "h", "hpp", "hh"]
_SUPPORTED_EXTENSIONS_TOKEI_ = ACCEPTED_EXTENSIONS  # [""]   # Tokei supports a huge variety of languages
_SUPPORTED_EXTENSIONS_HALSTEAD_TOOL_ = ["c", "cc", "cpp", "c++"]
_SUPPORTED_EXTENSIONS_MI_TOOL_ = ["c", "cc", "cpp", "c++"]


class Tools:
    """Class containing all the available third-party tools, and their related information."""

    raw_output = {}
    files_to_analyze = {}

    def __init__(self, wrapper_path=sys.argv[0]):
        self.baseDir = os.path.realpath(wrapper_path)

        # TOOLS
        self.CCCC = os.path.join(self.baseDir, "CCCC", "cccc")
        self.TOKEI = os.path.join(self.baseDir, "Tokei", "tokei")
        self.HALSTEAD_TOOL = os.path.join(self.baseDir, "Halstead_Metrics", "Halstead-Metrics.jar")
        self.MI_TOOL = os.path.join(self.baseDir, "Maintainability_Index", "lizard")

    def check_tools_existence(self):
        if not os.path.isdir(self.baseDir):
            logging.error("\tthe directory containing the tools (%s) does not exists.", self.baseDir)
            sys.exit(ExitCode.TOOLS_DIR_NOT_FOUND.value)

        if os.path.isfile(self.CCCC) is False or os.path.isfile(self.TOKEI) is False or os.path.isfile(
                self.HALSTEAD_TOOL) is False or os.path.isfile(self.MI_TOOL) is False:
            logging.error("\tone or more tools are missing.\n"
                          "Check the directory containing the tools (%s).", self.baseDir)
            sys.exit(ExitCode.TOOLS_NOT_FOUND.value)

    def _run_tool_cccc(self, files_list: list, output_dir: str):
        try:
            files = _filter_unsupported_files(files_list, _SUPPORTED_EXTENSIONS_CCCC_)
            outputs_subdir = os.path.join(output_dir, "outputs")
            if os.path.exists(outputs_subdir):  # Probably unnecessary, but it prevents the
                shutil.rmtree(outputs_subdir)
            os.mkdir(outputs_subdir)

            args = [self.CCCC, "--outdir=" + outputs_subdir]
            args.extend(files)
            return subprocess.run(args, capture_output=True, check=True)

        except subprocess.CalledProcessError as ex:
            logging.error("\tCCCC exited with an error.\n%s\n%s\n", ex.stdout, ex.stderr)
            sys.exit(ExitCode.CCCC_TOOL_ERR.value)

    def _run_tool_mi(self, files_list: list):
        try:
            args = [self.MI_TOOL, "-X"]
            args.extend(files_list)
            results = subprocess.run(args, capture_output=True, check=True)
            return results.stdout

        except subprocess.CalledProcessError as ex:
            logging.error("\tMaintainability Index Tool exited with an error.\n%s\n%s\n", ex.stdout, ex.stderr)
            sys.exit(ExitCode.MI_TOOL_ERR.value)

    def _run_tool_tokei(self, files_list: list):
        try:
            args = [self.TOKEI, "-o", "json"]
            args.extend(files_list)
            results = subprocess.run(args, capture_output=True, check=True)
            return results.stdout

        except subprocess.CalledProcessError as ex:
            logging.error("\tTokei exited with an error.\n%s\n%s\n", ex.stdout, ex.stderr)
            sys.exit(ExitCode.TOKEI_TOOL_ERR.value)

    def _run_tool_halstead(self, path_to_analyze: str):
        try:
            results = subprocess.run(
                ["/usr/bin/java", "-Duser.country=US", "-Duser.language=en",
                 "-jar", self.HALSTEAD_TOOL, path_to_analyze],
                capture_output=True, check=True)
            return results.stdout

        except subprocess.CalledProcessError as ex:
            logging.error("\tHalstead Metric Tool exited with an error.\n%s\n%s\n", ex.stdout, ex.stderr)
            sys.exit(ExitCode.HALSTEAD_TOOL_ERR.value)

    def run_n_parse_cccc(self, files_list: list, output_dir: os.path):
        filtered_files = _filter_unsupported_files(files_list, _SUPPORTED_EXTENSIONS_CCCC_)
        self._run_tool_cccc(filtered_files, output_dir)
        return output_unifier.cccc_output_reader(os.path.join(output_dir, "outputs"))

    def run_n_parse_tokei(self, files_list: list, output_dir: os.path):
        filtered_files = _filter_unsupported_files(files_list, _SUPPORTED_EXTENSIONS_TOKEI_)
        logging.debug("\tFILTERED FILES:\n%s", filtered_files)
        tokei_output_res = self._run_tool_tokei(filtered_files)
        return output_unifier.tokei_output_reader(tokei_output_res.decode())

    def run_n_parse_mi(self, files_list: list, output_dir: os.path):
        filtered_files = _filter_unsupported_files(files_list, _SUPPORTED_EXTENSIONS_MI_TOOL_)
        mi_tool_res = self._run_tool_mi(filtered_files)
        return output_unifier.mi_tool_output_reader(mi_tool_res.decode())

    def run_n_parse_halstead(self, files_list: list, output_dir: os.path):
        filtered_files = _filter_unsupported_files(files_list, _SUPPORTED_EXTENSIONS_HALSTEAD_TOOL_)
        results = []
        for file in filtered_files:
            results.append(self._run_n_parse_halstead(file, output_dir))
        return results

    def run_n_parse_halstead_dir(self, path_to_analyze: os.path, output_dir: os.path):
        return analyze_path(self, path_to_analyze, _SUPPORTED_EXTENSIONS_HALSTEAD_TOOL_,
                            self._run_n_parse_halstead, output_dir)

    def _run_n_parse_halstead(self, file: os.path, output_dir: str):
        hm_tool_res = self._run_tool_halstead(file)
        return output_unifier.halstead_metric_tool_reader(hm_tool_res)

    def run_tools(self, path_to_analyze: os.path, files_list: list, output_dir: os.path):
        """'path_to_analyze' is used if 'files_list' is None, or if the tool needs the path to calculate the correct
        results. """
        outputs = {}

        if files_list is None:
            self.files_to_analyze = list_of_files(path_to_analyze, ACCEPTED_EXTENSIONS)
        else:
            self.files_to_analyze = files_list
        logging.debug("\tFILES_LIST:\n%s", self.files_to_analyze)

        print("Running Tokei...")
        outputs["tokei"] = self.run_n_parse_tokei(self.files_to_analyze, output_dir)

        print("Running CCCC...")
        outputs["cccc"] = self.run_n_parse_cccc(self.files_to_analyze, output_dir)

        print("Running M.I. Tool...")
        outputs["mi"] = self.run_n_parse_mi(self.files_to_analyze, output_dir)

        print("Running Halstead Metrics Tool... (this may take a while)")
        outputs["halstead"] = self.run_n_parse_halstead(self.files_to_analyze, output_dir)
        self.raw_output = outputs

    def get_raw_output(self):
        return self.raw_output

    def get_output(self):
        return output_unifier.unifier(self.raw_output, self.files_to_analyze)

# End Class: Tools


def analyze_path(tool: Tools, path, accepted_extensions, run_n_parse_funct, output_dir):
    results = []
    _analyze_path(tool, path, accepted_extensions, run_n_parse_funct, output_dir, results)
    return results


def _analyze_path(tool: Tools, path, accepted_extensions, run_n_parse_funct,
                  output_dir, output_list: list):  # throws FileNotFoundError if path is wrong

    for f in os.listdir(path):
        ff = os.path.join(path, f)
        logging.debug("\tpath: %s", f)
        if os.path.isdir(ff):  # If path is a DIR, recurse.
            logging.debug("\t'_analyze_path': dir: %s", f)
            _analyze_path(tool, ff, accepted_extensions, run_n_parse_funct, output_dir, output_list)

        elif os.path.isfile(ff):  # If path is a FILE, check its extension
            base_name = os.path.basename(f)
            extension = base_name[base_name.rfind(".") + 1:]
            if extension in accepted_extensions:
                logging.debug("\t'_analyze_path': file: %s", f)
                parsed_result = run_n_parse_funct(ff, output_dir)
                output_list.append(parsed_result)


def list_of_files(path: os.path, accepted_extensions: list) -> list:
    """It returns a list containing all the files inside the given subdirectory that have a supported extension."""
    all_files = []
    _list_of_files(path, accepted_extensions, all_files)
    return all_files


def _list_of_files(path: os.path, accepted_extensions: list, output_list: list):
    if os.path.isfile(path):
        base_name = os.path.basename(path)
        extension = base_name[base_name.rfind(".") + 1:]
        if extension in accepted_extensions:
            output_list.append(path)

    elif os.path.isdir(path):
        for f in os.listdir(path):
            ff = os.path.join(path, f)
            _list_of_files(ff, accepted_extensions, output_list)

    else:
        logging.info("\tThe analyzed path (%s) is neither a file or a directory, it will be skipped.", path)


def _filter_unsupported_files(files_list: list, accepted_extensions: list):
    supported_files = []
    for file in files_list:
        base_name = os.path.basename(file)
        extension = base_name[base_name.rfind(".") + 1:]
        if extension in accepted_extensions:
            supported_files.append(file)
    return supported_files
