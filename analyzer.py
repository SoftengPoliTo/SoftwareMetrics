#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import sys

from exit_codes import ExitCode
import tools
import json
import argparse
import logging


def compile_commands_reader(json_file: os.path) -> list:
    if not os.path.isfile(json_file):
        logging.error(
            "\t'{}' is not a valid file. Check the path you have provided.",
            json_file,
        )
        sys.exit(ExitCode.COMPILE_COMMAND_FILE_ERROR.value)

    base_name = os.path.basename(json_file)
    if base_name[base_name.rfind(".") + 1 :] != "json":
        logging.error("\t'{}' is not a Json file.", json_file)
        sys.exit(ExitCode.COMPILE_COMMAND_FILE_ERROR.value)

    with open(json_file, "r") as json_fp:
        c_commands = json.load(json_fp)

    files = []
    try:
        for i in c_commands:
            files.append(os.path.join(i["directory"], i["file"]))

    except KeyError:
        logging.error(
            "\t'{}' is not a valid \"compile_commands\" file.", json_file
        )
        sys.exit(ExitCode.COMPILE_COMMAND_FILE_ERROR.value)

    return files


def analyze(
    enabled_tools,
    save_json_with_dirname,
    path_to_analyze=None,
    files_list=None,
    results_dir=".",
    tools_path="./CC++_Tools",
):
    if path_to_analyze is None and files_list is None:
        logging.error(
            "\teither a path to analyze, or "
            "a list of files must be passed to function 'analyze'."
        )
        sys.exit(ExitCode.PROGRAMMING_ERROR.value)

    if not os.path.isdir(results_dir):
        logging.error(
            "\tthe results path ( {} ) does not exists.", results_dir
        )
        sys.exit(ExitCode.TARGET_DIR_NOT_FOUND.value)

    t = tools.Tools(tools_path)
    t.check_tools_existence()

    if enabled_tools:
        t.set_enabled_tools(enabled_tools)

    # Checking for analyzable files.
    if path_to_analyze is not None and not tools.list_of_files(
        path_to_analyze, tools.ACCEPTED_EXTENSIONS
    ):
        logging.error(
            "\tthe given path does not contain any of the supported files.\n"
            "\tBe sure to pass the right folder to analyze."
        )
        sys.exit(ExitCode.NO_SUPPORTED_FILES_FOUND.value)

    output_dir = results_dir
    if save_json_with_dirname:
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

    logging.debug("\tOK, in output dir: {}", output_dir)
    if path_to_analyze is not None:
        logging.debug("\tpathToAnalyze: {}", path_to_analyze)
    else:
        logging.debug("\tfiles_list: {}", files_list)
    logging.debug("")

    # RUNNING THE EXTERNAL TOOLS
    t.run_tools(path_to_analyze, files_list, output_dir)

    logging.debug(
        "\tRAW RESULTS:\n" "TOKEI:\n {} "
        # "\n\nRUST-CODE-ANALYSIS:\n"
        # "{}"
        "\n\nCCCC:\n" "{}" "\n\nMI:\n {}" "\n\nHALSTEAD:\n {}\n",
        t.get_tool_output("tokei"),
        t.get_tool_output("rust-code-analysis"),
        t.get_tool_output("cccc"),
        t.get_tool_output("mi"),
        t.get_tool_output("halstead"),
    )

    formatted_outputs = t.get_output()

    json_output = json.dumps(formatted_outputs, sort_keys=True, indent=4)
    # REMEMBER: Json output *must* be printed to be viewed correctly.

    with open(
        os.path.join(output_dir, output_name + ".json"), "w"
    ) as output_file:
        json.dump(formatted_outputs, output_file, sort_keys=True, indent=4)
    print("Results have been written in folder: '" + output_name + "'")

    return json_output


def main():
    parser = argparse.ArgumentParser(
        # prog='myls',                      # Custom program name
        # usage='%(prog)s [options] path',  # Custom usage message
        # add_help=False,                   # Delete the default help message
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
        "-s",
        "--save",
        action="store_true",
        help="Set json filename to the name of the output directory",
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

    if args.verbosity:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logging.debug("\targs={}", vars(args))
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    print(os.path.dirname(os.path.realpath(sys.argv[0])))

    files_list = None
    if args.c is not None:
        files_list = compile_commands_reader(args.c)

    analyze(
        args.tools,
        args.save,
        path_to_analyze=args.path,
        files_list=files_list,
        tools_path=os.path.join(
            os.path.dirname(os.path.realpath(sys.argv[0])), "CC++_Tools"
        ),
        results_dir=args.results_dir,
    )


if __name__ == "__main__":
    main()
