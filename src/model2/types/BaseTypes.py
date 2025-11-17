from enum import Enum
from typing import Union


class LogicalConnectives(Enum):
    AND = '∧'
    OR = '∨'
    XOR = "⊕"
    THEN = "→"
    IFF = "↔"

    @classmethod
    def get(self, value: str):
        if value == '∧': return LogicalConnectives.AND
        if value == '∨': return LogicalConnectives.OR
        if value == "⊕": return LogicalConnectives.XOR
        if value == "→": return LogicalConnectives.THEN
        if value == "↔": return LogicalConnectives.IFF


class Quantifiers(Enum):
    UNIVERSALITY = '∀'
    EXISTENCE = '∃'

    @classmethod
    def get(self, value: str):
        if value == '∀': return Quantifiers.UNIVERSALITY
        if value == '∃': return Quantifiers.EXISTENCE


class Variables:
    def __init__(self, variables: list[str]):
        self._variables = list(variables)

    def append(self, var: str):
        self._variables.append(var)

    def __contains__(self, var: str):
        return var in self._variables

    def clear(self):
        self._variables = []
        

variables = Variables(["r", "s", "t", "u", "v", "w", "x", "y", "z"])


class Atom:
    def __init__(self, func: str, values: Union[list[str], str, list['Atom'], 'Atom', list[Union[str, 'Atom']]]):
        self.func = func

        if not isinstance(values, list):
            self.values = [values]
        else:
            self.values = values

    def get_func(self):
        return self.func

    def get_values(self):
        return self.values

    def __repr__(self):
        return f"{self.func}({', '.join(map(str, self.values))})"

    def __eq__(self, other):
        if not isinstance(other, Atom):
            return False
        return self.func == other.func and self.values == other.values


class Formula:
    pass


class AtomicFormula(Formula):
    def __init__(self, atom: Atom):
        self.atom = atom

    def __repr__(self):
        return str(self.atom)

    def __eq__(self, other):
        return self.atom == other.atom


class QuantifiedFormula(Formula):
    def __init__(self, quantifier: Quantifiers, variable: str, formula: Formula):
        self.quantifier = quantifier
        self.variable = variable
        self.formula = formula

    def __repr__(self):
        return f"{self.quantifier.value}{self.variable}({self.formula})"


class BinaryFormula(Formula):
    def __init__(self, left: Formula, connective: LogicalConnectives, right: Formula):
        self.left = left
        self.connective = connective
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.connective.value} {self.right})"

    def __eq__(self, other):
        return self.left == other.left and self.connective == other.connective and self.right == other.right


class NegativeFormula(Formula):
    def __init__(self, formula: Formula):
        self.formula = formula

    def __repr__(self):
        return f"¬{self.formula}"

    def __eq__(self, other):
        return self.formula == other.formula
