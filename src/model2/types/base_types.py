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


variables = []

class Atom:
    def __init__(self, func: str, values: Union[list[str], str, list['Atom'], 'Atom', list[Union[str, 'Atom']]]):
        self.func = func

        if not isinstance(values, list):
            self.values = [values]
        else:
            self.values = values

    def __repr__(self):
        if len(self.values) > 0:
            return f"{self.func}({', '.join(map(str, self.values))})"
        return f"{self.func}{', '.join(map(str, self.values))}"


class Formula:
    pass


class AtomicFormula(Formula):
    def __init__(self, atom: Atom):
        self.atom = atom
        
    def __repr__(self):
        return str(self.atom)


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


class NegativeFormula(Formula):
    def __init__(self, formula: Formula):
        self.formula = formula

    def __repr__(self):
        return f"¬{self.formula}"
    
