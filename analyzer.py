#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import sys

import tools
from exit_codes import ExitCode, log_conf, log_debug, log_err


def compile_commands_reader(json_file: os.path) -> list:
    if not os.path.isfile(json_file):
        log_err(
            "\t'{}' is not a valid file. Check the path you have provided.",
            ExitCode.COMPILE_COMMAND_FILE_ERROR,
            json_file,
        )

    base_name = os.path.basename(json_file)
    if base_name[base_name.rfind(".") + 1 :] != "json":
        log_err(
            "\t'{}' is not a Json file.",
            ExitCode.COMPILE_COMMAND_FILE_ERROR,
            json_file,
        )

    with open(json_file, "r") as json_fp:
        c_commands = json.load(json_fp)

    files = []
    try:
        for i in c_commands:
            files.append(os.path.join(i["directory"], i["file"]))

    except KeyError:
        log_err(
            "\t'{}' is not a valid \"compile_commands\" file.",
            ExitCode.COMPILE_COMMAND_FILE_ERROR,
            json_file,
        )

    return list(dict.fromkeys(files).keys())


def check_tools_correctness(tools, enabled_tools):
    check = [name for name in tools if name in enabled_tools]
    return check


def save_output(output, path):
    json_output = json.dumps(output, indent=4)

    with open(path, "w") as output_file:
        json.dump(output, output_file, indent=4)

    return json_output


def analyze(
    enabled_tools,
    test_mode,
    path_to_analyze=None,
    files_list=None,
    results_dir=".",
    tools_path="./CC++_Tools",
):
    if path_to_analyze is None and files_list is None:
        log_err(
            "\teither a path to analyze, or "
            "a list of files must be passed to function 'analyze'.",
            ExitCode.PROGRAMMING_ERROR,
        )

    if not os.path.isdir(results_dir):
        log_err(
            "\tthe results path ( {} ) does not exists.",
            ExitCode.TARGET_DIR_NOT_FOUND,
            results_dir,
        )

    t = tools.Tools(tools_path)

    if enabled_tools:
        tool = t.get_tools()
        correct_tools = check_tools_correctness(tool, enabled_tools)
        t.set_enabled_tools(correct_tools)

    t.check_tools_existence()

    # Checking for analyzable files.
    if path_to_analyze is not None and not tools.list_of_files(
        path_to_analyze, tools.ACCEPTED_EXTENSIONS
    ):
        log_err(
            "\tthe given path does not contain any of the supported files.\n"
            "\tBe sure to pass the right folder to analyze.",
            ExitCode.NO_SUPPORTED_FILES_FOUND,
        )

    output_dir = results_dir
    if test_mode:
        output_name = os.path.basename(os.path.normpath(results_dir))
    else:
        # The output folder in which all the output data will be placed
        output_name = datetime.datetime.now().strftime(
            "results_%Y.%m.%d_%H.%M.%S"
        )

        output_dir = os.path.join(output_dir, output_name)

        # In case of an already existing path, add trailing '_'
        while os.path.exists(output_dir):
            output_dir = output_dir + "_"
        os.mkdir(output_dir)

    log_debug("\tOK, in output dir: {}", output_dir)
    if path_to_analyze is not None:
        log_debug("\tpathToAnalyze: {}", path_to_analyze)
    else:
        log_debug("\tfiles_list: {}", files_list)
    log_debug("")

    # RUNNING THE EXTERNAL TOOLS
    t.run_tools(path_to_analyze, files_list, output_dir)

    log_debug(
        "\tRAW RESULTS:\n"
        "TOKEI:\n {} "
        "\n\nRUST-CODE-ANALYSIS:\n {}"
        "\n\nCCCC:\n"
        "{}"
        "\n\nMI:\n {}"
        "\n\nHALSTEAD:\n {}\n",
        t.get_tool_output("tokei"),
        t.get_tool_output("rust-code-analysis"),
        t.get_tool_output("cccc"),
        t.get_tool_output("mi"),
        t.get_tool_output("halstead"),
    )

    formatted_outputs = t.get_output(test_mode)

    json_outputs = {}
    if test_mode:
        for tool in t.get_enabled_tools():
            path = os.path.join(output_dir, output_name + "_" + tool + ".json")
            json_output = save_output(formatted_outputs[tool], path)
            json_outputs[tool] = json_output
    else:
        path = os.path.join(output_dir, output_name + ".json")
        json_output = save_output(formatted_outputs["all"], path)
        json_outputs["all"] = json_output

    print("Results have been written in folder: '" + output_name + "'")

    return json_outputs


def main():
    parser = argparse.ArgumentParser(
        description="A program to calculate various source code metrics, "
        "aggregating the results obtained from different tools.",
        epilog="The manual and the source code of this program can be found on"
        " GitHub at https://github.com/SoftengPoliTo/SoftwareMetrics",
    )

    # Optional args
    parser.add_argument(
        "-v",
        "--verbosity",
        action="store_true",
        help="Increase output verbosity, useful for debugging purposes",
    )

    parser.add_argument(
        "-tm",
        "--test-mode",
        action="store_true",
        help="Run the analyzer in test mode",
    )

    parser.add_argument(
        "-t",
        "--tools",
        type=str,
        nargs="+",
        help="List of tools to be executed",
    )

    # Args
    parser.add_argument(
        "results_dir",  # "-r", "--results",
        metavar="results dir",
        type=str,
        default=".",
        nargs="?",
        help="The directory in which to save the results",
    )

    # Input from paths OR compile_commands.json
    paths_or_json = parser.add_mutually_exclusive_group(required=True)
    # required=True means that at least one option must be present

    paths_or_json.add_argument(
        "-p",
        "--path",  # "paths_to_analyze",
        type=str,
        help="The PATH (directory(ies) / file(s)) to analyze",
    )

    paths_or_json.add_argument(
        "-c",
        type=str,
        metavar="FILE.json",  # action="store",
        help="The path to the 'compile_commands.json' file",
    )

    args = parser.parse_args()

    log_conf(args.verbosity)

    log_debug("\targs={}", vars(args))
    print(os.path.dirname(os.path.realpath(sys.argv[0])))

    files_list = None
    if args.c is not None:
        files_list = compile_commands_reader(args.c)

    analyze(
        args.tools,
        args.test_mode,
        path_to_analyze=args.path,
        files_list=files_list,
        tools_path=os.path.join(
            os.path.dirname(os.path.realpath(sys.argv[0])), "CC++_Tools"
        ),
        results_dir=args.results_dir,
    )


if __name__ == "__main__":
    main()
