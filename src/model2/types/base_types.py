from enum import Enum
from typing import Union

class LogicalConnectives(Enum):
    AND = '∧'
    OR = '∨'
    XOR = "⊕"
    THEN = "→"     
    IFF = "↔" 

class Quantifiers(Enum):
    UNIVERSALITY = '∀'
    EXISTENCE = '∃'

variables = []

class Atom:
    def __init__(self, func: str, values: Union[list[str], str]):
        self.func = func
        if isinstance(values, str):
            self.values = [values]
        else:
            self.values = values
    
    def __str__(self):
        return f"{self.func}({', '.join(self.values)})"

class Formula:
    pass

class AtomicFormula(Formula):
    def __init__(self, atom: Atom):
        self.atom = atom
    
    def __str__(self):
        return str(self.atom)

class QuantifiedFormula(Formula):
    def __init__(self, quantifier: Quantifiers, variable: str, formula: Formula):
        self.quantifier = quantifier
        self.variable = variable
        self.formula = formula
    
    def __str__(self):
        return f"{self.quantifier.value}{self.variable}({self.formula})"

class BinaryFormula(Formula):
    def __init__(self, left: Formula, connective: LogicalConnectives, right: Formula):
        self.left = left
        self.connective = connective
        self.right = right
    
    def __str__(self):
        return f"({self.left} {self.connective.value} {self.right})"

class NegativeFormula(Formula):
    def __init__(self, formula: Formula):
        self.formula = formula
    
    def __str__(self):
        return f"¬{self.formula}"