import json
import os
import subprocess

from exit_codes import ExitCode, log_debug, log_err

TOKEI_EXTENSIONS = ["c", "cc", "cpp", "c++", "h", "hpp", "hh", "rs"]


class Tokei:
    def __init__(self, path):
        self.tokei_path = os.path.join(path, "Tokei", "tokei")

    def run_n_parse_tokei(self, files_list: list, output_dir: os.path):
        tokei_output_res = self.run_tool_tokei(files_list)
        return json.loads(tokei_output_res.decode())

    def run_tool_tokei(self, files_list: list):
        try:
            args = [self.tokei_path, "-o", "json"]
            args.extend(files_list)
            results = subprocess.run(args, capture_output=True, check=True)
            return results.stdout

        except subprocess.CalledProcessError as ex:
            log_err(
                "\tTokei exited with an error.\n{}\n{}\n",
                ExitCode.TOKEI_TOOL_ERR,
                ex.stdout,
                ex.stderr,
            )


def standardizer_tokei(data):
    formatted_output = {"files": []}

    for d in data:
        for reports in data[d]["reports"]:

            s = reports["stats"]
            per_file = {
                "filename": reports["name"],
                "SLOC": int(s["code"]) + int(s["comments"]) + int(s["blanks"]),
                "PLOC": s["code"],
                "CLOC": s["comments"],
                "BLANK": s["blanks"],
                "spaces": [],  # Tokei does not consider per-spaces information
            }

            # Tokei discriminates CHeaders from CppHeaders from the extension.
            # That is why I decided to unify CHeader and CppHeader.
            if d in ["CHeader", "CppHeader"]:
                per_file["type"] = "C/CppHeader"
            else:
                per_file["type"] = d

            formatted_output["files"].append(per_file)

    return (formatted_output, 0)


def helper_test_tokei(standardized_output: dict, spaces=0):
    tot_sloc = 0
    tot_ploc = 0
    tot_cloc = 0
    tot_blank = 0

    for file in standardized_output["files"]:
        tot_sloc += file["SLOC"]
        tot_ploc += file["PLOC"]
        tot_cloc += file["CLOC"]
        tot_blank += file["BLANK"]

    output = {}
    output["SLOC"] = tot_sloc
    output["PLOC"] = tot_ploc
    output["CLOC"] = tot_cloc
    output["BLANK"] = tot_blank
    output["files"] = []

    for file in standardized_output["files"]:
        file_metrics = {
            "filename": file["filename"],
            "type": file["type"],
            "SLOC": file["SLOC"],
            "PLOC": file["PLOC"],
            "CLOC": file["CLOC"],
            "BLANK": file["BLANK"],
            "spaces": file["spaces"],
        }
        output["files"].append(file_metrics)

    return output
