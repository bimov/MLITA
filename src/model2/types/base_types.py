from enum import Enum
from typing import Union

class LogicalConnectives(Enum):
    CONJUNCTION = '∧'
    DISJUNCTION = '∨'
    IMPLICATION = '→'

class Quantifiers(Enum):
    UNIVERSALITY = '∀'
    EXISTENCE = '∃'

variables = []


class Atom:
    def __init__(self, func: str, values: Union[list[str], str]):
        self.func = func
        if type(values) is type(str) :
            self.values = [values]
        else:
            self.values = values


class Formula:
    pass


class AtomicFormula(Formula):
    def __init__(self, atom: Atom):
        self.atom = atom


class QuantifiedFormula(Formula):
    def __init__(self, quantifiers: Quantifiers, variable: str, formula: AtomicFormula):
        self.quantifiers = quantifiers
        self.variable = variable
        self.formula = formula


class BinaryFormula(Formula):
    def __init__(self, left: Formula, connective: LogicalConnectives, right: Formula):
        self.left = left
        self.connective = connective
        self.right = right


class NegativeFormula(Formula):
    def __init__(self, formula: Formula):
        self.formula = formula

