import json
import os
import subprocess

from exit_codes import ExitCode, log_err

RCA_EXTENSIONS = [
    "c",
    "cc",
    "cpp",
    "c++",
    "h",
    "hpp",
    "hh",
    "rs",
]


class RustCodeAnalysis:
    def __init__(self, path):
        self.rust_code_analysis_path = os.path.join(
            path, "rust-code-analysis", "rust-code-analysis-cli"
        )

    def run_n_parse_rust_code_analysis(
        self, files_list: list, output_dir: os.path
    ):
        rust_code_analysis_output_res = self.run_tool_rust_code_analysis(
            files_list, output_dir
        )
        return json.loads(rust_code_analysis_output_res.decode())

    def run_tool_rust_code_analysis(self, files_list: list, output_dir: str):
        try:
            args = [
                self.rust_code_analysis_path,
                "-m",
                "-O",
                "json",
                "-p",
            ]
            args.extend(files_list)
            results = subprocess.run(args, capture_output=True, check=True)
            return results.stdout

        except subprocess.CalledProcessError as ex:
            log_err(
                "\trust-code-analysis exited with an error.\n{}\n{}\n",
                ExitCode.RUST_CODE_ANALYSIS_TOOL_ERR,
                ex.stdout,
                ex.stderr,
            )


def standardizer_rust_code_analysis(data):
    def _get_nom(metrics):
        nom = {}

        nom["functions"] = int(metrics["nom"]["functions"])
        nom["closures"] = int(metrics["nom"]["closures"])
        nom["total"] = int(metrics["nom"]["total"])

        return nom

    def _get_halstead(metrics):
        halstead = {}

        halstead["n1"] = int(metrics["halstead"]["n1"])
        halstead["n2"] = int(metrics["halstead"]["n2"])
        halstead["N1"] = int(metrics["halstead"]["N1"])
        halstead["N2"] = int(metrics["halstead"]["N2"])
        halstead["Vocabulary"] = int(metrics["halstead"]["vocabulary"])
        halstead["Length"] = int(metrics["halstead"]["length"])
        halstead["Volume"] = metrics["halstead"]["volume"]
        halstead["Difficulty"] = metrics["halstead"]["difficulty"]
        halstead["Effort"] = metrics["halstead"]["effort"]
        halstead["Programming time"] = metrics["halstead"]["time"]
        halstead["Estimated program length"] = metrics["halstead"][
            "estimated_program_length"
        ]
        halstead["Purity ratio"] = metrics["halstead"]["purity_ratio"]

        return halstead

    formatted_output = {"files": []}

    metrics = data["metrics"]
    per_file = {
        "filename": data["name"],
        "SLOC": int(metrics["loc"]["sloc"]),
        "PLOC": int(metrics["loc"]["ploc"]),
        "LLOC": int(metrics["loc"]["lloc"]),
        "CLOC": int(metrics["loc"]["cloc"]),
        "BLANK": int(metrics["loc"]["blank"]),
        "CC": metrics["cyclomatic"],
        "NARGS": int(metrics["nargs"]),
        "NEXITS": int(metrics["nexits"]),
        "NOM": _get_nom(metrics),
        "Halstead": _get_halstead(metrics),
        "functions": [],
    }

    for space in data["spaces"]:
        if space["kind"] == "function":
            space_file = {}
            space_file["function name"] = space["name"]
            space_file["line number"] = space["start_line"]

            space_metrics = space["metrics"]
            space_file["SLOC"] = int(space_metrics["loc"]["sloc"])
            space_file["PLOC"] = int(space_metrics["loc"]["ploc"])
            space_file["LLOC"] = int(space_metrics["loc"]["lloc"])
            space_file["CLOC"] = int(space_metrics["loc"]["cloc"])
            space_file["BLANK"] = int(space_metrics["loc"]["blank"])
            space_file["CC"] = space_metrics["cyclomatic"]
            space_file["NARGS"] = int(space_metrics["nargs"])
            space_file["NEXITS"] = int(space_metrics["nexits"])
            space_file["NOM"] = _get_nom(space_metrics)
            space_file["Halstead"] = _get_halstead(space_metrics)

            per_file["functions"].append(space_file)

    formatted_output["files"].append(per_file)

    return formatted_output


def helper_test_rust_code_analysis(standardized_output: dict, output: dict):
    tot_sloc = 0
    tot_ploc = 0
    tot_lloc = 0
    tot_cloc = 0
    tot_blank = 0

    for file in standardized_output["files"]:
        tot_sloc += file["SLOC"]
        tot_ploc += file["PLOC"]
        tot_lloc += file["LLOC"]
        tot_cloc += file["CLOC"]
        tot_blank += file["BLANK"]

    output["SLOC"] = tot_sloc
    output["PLOC"] = tot_ploc
    output["LLOC"] = tot_lloc
    output["CLOC"] = tot_cloc
    output["BLANK"] = tot_blank

    output["files"] = []

    for file in standardized_output["files"]:
        file_metrics = {
            "filename": file["filename"],
            "SLOC": file["SLOC"],
            "PLOC": file["PLOC"],
            "LLOC": file["LLOC"],
            "CLOC": file["CLOC"],
            "BLANK": file["BLANK"],
            "CC": file["CC"],
            "NARGS": file["NARGS"],
            "NEXITS": file["NEXITS"],
            "NOM": file["NOM"],
            "Halstead": file["Halstead"],
            "functions": file["functions"],
        }
        output["files"].append(file_metrics)
