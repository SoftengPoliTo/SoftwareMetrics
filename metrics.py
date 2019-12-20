import math


def __halstead(operators: dict, operands: dict) -> dict:
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

    halstead = {
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

    return halstead
