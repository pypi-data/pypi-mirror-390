import math
import re
from collections import Counter


class HalSteadAnalyzer:
    def __init__(self, operators: set):
        self.operators: set = operators

    def calculate_halstead_metrics(self, code: str):
        # Tokenize the code
        tokens = re.findall(r"\b\w+\b|[^\s\w]", code)

        # Count operators and operands
        operator_counts = Counter()
        operand_counts = Counter()

        for token in tokens:
            if token in self.operators:
                operator_counts[token] += 1
            elif re.match(r"\b\w+\b", token):
                operand_counts[token] += 1

        # Halstead metrics
        n1 = len(operator_counts)  # distinct operators
        n2 = len(operand_counts)  # distinct operands
        N1 = sum(operator_counts.values())  # total operators
        N2 = sum(operand_counts.values())  # total operands

        vocabulary = n1 + n2
        length = N1 + N2
        volume = length * math.log2(vocabulary) if vocabulary > 0 else 0
        difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
        effort = difficulty * volume

        calculated_length = 0
        if n1 > 0:
            calculated_length += n1 * math.log2(n1)
        if n2 > 0:
            calculated_length += n2 * math.log2(n2)

        bugs = (effort ** (2 / 3)) / 3000 if effort > 0 else 0
        time = effort / 18 if effort > 0 else 0

        return {
            "n1": n1,  # distinct operators
            "n2": n2,  # distinct operands
            "N1": N1,  # total operators
            "N2": N2,  # total operands
            "vocabulary": vocabulary,
            "length": length,
            "volume": volume,
            "difficulty": difficulty,
            "effort": effort,
            "calculated_length": calculated_length,
            "bugs": bugs,
            "time": time,
        }
