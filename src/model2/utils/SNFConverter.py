from ..types.BaseTypes import *
from typing import List, Tuple

class SNFConverter:
    def __init__(self):
        self.skolem_counter = 0
        self.quantifiers = []  # стек кванторов для сколемизации
    
    def to_skolem(self, formula: Formula) -> Formula:
        """Удаляет кванторы существования через сколемизацию"""
        if isinstance(formula, QuantifiedFormula):
            if formula.quantifier == Quantifiers.UNIVERSALITY:
                # Для ∀ добавляем переменную в контекст и продолжаем
                self.quantifiers.append(formula.variable)
                result = self.to_skolem(formula.formula)
                self.quantifiers.pop()
                return result
            
            elif formula.quantifier == Quantifiers.EXISTENCE:
                # Для ∃ заменяем на сколемовскую константу/функцию
                skolem_term = self.create_skolem_term()
                return self.substitute_variable(formula.formula, formula.variable, skolem_term)
            else:
                return formula
        
        elif isinstance(formula, BinaryFormula):
            return BinaryFormula(
                self.to_skolem(formula.left),
                formula.connective,
                self.to_skolem(formula.right)
            )
        
        elif isinstance(formula, NegativeFormula):
            return NegativeFormula(self.to_skolem(formula.formula))
        
        else:
            return formula
    
    def remove_universal_quantifiers(self, formula: Formula) -> Formula:
        """Удаляет все кванторы всеобщности из формулы"""
        if isinstance(formula, QuantifiedFormula):
            if formula.quantifier == Quantifiers.UNIVERSALITY:
                # Просто убираем квантор и продолжаем рекурсивно
                return self.remove_universal_quantifiers(formula.formula)
            else:
                # Для ∃ тоже убираем (после сколемизации их не должно остаться)
                return self.remove_universal_quantifiers(formula.formula)
        
        elif isinstance(formula, BinaryFormula):
            return BinaryFormula(
                self.remove_universal_quantifiers(formula.left),
                formula.connective,
                self.remove_universal_quantifiers(formula.right)
            )
        
        elif isinstance(formula, NegativeFormula):
            return NegativeFormula(self.remove_universal_quantifiers(formula.formula))
        
        else:
            return formula
    
    def create_skolem_term(self) -> str:
        """Создает сколемовский терм"""
        self.skolem_counter += 1
        if self.quantifiers:
            # Если есть универсальные кванторы, создаем функцию f(x, y, ...)
            args = "_".join(self.quantifiers)
            return f"f{self.skolem_counter}({args})"
        else:
            # Иначе создаем константу
            return f"c{self.skolem_counter}"
    
    def substitute_variable(self, formula: Formula, variable: str, replacement: str) -> Formula:
        """Заменяет переменную в формуле"""
        if isinstance(formula, AtomicFormula):
            new_values = [replacement if arg == variable else arg for arg in formula.atom.values]
            return AtomicFormula(Atom(formula.atom.func, new_values))
        
        elif isinstance(formula, BinaryFormula):
            return BinaryFormula(
                self.substitute_variable(formula.left, variable, replacement),
                formula.connective,
                self.substitute_variable(formula.right, variable, replacement)
            )
        
        elif isinstance(formula, NegativeFormula):
            return NegativeFormula(self.substitute_variable(formula.formula, variable, replacement))
        
        elif isinstance(formula, QuantifiedFormula):
            # Не подставляем в связанные переменные с тем же именем
            if formula.variable == variable:
                return formula
            else:
                return QuantifiedFormula(
                    formula.quantifier,
                    formula.variable,
                    self.substitute_variable(formula.formula, variable, replacement)
                )
        
        else:
            return formula