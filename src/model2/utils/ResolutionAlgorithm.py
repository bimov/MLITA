from ..types.BaseTypes import *
from .Unificator import Unificator
from .FullConverter import FullConverter
from typing import List, Set, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class ResolutionAlgorithm:
    def __init__(self):
        """Инициализация алгоритма резолюции"""
        self.full_converter = FullConverter()
        self.unification = Unificator()
    
    def resolve(self, clauses: List[Formula], goal: Formula) -> bool:
        """
        Алгоритм резолюции для доказательства формулы.
        """
        logger.info("=" * 60)
        logger.info("НАЧАЛО АЛГОРИТМА РЕЗОЛЮЦИИ")
        logger.info("=" * 60)
        
        # Отрицаем целевую формулу
        negated_goal = NegativeFormula(goal)
        logger.info(f"\nЦелевая формула: {goal}")
        logger.info(f"Отрицание целевой формулы: {negated_goal}")
        
        # Преобразуем отрицание в клаузы
        logger.info("Преобразование отрицания цели в ПНФ -> СНФ -> КНФ и разбиение на клаузы...")
        try:
            goal_clauses = self.full_converter.to_clauses(negated_goal)
            logger.info(f"Клаузы из отрицания цели: {goal_clauses}")
        except Exception as e:
            logger.warning(f"Ошибка при преобразовании цели в клаузы: {e}")
            goal_clauses = self._formula_to_clauses(negated_goal)
            logger.info(f"Клаузы из отрицания цели (простое разбиение): {goal_clauses}")
        
        all_clauses = []
        logger.info("Преобразование посылок в ПНФ -> СНФ -> КНФ и разбиение на клаузы...")
        for clause in clauses:
            all_clauses.extend(self.full_converter.to_clauses(clause))
        
        # Объединяем все клаузы
        all_clauses += goal_clauses
        logger.info(f"\nВсего клауз в начале: {len(all_clauses)}")
        for i, clause in enumerate(all_clauses, 1):
            logger.info(f"  Клауза {i}: {clause}")
        
        # Используем список вместо множества для хранения уникальных клауз
        clause_strings = set()
        unique_clauses = []
        
        for clause in all_clauses:
            clause_str = self._clause_to_string(clause)
            if clause_str not in clause_strings:
                clause_strings.add(clause_str)
                unique_clauses.append(clause)
        
        all_clauses = unique_clauses
        
        # Множество уже проверенных пар клауз
        checked_pairs: Set[Tuple[str, str]] = set()
        
        iteration = 0
        max_iterations = 100
        
        logger.info("\n" + "=" * 60)
        logger.info("НАЧАЛО ИТЕРАЦИЙ РЕЗОЛЮЦИИ")
        logger.info("=" * 60)
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"\n--- Итерация {iteration} ---")
            logger.info(f"Текущее количество клауз: {len(all_clauses)}")
            new_clauses = []
            
            for i in range(len(all_clauses)):
                for j in range(i + 1, len(all_clauses)):
                    clause1 = all_clauses[i]
                    clause2 = all_clauses[j]
                    
                    key1 = self._clause_to_string(clause1)
                    key2 = self._clause_to_string(clause2)
                    pair_key = (key1, key2) if key1 < key2 else (key2, key1)
                    
                    if pair_key in checked_pairs:
                        continue
                    
                    checked_pairs.add(pair_key)
                    
                    logger.info(f"\nПопытка резолюции клауз:")
                    logger.info(f"  Клауза 1: {clause1}")
                    logger.info(f"  Клауза 2: {clause2}")
                    
                    # Извлекаем литералы из обеих клауз
                    literals1 = self._extract_literals(clause1) 
                    literals2 = self._extract_literals(clause2)
                    
                    logger.info(f"  Литералы клаузы 1: {[str(l) for l in literals1]}")
                    logger.info(f"  Литералы клаузы 2: {[str(l) for l in literals2]}")
                    
                    # Ищем комплементарные пары с подстановками
                    result = self._find_resolvents(literals1, literals2)
                    
                    if result:
                        resolvent_literals, substitution = result 
                        try:
                            new_clause = self._literals_to_clause(resolvent_literals)
                            new_clause_str = self._clause_to_string(new_clause)
                            if new_clause_str not in clause_strings:
                                clause_strings.add(new_clause_str)
                                new_clauses.append(new_clause)
                                if substitution:
                                    logger.info(f"  ✓ Новая резольвента: {new_clause} (подстановка: {substitution})")
                                else:
                                    logger.info(f"  ✓ Новая резольвента: {new_clause}")
                            else:
                                logger.info(f"  ✗ Резольвента уже существует: {new_clause}")
                        except Exception as e:
                            error_message = str(e)
                            if error_message == "TAUTOLOGY":
                                continue
                            elif error_message == "EMPTY CLAUSE":
                                # Пустая клауза - противоречие найдено!
                                if substitution:
                                    logger.info(f"  Подстановка: {substitution}")
                                logger.info("\n" + "!" * 60)
                                logger.info("НАЙДЕНА ПУСТАЯ КЛАУЗА - ПРОТИВОРЕЧИЕ!")
                                logger.info("ФОРМУЛА ДОКАЗАНА!")
                                logger.info("!" * 60)
                                return True
                    else:
                        logger.info(f"  ✗ Комплементарных пар не найдено")
            
            # Добавляем новые клаузы к основному списку
            if len(new_clauses) > 0:
                all_clauses.extend(new_clauses)
                logger.info(f"\nДобавлено новых клауз: {len(new_clauses)}")
            else:
                logger.info(f"\nНовых резольвент не найдено на итерации {iteration}")
                logger.info("Алгоритм завершается")
                break
        
        logger.info("\n" + "=" * 60)
        logger.info("ЗАВЕРШЕНИЕ АЛГОРИТМА РЕЗОЛЮЦИИ")
        logger.info("=" * 60)
        logger.info(f"Всего итераций: {iteration}")
        logger.info(f"Всего клауз: {len(all_clauses)}")
        logger.info("ФОРМУЛА НЕ ДОКАЗАНА")
        logger.info("=" * 60)
        return False
    
    def _find_resolvents(self, literals1: List[Formula], literals2: List[Formula]) -> Optional[Tuple[List[Formula], Dict[str, str]]]:
        """
        Находит все возможные резольвенты между двумя списками литералов.
        Использует алгоритм унификации.
        """
        resolvents = []
        
        for i, lit1 in enumerate(literals1):
            for j, lit2 in enumerate(literals2):
                # Проверяем, являются ли литералы комплементарными с унификацией
                substitution = self._are_complementary_with_unification(lit1, lit2)
                if substitution is not None:
                    logger.info(f"  Найдена комплементарная пара: {lit1} и {lit2}")
                    logger.info(f"  Подстановка: {substitution}")
                    
                    # Создаем резольвенту без этих двух литералов
                    new_literals1 = [l for k, l in enumerate(literals1) if k != i]
                    new_literals2 = [l for k, l in enumerate(literals2) if k != j]
                    
                    # Объединяем оставшиеся литералы
                    combined_literals = new_literals1 + new_literals2
                    
                    # Применяем подстановку ко всем литералам
                    if substitution:
                        substituted_literals = []
                        for lit in combined_literals:
                            substituted_lit = self._apply_substitution(lit, substitution)
                            substituted_literals.append(substituted_lit)
                        combined_literals = substituted_literals
                    
                    # Удаляем дубликаты
                    unique_literals = []
                    seen = set()
                    for lit in combined_literals:
                        lit_str = self._literal_to_string(lit)
                        if lit_str not in seen:
                            seen.add(lit_str)
                            unique_literals.append(lit)
                    return unique_literals, substitution # достаточно найти одну резольвенту
        return None
    
    def _are_complementary_with_unification(self, lit1: Formula, lit2: Formula) -> Optional[Dict[str, str]]:
        """
        Проверяет, являются ли два литерала комплементарными с использованием унификации.
        """
        # Случай 1: lit1 - отрицание, lit2 - атом
        if isinstance(lit1, NegativeFormula) and isinstance(lit2, AtomicFormula):
            if isinstance(lit1.formula, AtomicFormula):
                result = self.unification.unify_atoms(lit1.formula.atom, lit2.atom)
                if result is None:
                    return None
                _, _, substitution = result
                return substitution
        
        # Случай 2: lit1 - атом, lit2 - отрицание
        if isinstance(lit1, AtomicFormula) and isinstance(lit2, NegativeFormula):
            if isinstance(lit2.formula, AtomicFormula):
                result = self.unification.unify_atoms(lit1.atom, lit2.formula.atom)
                if result is None:
                    return None
                _, _, substitution = result
                return substitution
        
        return None
    
    def _apply_substitution(self, formula: Formula, substitution: Dict[str, str]) -> Formula:
        """
        Применяет подстановку к формуле.
        """
        if not substitution:
            return formula
        
        if isinstance(formula, AtomicFormula):
            # Применяем подстановку к атому через алгоритм унификации
            new_atom = self.unification._apply_substitution_to_atom(formula.atom, substitution)
            return AtomicFormula(new_atom)
        
        elif isinstance(formula, NegativeFormula):
            return NegativeFormula(self._apply_substitution(formula.formula, substitution))
        
        elif isinstance(formula, BinaryFormula): # такого случая не бывает
            return BinaryFormula(
                self._apply_substitution(formula.left, substitution),
                formula.connective,
                self._apply_substitution(formula.right, substitution)
            )
        
        else: # такого случая тоже нет
            return formula

    def _formula_to_clauses(self, formula: Formula) -> List[Formula]:
        """Преобразует формулу в список клауз (простое разбиение по AND)."""
        clauses = []
        
        if isinstance(formula, BinaryFormula) and formula.connective == LogicalConnectives.AND:
            clauses.extend(self._formula_to_clauses(formula.left))
            clauses.extend(self._formula_to_clauses(formula.right))
        else:
            clauses.append(formula)
        
        return clauses
    
    def _extract_literals(self, clause: Formula) -> List[Formula]:
        """
        Извлекает все литералы из клаузы.
        Литерал - это атом или отрицание атома.
        """
        literals = []
        
        if isinstance(clause, AtomicFormula):
            literals.append(clause)
        elif isinstance(clause, NegativeFormula):
            if isinstance(clause.formula, AtomicFormula):
                literals.append(clause)
            else:
                literals.extend(self._extract_literals(clause.formula))
        elif isinstance(clause, BinaryFormula):
            if clause.connective == LogicalConnectives.OR:
                literals.extend(self._extract_literals(clause.left))
                literals.extend(self._extract_literals(clause.right))
            else:
                literals.append(clause)
        else:
            literals.append(clause)
        return literals
    
    def _literals_to_clause(self, literals: List[Formula]):
        """
        Преобразует список литералов в клаузу (дизъюнкцию).
        Если список пуст, возвращает None (пустая клауза).
        Если один литерал, возвращает его.
        Иначе создает дизъюнкцию.
        """
        if not literals:
            raise Exception("EMPTY CLAUSE")
        
        if len(literals) == 1:
            return literals[0]
        
        # Проверка на тавтологию (наличие P и ¬P после унификации)
        for i in range(len(literals)):
            lit1 = literals[i]
            for j in range(i + 1, len(literals)):
                lit2 = literals[j]
                if self._are_complementary_with_unification(lit1, lit2):
                    logger.info(f"  Обнаружена тавтология: {lit1} и {lit2} комплементарны")
                    raise Exception("TAUTOLOGY")
        
        unique_literals = []
        seen = set()
        for lit in literals:
            lit_str = self._literal_to_string(lit)
            if lit_str not in seen:
                seen.add(lit_str)
                unique_literals.append(lit)
        
        if len(unique_literals) == 1:
            return unique_literals[0]
        
        # Создаем дизъюнкцию
        result = unique_literals[0]
        for i in range(1, len(unique_literals)):
            result = BinaryFormula(result, LogicalConnectives.OR, unique_literals[i])
        
        return result
    
    def _clause_to_string(self, clause: Formula) -> str:
        """Преобразует клаузу в строку для сравнения"""
        return str(clause)
    
    def _literal_to_string(self, literal: Formula) -> str:
        """Преобразует литерал в строку для сравнения"""
        return str(literal)