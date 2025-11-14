from ..types.base_types import *
from typing import List, Tuple

class PNFConverter:
    def __init__(self):
        self.used_variables = set()
    
    def to_pnf(self, formula: Formula) -> Formula:
        """Основной метод преобразования в ПНФ"""
        
        # 1. Удаление импликаций и эквиваленций
        formula = self.remove_implications(formula)
        
        # 2. Проталкивание отрицаний внутрь
        formula = self.push_negations(formula)
        
        # 3. Переименование переменных (избегание конфликтов)
        formula = self.rename_variables(formula)
        
        # 4. Вынесение кванторов вперед
        formula = self.extract_quantifiers(formula)
        
        return formula
    
    def remove_implications(self, formula: Formula) -> Formula:
        """Удаление → и ↔"""
        if isinstance(formula, AtomicFormula):
            return formula
        
        elif isinstance(formula, QuantifiedFormula):
            return QuantifiedFormula(
                formula.quantifier,
                formula.variable,
                self.remove_implications(formula.formula)
            )
        
        elif isinstance(formula, BinaryFormula):
            if formula.connective == LogicalConnectives.THEN:
                # p → q заменяем на ¬p ∨ q
                return BinaryFormula(
                    self.remove_implications(NegativeFormula(formula.left)),
                    LogicalConnectives.OR,
                    self.remove_implications(formula.right)
                )
            elif formula.connective == LogicalConnectives.IFF:
                # p ↔ q заменяем на (¬p ∨ q) ∧ (¬q ∨ p)
                left_impl = BinaryFormula(
                    self.remove_implications(NegativeFormula(formula.left)),
                    LogicalConnectives.OR,
                    self.remove_implications(formula.right)
                )
                right_impl = BinaryFormula(
                    self.remove_implications(NegativeFormula(formula.right)),
                    LogicalConnectives.OR,
                    self.remove_implications(formula.left)
                )
                return BinaryFormula(left_impl, LogicalConnectives.AND, right_impl)
            elif formula.connective == LogicalConnectives.XOR:
                # p ⊕ q заменяем на (p ∨ q) ∧ (¬p ∨ ¬q)
                left_or = BinaryFormula(
                    self.remove_implications(formula.left),
                    LogicalConnectives.OR,
                    self.remove_implications(formula.right)
                )
                right_and = BinaryFormula(
                    self.remove_implications(NegativeFormula(formula.left)),
                    LogicalConnectives.OR,
                    self.remove_implications(NegativeFormula(formula.right))
                )
                return BinaryFormula(left_or, LogicalConnectives.AND, right_and)
            else:
                return BinaryFormula(
                    self.remove_implications(formula.left),
                    formula.connective,
                    self.remove_implications(formula.right)
                )

        elif isinstance(formula, NegativeFormula):
            return NegativeFormula(self.remove_implications(formula.formula))
        
        return formula
    
    def push_negations(self, formula: Formula) -> Formula:
        """Проталкивание отрицаний внутрь"""
        if isinstance(formula, NegativeFormula):
            inner = formula.formula
            
            if isinstance(inner, NegativeFormula):
                # ¬¬p → p
                return self.push_negations(inner.formula)
            
            elif isinstance(inner, BinaryFormula):
                if inner.connective == LogicalConnectives.AND:
                    # ¬(p ∧ q) → ¬p ∨ ¬q
                    return BinaryFormula(
                        self.push_negations(NegativeFormula(inner.left)),
                        LogicalConnectives.OR,
                        self.push_negations(NegativeFormula(inner.right))
                    )
                elif inner.connective == LogicalConnectives.OR:
                    # ¬(p ∨ q) → ¬p ∧ ¬q
                    return BinaryFormula(
                        self.push_negations(NegativeFormula(inner.left)),
                        LogicalConnectives.AND,
                        self.push_negations(NegativeFormula(inner.right))
                    )
            
            elif isinstance(inner, QuantifiedFormula):
                if inner.quantifier == Quantifiers.UNIVERSALITY:
                    # ¬∀x p → ∃x ¬p
                    return QuantifiedFormula(
                        Quantifiers.EXISTENCE,
                        inner.variable,
                        self.push_negations(NegativeFormula(inner.formula))
                    )
                elif inner.quantifier == Quantifiers.EXISTENCE:
                    # ¬∃x p → ∀x ¬p
                    return QuantifiedFormula(
                        Quantifiers.UNIVERSALITY,
                        inner.variable,
                        self.push_negations(NegativeFormula(inner.formula))
                    )
            
            return NegativeFormula(self.push_negations(inner))
        
        elif isinstance(formula, BinaryFormula):
            return BinaryFormula(
                self.push_negations(formula.left),
                formula.connective,
                self.push_negations(formula.right)
            )
        
        elif isinstance(formula, QuantifiedFormula):
            return QuantifiedFormula(
                formula.quantifier,
                formula.variable,
                self.push_negations(formula.formula)
            )
        
        return formula
    
    def rename_variables(self, formula: Formula, mapping=None) -> Formula:
        """Переименование переменных для избежания конфликтов"""
        if mapping is None:
            mapping = {}
        
        if isinstance(formula, AtomicFormula):
            new_values = [mapping.get(arg, arg) for arg in formula.atom.values]
            return AtomicFormula(Atom(formula.atom.func, new_values))
        
        elif isinstance(formula, QuantifiedFormula):
            old_var = formula.variable
            new_var = self.generate_new_variable(old_var)
            mapping[old_var] = new_var
            
            new_formula = self.rename_variables(formula.formula, mapping.copy())
            return QuantifiedFormula(formula.quantifier, new_var, new_formula)
        
        elif isinstance(formula, BinaryFormula):
            return BinaryFormula(
                self.rename_variables(formula.left, mapping.copy()),
                formula.connective,
                self.rename_variables(formula.right, mapping.copy())
            )
        
        elif isinstance(formula, NegativeFormula):
            return NegativeFormula(self.rename_variables(formula.formula, mapping.copy()))
        
        return formula
    
    def generate_new_variable(self, base: str) -> str:
        """Генерация новой уникальной переменной"""
        counter = 1
        new_var = f"{base}_{counter}"
        while new_var in self.used_variables:
            counter += 1
            new_var = f"{base}_{counter}"
        self.used_variables.add(new_var)
        return new_var
    
    def extract_quantifiers(self, formula: Formula, prefix=None) -> Formula:
        """Вынесение кванторов в начало"""
        if prefix is None:
            prefix = []
        
        if isinstance(formula, QuantifiedFormula):
            prefix.append((formula.quantifier, formula.variable))
            return self.extract_quantifiers(formula.formula, prefix)
        
        elif isinstance(formula, BinaryFormula):
            left_result = self.extract_quantifiers(formula.left, [])
            right_result = self.extract_quantifiers(formula.right, [])
            
            # Объединяем кванторы из обеих частей
            left_quantifiers = self.get_quantifiers(left_result)
            right_quantifiers = self.get_quantifiers(right_result)
            
            # Создаем формулу с кванторами в начале
            result = self.wrap_with_quantifiers(
                BinaryFormula(
                    self.remove_quantifiers(left_result),
                    formula.connective,
                    self.remove_quantifiers(right_result)
                ),
                prefix + left_quantifiers + right_quantifiers
            )
            
            return result
        
        else:
            return self.wrap_with_quantifiers(formula, prefix)
    
    def get_quantifiers(self, formula: Formula) -> List[Tuple[Quantifiers, str]]:
        """Извлечение кванторов из формулы"""
        if isinstance(formula, QuantifiedFormula):
            return [(formula.quantifier, formula.variable)] + self.get_quantifiers(formula.formula)
        return []
    
    def remove_quantifiers(self, formula: Formula) -> Formula:
        """Удаление кванторов из формулы (оставляет матрицу)"""
        if isinstance(formula, QuantifiedFormula):
            return self.remove_quantifiers(formula.formula)
        return formula
    
    def wrap_with_quantifiers(self, formula: Formula, quantifiers: List[Tuple[Quantifiers, str]]) -> Formula:
        """Обертывание формулы кванторами"""
        result = formula
        for quantifier, variable in reversed(quantifiers):
            result = QuantifiedFormula(quantifier, variable, result)
        return result