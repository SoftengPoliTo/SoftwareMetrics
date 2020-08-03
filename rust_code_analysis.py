import json
import math
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
        list_of_files = {"files": []}
        for single_file in files_list:
            rust_code_analysis_output_res = self.run_tool_rust_code_analysis(
                single_file, output_dir
            )
            list_of_files["files"].append(
                json.loads(rust_code_analysis_output_res.decode())
            )

        return list_of_files

    def run_tool_rust_code_analysis(self, single_file: str, output_dir: str):
        try:
            args = [
                self.rust_code_analysis_path,
                "-m",
                "-O",
                "json",
                "-p",
            ]
            args.append(single_file)
            results = subprocess.run(args, capture_output=True, check=True)
            return results.stdout

        except subprocess.CalledProcessError as ex:
            log_err(
                "\trust-code-analysis exited with an error.\n{}\n{}\n",
                ExitCode.RUST_CODE_ANALYSIS_TOOL_ERR,
                ex.stdout,
                ex.stderr,
            )


def standardizer_rust_code_analysis(data_list):
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
        halstead["Level"] = metrics["halstead"]["level"]
        halstead["Effort"] = metrics["halstead"]["effort"]
        halstead["Programming time"] = metrics["halstead"]["time"]
        halstead["Bugs"] = metrics["halstead"]["bugs"]
        halstead["Estimated program length"] = metrics["halstead"][
            "estimated_program_length"
        ]
        halstead["Purity ratio"] = metrics["halstead"]["purity_ratio"]

        return halstead

    def _get_space(write_space, space_data):
        nspace = 0
        for space in space_data:
            nspace += 1
            space_file = {}
            space_file["name"] = space["name"]
            space_file["kind"] = space["kind"]
            space_file["start_line"] = space["start_line"]
            space_file["end_line"] = space["end_line"]

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

            if space["spaces"]:
                space_file["spaces"] = []
                nspace += _get_space(space_file, space["spaces"])

            write_space["spaces"].append(space_file)
        return nspace

    formatted_output = {"files": []}
    nspace = 0

    for data in data_list["files"]:
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
            "spaces": [],
        }

        nspace += _get_space(per_file, data["spaces"])

        formatted_output["files"].append(per_file)

    return (formatted_output, nspace)


def helper_test_rust_code_analysis(standardized_output: dict, nspace: int = 0):

    # FIXME: CC, MI
    print(nspace)
    tot_sloc = 0
    tot_ploc = 0
    tot_lloc = 0
    tot_cloc = 0
    tot_blank = 0
    tot_halstead_n1 = 0
    tot_halstead_n2 = 0
    tot_halstead_N1 = 0
    tot_halstead_N2 = 0
    tot_functions = 0
    tot_closures = 0
    tot_functions_and_closures = 0
    tot_nexits = 0
    tot_nargs = 0

    def _global_halstead():
        vocabulary = tot_halstead_n1 + tot_halstead_n2
        length = tot_halstead_N1 + tot_halstead_N2
        volume = length * math.log2(vocabulary)
        difficulty = tot_halstead_n1 / 2.0 * tot_halstead_N2 / tot_halstead_n2
        level = 1.0 / difficulty
        effort = difficulty * volume
        prog_time = effort / 18.0
        bugs = math.pow(effort, (2.0 / 3.0)) / 3000.0
        est_prog_length = tot_halstead_n1 * math.log2(
            tot_halstead_n1
        ) + tot_halstead_n2 * math.log2(tot_halstead_n2)
        purity_ratio = est_prog_length / length
        return {
            "n1": tot_halstead_n1,
            "n2": tot_halstead_n2,
            "N1": tot_halstead_N1,
            "N2": tot_halstead_N2,
            "Vocabulary": vocabulary,
            "Length": length,
            "Volume": volume,
            "Difficulty": difficulty,
            "Level": level,
            "Effort": effort,
            "Programming time": prog_time,
            "Bugs": bugs,
            "Estimated program length": est_prog_length,
            "Purity ratio": purity_ratio,
        }

    def _global_mi(
        sloc, cloc, cc, halstead_length, halstead_volume, halstead_vocabulary
    ):
        comments_percentage = cloc / sloc
        mi_visual_studio = (
            171.0
            - 5.2 * math.ln(halstead_volume)
            - 0.23 * cc
            - 16.2 * math.ln(sloc)
        )
        return {
            "mi_original": 171.0
            - 5.2 * math.ln(halstead_volume)
            - 0.23 * cc
            - 16.2 * math.ln(sloc),
            "mi_sei": 171.0
            - 5.2 * math.log2(halstead_volume)
            - 0.23 * cc
            - 16.2 * math.log2(sloc)
            + 50.0 * math.sin(math.sqrt(comments_peentage * 2.4)),
            "mi_visual_studio": math.max((formula * 100.0 / 171.0), 0.0),
        }

    def _global_nom():
        return {
            "functions": tot_functions,
            "closures": tot_closures,
            "total": tot_functions_and_closures,
        }

    for file in standardized_output["files"]:
        tot_sloc += file["SLOC"]
        tot_ploc += file["PLOC"]
        tot_lloc += file["LLOC"]
        tot_cloc += file["CLOC"]
        tot_blank += file["BLANK"]
        tot_halstead_n1 += file["Halstead"]["n1"]
        tot_halstead_n2 += file["Halstead"]["n2"]
        tot_halstead_N1 += file["Halstead"]["N1"]
        tot_halstead_N2 += file["Halstead"]["N2"]
        tot_functions += file["NOM"]["functions"]
        tot_closures += file["NOM"]["closures"]
        tot_functions_and_closures += file["NOM"]["total"]
        tot_nexits += file["NEXITS"]
        tot_nargs += file["NARGS"]

    output = {}

    output["SLOC"] = tot_sloc
    output["PLOC"] = tot_ploc
    output["LLOC"] = tot_lloc
    output["CLOC"] = tot_cloc
    output["BLANK"] = tot_blank
    output["HALSTEAD"] = _global_halstead()
    output["NOM"] = _global_nom()
    """output["MI"] = _global_mi(
        output["SLOC"],
        output["CLOC"],
        output["CC"],
        output["HALSTEAD"]["length"],
        output["HALSTEAD"]["volume"],
        output["HALSTEAD"]["vocabulary"]
    )"""
    output["NEXITS"] = tot_nexits
    output["NARGS"] = tot_nargs

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
            "spaces": file["spaces"],
        }
        output["files"].append(file_metrics)

    return output
