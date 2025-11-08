from model2.types.base_types import *
from typing import List, Tuple

class CNFConverter:
    def __init__(self):
        pass
    
    def to_cnf(self, formula: Formula) -> Formula:
        """Преобразует матрицу формулы в КНФ (без кванторов)"""
        if isinstance(formula, QuantifiedFormula):
            # Для кванторных формул преобразуем только внутреннюю часть
            return QuantifiedFormula(
                formula.quantifier,
                formula.variable,
                self.to_cnf(formula.formula)
            )
        
        elif isinstance(formula, BinaryFormula):
            if formula.connective == LogicalConnectives.AND:
                # Рекурсивно применяем к обеим частям конъюнкции
                return BinaryFormula(
                    self.to_cnf(formula.left),
                    LogicalConnectives.AND,
                    self.to_cnf(formula.right)
                )
            
            elif formula.connective == LogicalConnectives.OR:
                # Применяем дистрибутивность: A ∨ (B ∧ C) → (A ∨ B) ∧ (A ∨ C)
                left_cnf = self.to_cnf(formula.left)
                right_cnf = self.to_cnf(formula.right)
                
                # Если правая часть - конъюнкция
                if isinstance(right_cnf, BinaryFormula) and right_cnf.connective == LogicalConnectives.AND:
                    return BinaryFormula(
                        self.to_cnf(BinaryFormula(left_cnf, LogicalConnectives.OR, right_cnf.left)),
                        LogicalConnectives.AND,
                        self.to_cnf(BinaryFormula(left_cnf, LogicalConnectives.OR, right_cnf.right))
                    )
                
                # Если левая часть - конъюнкция  
                elif isinstance(left_cnf, BinaryFormula) and left_cnf.connective == LogicalConnectives.AND:
                    return BinaryFormula(
                        self.to_cnf(BinaryFormula(left_cnf.left, LogicalConnectives.OR, right_cnf)),
                        LogicalConnectives.AND,
                        self.to_cnf(BinaryFormula(left_cnf.right, LogicalConnectives.OR, right_cnf))
                    )
                
                # Иначе просто возвращаем дизъюнкцию
                else:
                    return BinaryFormula(left_cnf, LogicalConnectives.OR, right_cnf)
            
            else:
                return formula
        
        elif isinstance(formula, NegativeFormula):
            # Для отрицания рекурсивно применяем к внутренней формуле
            return NegativeFormula(self.to_cnf(formula.formula))
        
        else:
            # AtomicFormula и другие - возвращаем как есть
            return formula