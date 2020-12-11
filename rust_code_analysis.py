import json
import math
import os
import pathlib
import subprocess
import typing as T

from exit_codes import ExitCode, log_err

RCA_EXTENSIONS = [
    "c",
    "cc",
    "cpp",
    "c++",
    "h",
    "hpp",
    "hh",
    "js",
    "py",
    "rs",
    "ts",
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
                "--pr",
                "-p",
            ]
            args.append(single_file)
            results = subprocess.run(args, capture_output=True, check=True)

            input_name = pathlib.Path(single_file).name
            filename = "rca-json/" + input_name + ".json"

            with open(filename, "w") as f:
                f.write(results.stdout.decode("utf-8"))

            return results.stdout

        except subprocess.CalledProcessError as ex:
            log_err(
                "\trust-code-analysis exited with an error.\n{}\n{}\n",
                ExitCode.RUST_CODE_ANALYSIS_TOOL_ERR,
                ex.stdout,
                ex.stderr,
            )


def standardizer_rust_code_analysis(data_list):
    def _get_cc(metrics):
        cc = {}
        cc["sum"] = int(metrics["cyclomatic"]["sum"])
        cc["average"] = metrics["cyclomatic"]["average"]

        return cc

    def _get_cognitive(metrics):
        cognitive = {}
        cognitive["sum"] = int(metrics["cognitive"]["sum"])
        # Deciding upstream whether to return null or 0
        # when there are no functions/closures
        cognitive["average"] = (
            metrics["cognitive"]["average"]
            if metrics["cognitive"]["average"]
            else 0.0
        )

        return cognitive

    def _get_nargs(metrics):
        nargs = {}
        nargs["sum"] = int(metrics["nargs"]["sum"])
        # Deciding upstream whether to return null or 0
        # when there are no functions/closures
        nargs["average"] = (
            metrics["nargs"]["average"] if metrics["nargs"]["average"] else 0.0
        )

        return nargs

    def _get_nexits(metrics):
        nexits = {}
        nexits["sum"] = int(metrics["nexits"]["sum"])
        # Deciding upstream whether to return null or 0
        # when there are no functions/closures
        nexits["average"] = (
            metrics["nexits"]["average"]
            if metrics["nexits"]["average"]
            else 0.0
        )

        return nexits

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

    def _get_mi(metrics):
        mi = {}
        mi["Original"] = metrics["mi"]["mi_original"]
        mi["Sei"] = metrics["mi"]["mi_sei"]
        mi["Visual Studio"] = metrics["mi"]["mi_visual_studio"]

        return mi

    def _get_space(write_space, space_data):
        nspace = 0
        for space in space_data:
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
            space_file["CC"] = _get_cc(space_metrics)
            space_file["COGNITIVE"] = _get_cognitive(space_metrics)
            space_file["NARGS"] = _get_nargs(space_metrics)
            space_file["NEXITS"] = _get_nexits(space_metrics)
            space_file["NOM"] = _get_nom(space_metrics)
            space_file["Halstead"] = _get_halstead(space_metrics)
            space_file["Mi"] = _get_mi(space_metrics)

            nspace += 1

            if space["spaces"]:
                space_file["spaces"] = []
                nspace_med = _get_space(space_file, space["spaces"])
                nspace += nspace_med

            write_space["spaces"].append(space_file)

        return nspace

    formatted_output = {"files": []}

    files_nspace = []

    for data in data_list["files"]:
        metrics = data["metrics"]
        per_file = {
            "filename": data["name"],
            "SLOC": int(metrics["loc"]["sloc"]),
            "PLOC": int(metrics["loc"]["ploc"]),
            "LLOC": int(metrics["loc"]["lloc"]),
            "CLOC": int(metrics["loc"]["cloc"]),
            "BLANK": int(metrics["loc"]["blank"]),
            "CC": _get_cc(metrics),
            "COGNITIVE": _get_cognitive(metrics),
            "NARGS": _get_nargs(metrics),
            "NEXITS": _get_nexits(metrics),
            "NOM": _get_nom(metrics),
            "Halstead": _get_halstead(metrics),
            "Mi": _get_mi(metrics),
            "spaces": [],
        }

        nspace = _get_space(per_file, data["spaces"])
        files_nspace.append(nspace)

        formatted_output["files"].append(per_file)

    return (formatted_output, files_nspace)


def helper_test_rust_code_analysis(
    standardized_output: dict, files_nspace: T.List
):

    tot_sloc = 0
    tot_ploc = 0
    tot_lloc = 0
    tot_cloc = 0
    tot_blank = 0
    tot_cc = 0
    tot_cc_avg = 0
    tot_cognitive = 0
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
        mi_original = (
            171.0
            - 5.2 * math.log(halstead_volume)
            - 0.23 * cc
            - 16.2 * math.log(sloc)
        )
        return {
            "Original": mi_original,
            "Sei": 171.0
            - 5.2 * math.log2(halstead_volume)
            - 0.23 * cc
            - 16.2 * math.log2(sloc)
            + 50.0 * math.sin(math.sqrt(comments_percentage * 2.4)),
            "Visual Studio": max((mi_original * 100.0 / 171.0), 0.0),
        }

    def _global_nom():
        return {
            "functions": tot_functions,
            "closures": tot_closures,
            "total": tot_functions_and_closures,
        }

    for file, cc_file in zip(standardized_output["files"], files_nspace):
        tot_sloc += file["SLOC"]
        tot_ploc += file["PLOC"]
        tot_lloc += file["LLOC"]
        tot_cloc += file["CLOC"]
        tot_blank += file["BLANK"]
        tot_cc += file["CC"]["sum"]
        tot_cc_avg += file["CC"]["average"] * (cc_file + 1)
        tot_cognitive += file["COGNITIVE"]["sum"]
        tot_halstead_n1 += file["Halstead"]["n1"]
        tot_halstead_n2 += file["Halstead"]["n2"]
        tot_halstead_N1 += file["Halstead"]["N1"]
        tot_halstead_N2 += file["Halstead"]["N2"]
        tot_functions += file["NOM"]["functions"]
        tot_closures += file["NOM"]["closures"]
        tot_functions_and_closures += file["NOM"]["total"]
        tot_nexits += file["NEXITS"]["sum"]
        tot_nargs += file["NARGS"]["sum"]

    output = {}

    nom = _global_nom()

    output["SLOC"] = tot_sloc
    output["PLOC"] = tot_ploc
    output["LLOC"] = tot_lloc
    output["CLOC"] = tot_cloc
    output["BLANK"] = tot_blank
    output["CC_SUM"] = tot_cc
    output["CC_AVG"] = tot_cc_avg / (sum(files_nspace) + len(files_nspace))
    output["COGNITIVE_SUM"] = tot_cognitive
    output["COGNITIVE_AVG"] = tot_cognitive / max(1, nom["total"])
    output["NARGS_SUM"] = tot_nargs
    output["NARGS_AVG"] = tot_nargs / max(1, nom["total"])
    output["NEXITS"] = tot_nexits
    output["NEXITS_AVG"] = tot_nexits / max(1, nom["total"])
    output["NOM"] = nom
    output["HALSTEAD"] = _global_halstead()
    output["MI"] = _global_mi(
        output["SLOC"],
        output["CLOC"],
        output["CC_SUM"],
        output["HALSTEAD"]["Length"],
        output["HALSTEAD"]["Volume"],
        output["HALSTEAD"]["Vocabulary"],
    )

    output["files"] = []

    for file in standardized_output["files"]:
        file_metrics = {
            "filename": file["filename"],
            "SLOC": file["SLOC"],
            "PLOC": file["PLOC"],
            "LLOC": file["LLOC"],
            "CLOC": file["CLOC"],
            "BLANK": file["BLANK"],
            "CC_SUM": file["CC"]["sum"],
            "CC_AVG": file["CC"]["average"],
            "COGNITIVE_SUM": file["COGNITIVE"]["sum"],
            "COGNITIVE_AVG": file["COGNITIVE"]["average"],
            "NARGS_SUM": file["NARGS"]["sum"],
            "NARGS_AVG": file["NARGS"]["average"],
            "NEXITS": file["NEXITS"]["sum"],
            "NEXITS_AVG": file["NEXITS"]["average"],
            "NOM": file["NOM"],
            "Halstead": file["Halstead"],
            "Mi": file["Mi"],
            "spaces": file["spaces"],
        }
        output["files"].append(file_metrics)

    return output
