import json
import math
import os
import subprocess

from exit_codes import ExitCode, log_err

HALSTEAD_EXCEPTIONS = ["c", "cc", "cpp", "c++"]


class Halstead:
    def __init__(self, path):
        self.halstead_path = os.path.join(
            path, "Halstead_Metrics_Tool", "Halstead-Metrics.jar"
        )

    def run_n_parse_halstead(self, files_list: list, output_dir: os.path):
        results = []
        for file in files_list:
            results.append(self._run_n_parse_halstead(file, output_dir))
        return results

    def _run_n_parse_halstead(self, file: os.path, output_dir: str):
        hm_tool_res = self.run_tool_halstead(file)
        return json.loads(hm_tool_res)

    def run_tool_halstead(self, path_to_analyze: str):
        try:
            results = subprocess.run(
                [
                    "/usr/bin/java",
                    "-Duser.country=US",
                    "-Duser.language=en",
                    "-jar",
                    self.halstead_path,
                    path_to_analyze,
                ],
                capture_output=True,
                check=True,
            )
            return results.stdout

        except subprocess.CalledProcessError as ex:
            log_err(
                "\tHalstead Metric Tool exited with an error.\n{}\n{}\n",
                ExitCode.HALSTEAD_TOOL_ERR,
                ex.stdout,
                ex.stderr,
            )


def standardizer_halstead(data):

    formatted_output = {"files": []}

    for d in data:
        h = d["Halstead"]
        per_file = {
            "_Operators": h["_Operators"],
            "_Operands": h["_Operands"],
            "n1": h["n1"],
            "n2": h["n2"],
            "N1": h["N1"],
            "N2": h["N2"],
            "Vocabulary": int(h["Vocabulary"]),
            "Length": int(h["Length"]),
            "Volume": h["Volume"],
            "Difficulty": h["Difficulty"],
            "Effort": h["Effort"],
            "Programming time": h["Programming time"],
            "Estimated program length": h["Estimated program length"],
            "Purity ratio": h["Purity ratio"],
        }
        formatted_output["files"].append(
            {
                "filename": d["filename"],
                "Halstead": per_file,
                "functions": [],  # No per_function data from this tool
            }
        )

        return formatted_output


def helper_halstead(standardized_output: dict):
    all_operators = {}
    all_operands = {}

    for file in standardized_output["files"]:
        if "Halstead" not in file:
            continue

        h = file["Halstead"]

        for i in h["_Operators"]:
            if i not in all_operators:
                all_operators[i] = int(h["_Operators"][i])
            else:
                all_operators[i] += int(h["_Operators"][i])

        for i in h["_Operands"]:
            if i not in all_operands:
                all_operands[i] = int(h["_Operands"][i])
            else:
                all_operands[i] += int(h["_Operands"][i])

    standardized_output["Halstead"] = _helper_halstead(
        all_operators, all_operands
    )


def helper_test_halstead(standardized_output: dict, output: dict):
    all_operators = {}
    all_operands = {}

    for file in standardized_output["files"]:
        if "Halstead" not in file:
            continue

        h = file["Halstead"]

        for i in h["_Operators"]:
            if i not in all_operators:
                all_operators[i] = int(h["_Operators"][i])
            else:
                all_operators[i] += int(h["_Operators"][i])

        for i in h["_Operands"]:
            if i not in all_operands:
                all_operands[i] = int(h["_Operands"][i])
            else:
                all_operands[i] += int(h["_Operands"][i])

        del file["Halstead"]["_Operators"]
        del file["Halstead"]["_Operands"]

    output["Halstead"] = _helper_halstead(all_operators, all_operands)

    output["files"] = []
    for file in standardized_output["files"]:
        files = {
            "filename": file["filename"],
            "Halstead": file["Halstead"],
            "functions": [],
        }

        output["files"].append(files)


def _helper_halstead(operators: dict, operands: dict) -> dict:
    n1 = len(operators)
    n2 = len(operands)
    N1 = 0
    N2 = 0

    for i in operators:
        N1 += operators[i]

    for i in operands:
        N2 += operands[i]

    program_length = N1 + N2
    program_vocabulary = n1 + n2
    estimated_length = n1 * math.log2(n1) + n2 * math.log2(n2)
    purity_ratio = estimated_length / program_length
    volume = program_length * math.log2(program_vocabulary)
    difficulty = (n1 / 2) * (N2 / n2)
    program_effort = volume * difficulty
    programming_time = program_effort / 18

    halstead_output = {
        "n1": n1,
        "n2": n2,
        "N1": N1,
        "N2": N2,
        "Vocabulary": program_vocabulary,
        "Length": program_length,
        "Volume": volume,
        "Difficulty": difficulty,
        "Effort": program_effort,
        "Programming time": programming_time,
        "Estimated program length": estimated_length,
        "Purity ratio": purity_ratio,
    }

    return halstead_output
