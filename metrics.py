import math
"""These functions are meant to further enrich the data obtained using the third-party tools.
 They can be used to extend the already present metrics, or to calculate some other metrics."""


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

    standardized_output["Halstead"] = _helper_halstead(all_operators, all_operands)


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


def helper_tokei(standardized_output: dict):
    tot_loc = 0
    tot_cloc = 0
    tot_lines = 0

    for file in standardized_output["files"]:
        tot_loc += file["LOC"]
        tot_cloc += file["CLOC"]
        tot_lines += file["Lines"]

    standardized_output["LOC"] = tot_loc
    standardized_output["CLOC"] = tot_cloc
    standardized_output["Lines"] = tot_lines


# def helper_cccc(standardized_output: dict):
#     """Calculate McCabe's Weighted Method Count metric"""
#     for file in standardized_output["files"]:
#         WMC = 0
#         for func in file["functions"]:
#             WMC += func["CC"]
