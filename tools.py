import os
import sys

import tokei
import halstead
import mi
import rust_code_analysis
import cccc

import output_unifier

from exit_codes import ExitCode, log_debug, log_err, log_info

ACCEPTED_EXTENSIONS = ["c", "cc", "cpp", "c++", "h", "hpp", "hh", "rs"]


class Tools:
    """
    Class containing all the available third-party tools, and
    their related information.
    """

    raw_output = {}
    files_to_analyze = {}

    def __init__(self, wrapper_path=sys.argv[0]):
        self.baseDir = os.path.realpath(wrapper_path)

        # TOOLS
        self.cccc_tool = cccc.Cccc(self.baseDir)
        self.halstead_tool = halstead.Halstead(self.baseDir)
        self.mi_tool = mi.Mi(self.baseDir)
        self.rca_tool = rust_code_analysis.RustCodeAnalysis(self.baseDir)
        self.tokei_tool = tokei.Tokei(self.baseDir)

        self._tool_matcher = {
            "mi": self.mi_tool.run_n_parse_mi,
            "tokei": self.tokei_tool.run_n_parse_tokei,
            "cccc": self.cccc_tool.run_n_parse_cccc,
            "halstead": self.halstead_tool.run_n_parse_halstead,
            "rust-code-analysis": self.rca_tool.run_n_parse_rust_code_analysis,
        }

        self._tool_extensions = {
            "mi": mi.MI_EXTENSIONS,
            "tokei": tokei.TOKEI_EXTENSIONS,
            "cccc": cccc.CCCC_EXTENSIONS,
            "halstead": halstead.HALSTEAD_EXCEPTIONS,
            "rust-code-analysis": rust_code_analysis.RCA_EXTENSIONS,
        }

        self._enabled_tools = list(self._tool_matcher.keys())

    def set_enabled_tools(self, enabled_tools):
        if enabled_tools:
            self._enabled_tools = enabled_tools

    def get_tools(self):
        return self._tool_matcher.keys()

    def get_enabled_tools(self):
        return self._enabled_tools

    def check_tools_existence(self):
        if not os.path.isdir(self.baseDir):
            log_err(
                "\tThe directory containing the tools ({}) does not exists.",
                ExitCode.TOOLS_DIR_NOT_FOUND,
                self.baseDir,
            )

        tool_path = {
            "tokei": self.tokei_tool.tokei_path,
            "rust-code-analysis": self.rca_tool.rust_code_analysis_path,
            "cccc": self.cccc_tool.cccc_path,
            "mi": self.mi_tool.mi_path,
            "halstead": self.halstead_tool.halstead_path,
        }

        for name in self._enabled_tools:
            if os.path.isfile(tool_path.get(name)) is False:
                log_err(
                    "\tOne or more tools are missing.\n"
                    "Check the directory containing the tools ({}).",
                    ExitCode.TOOLS_NOT_FOUND,
                    self.baseDir,
                )

    def _run_tool(self, name, tool_files, outputs, output_dir):
        print("Running {}...".format(name))
        run_tool = self._tool_matcher.get(name)
        outputs[name] = run_tool(tool_files, output_dir)

    def run_tools(
        self, path_to_analyze: os.path, files_list: list, output_dir: os.path
    ):
        """
        'path_to_analyze' is used if 'files_list' is None, or if the tool
        needs the path to calculate the correct results.
        """

        outputs = {}

        if not files_list:
            self.files_to_analyze = list_of_files(
                path_to_analyze, ACCEPTED_EXTENSIONS
            )
        else:
            self.files_to_analyze = files_list

        # Check extensions supported by tools
        filtered_files_per_tool = {}
        current_enabled_tools = [
            tool_name for tool_name in self._enabled_tools
        ]
        for tool_name in current_enabled_tools:
            filtered_files = _filter_unsupported_files(
                self.files_to_analyze, self._tool_extensions.get(tool_name)
            )

            log_debug("\t{} FILES_LIST:\n{}", tool_name, filtered_files)

            if not filtered_files:
                self._enabled_tools.remove(tool_name)
            else:
                filtered_files_per_tool[tool_name] = filtered_files

        # rust-code-analysis can read just a single json file
        rust_code_analysis_file = filtered_files_per_tool.get(
            "rust-code-analysis", None
        )
        if (
            rust_code_analysis_file
            and len(rust_code_analysis_file) != 1
            and os.path.isdir(rust_code_analysis_file[0])
        ):
            self._enabled_tools.remove("rust-code-analysis")

        for name in self._enabled_tools:
            self._run_tool(
                name, filtered_files_per_tool[name], outputs, output_dir
            )

        self.raw_output = outputs

    def get_tool_output(self, tool_name):
        return self.raw_output.get(tool_name, {})

    def get_output(self, one_json_per_tool):
        return output_unifier.unifier(
            self, self.files_to_analyze, one_json_per_tool
        )


def analyze_path(
    tool: Tools, path, accepted_extensions, run_n_parse_funct, output_dir
):
    results = []
    _analyze_path(
        tool, path, accepted_extensions, run_n_parse_funct, output_dir, results
    )
    return results


def _analyze_path(
    tool: Tools,
    path,
    accepted_extensions,
    run_n_parse_funct,
    output_dir,
    output_list: list,
):  # throws FileNotFoundError if path is wrong

    for f in os.listdir(path):
        ff = os.path.join(path, f)
        log_debug("\tpath: {}", f)
        if os.path.isdir(ff):  # If path is a DIR, recurse.
            log_debug("\t'_analyze_path': dir: {}", f)
            _analyze_path(
                tool,
                ff,
                accepted_extensions,
                run_n_parse_funct,
                output_dir,
                output_list,
            )

        elif os.path.isfile(ff):  # If path is a FILE, check its extension
            base_name = os.path.basename(f)
            extension = base_name[base_name.rfind(".") + 1 :]
            if extension in accepted_extensions:
                log_debug("\t'_analyze_path': file: {}", f)
                parsed_result = run_n_parse_funct(ff, output_dir)
                output_list.append(parsed_result)


def list_of_files(path: os.path, accepted_extensions: list) -> list:
    """
    It returns a list containing all the files inside the given subdirectory
    that have a supported extension.
    """

    all_files = []
    _list_of_files(path, accepted_extensions, all_files)
    return all_files


def _list_of_files(
    path: os.path, accepted_extensions: list, output_list: list
):
    if os.path.isfile(path):
        base_name = os.path.basename(path)
        extension = base_name[base_name.rfind(".") + 1 :]
        if extension in accepted_extensions:
            output_list.append(path)

    elif os.path.isdir(path):
        for f in os.listdir(path):
            ff = os.path.join(path, f)
            _list_of_files(ff, accepted_extensions, output_list)

    else:
        log_info(
            "\tThe analyzed path ({}) is neither a file or a directory, "
            "it will be skipped.",
            path,
        )


def _filter_unsupported_files(files_list: list, accepted_extensions: list):
    supported_files = []
    for file in files_list:
        base_name = os.path.basename(file)
        extension = base_name[base_name.rfind(".") + 1 :]
        if extension in accepted_extensions:
            supported_files.append(file)
    return supported_files
