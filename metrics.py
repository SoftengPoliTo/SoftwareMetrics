import math


"""
These functions further enrich data obtained using third-party tools.
They can be used to extend the already present metrics, or
calculate some other metrics.
"""


def helper_halstead(standardized_output: dict, output: dict):
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

    output["Halstead"] = _helper_halstead(all_operators, all_operands)

    output["files"] = standardized_output["files"]


def _helper_halstead(operators: dict, operands: dict) -> dict:
    N1 = len(operators)
    N2 = len(operands)
    n1 = 0
    n2 = 0

    for i in operators:
        n1 += operators[i]

    for i in operands:
        n2 += operands[i]

    program_length = N1 + N2
    program_vocabulary = n1 + n2
    estimated_length = n1 * math.log2(n1) + n2 * math.log2(n2)
    purity_ratio = estimated_length / program_length
    volume = program_length * math.log2(program_vocabulary)
    difficulty = (n1 / 2) * (N2 / n2)
    program_effort = volume * difficulty
    programming_time = program_effort / 18

    halstead_output = {
        "_Operators": operators,
        "_Operands": operands,
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


def helper_tokei(standardized_output: dict, output: dict):
    tot_sloc = 0
    tot_loc = 0
    tot_lloc = 0
    tot_cloc = 0

    for file in standardized_output["files"]:
        tot_sloc += file["SLOC"]
        tot_loc += file["LOC"]
        tot_lloc += file["LLOC"]
        tot_cloc += file["CLOC"]

    output["SLOC"] = tot_sloc
    output["LOC"] = tot_loc
    output["LLOC"] = tot_lloc
    output["CLOC"] = tot_cloc

    output["files"] = standardized_output["files"]


def helper_rust_code_analysis(standardized_output: dict, output: dict):
    tot_sloc = 0
    tot_lloc = 0

    for file in standardized_output["files"]:
        tot_sloc += file["SLOC"]
        tot_lloc += file["LLOC"]

    output["SLOC"] = tot_sloc
    output["LLOC"] = tot_lloc

    output["files"] = standardized_output["files"]


def helper_cccc(standardized_output: dict, output: dict):
    """Calculate McCabe's Weighted Method Count metric.
    This version uses the McCabe's CC for calculating the weight of
    each method."""

    output["classes"] = standardized_output["classes"]
    output["files"] = standardized_output["files"]

    for module in output["classes"]:
        WMC = 0
        n_func = 0
        module_name = module["class name"]
        for file in output["files"]:
            for func in file["functions"]:
                if "class name" in func and func["class name"] == module_name:
                    WMC += func["CC"]
                    n_func += 1
        module["WMC"] = WMC
        module["no. functions"] = n_func
