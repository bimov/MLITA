from model2.types.base_types import *
from model2.utils.PNFConverter import PNFConverter
from model2.utils.SNFConverter import SNFConverter
from model2.utils.CNFConverter import CNFConverter
from typing import List, Tuple


class FullConverter:
    def __init__(self):
        self.pnf_converter = PNFConverter()
        self.skolem_converter = SNFConverter()
        self.cnf_converter = CNFConverter()
    
    def to_clauses(self, formula: Formula) -> List[Formula]:
        """Полное преобразование в множество дизъюнктов"""
        # 1. ПНФ
        pnf = self.pnf_converter.to_pnf(formula)
        print("После ПНФ:", pnf)
        
        # 2. Сколемизация
        skolemized = self.skolem_converter.to_skolem(pnf)
        print("После сколемизации:", skolemized)
        
        # 3. Удаление кванторов всеобщности
        no_quantifiers = self.skolem_converter.remove_universal_quantifiers(skolemized)
        print("После удаления кванторов:", no_quantifiers)
        
        # 4. КНФ
        cnf = self.cnf_converter.to_cnf(no_quantifiers)
        print("После КНФ:", cnf)
        
        # 5. Разбиение на дизъюнкты
        return self.split_into_clauses(cnf)
    
    def split_into_clauses(self, formula: Formula) -> List[Formula]:
        """Разбивает КНФ на список дизъюнктов"""
        clauses = []
        
        if isinstance(formula, BinaryFormula) and formula.connective == LogicalConnectives.AND:
            clauses.extend(self.split_into_clauses(formula.left))
            clauses.extend(self.split_into_clauses(formula.right))
        else:
            clauses.append(formula)
        
        return clauses