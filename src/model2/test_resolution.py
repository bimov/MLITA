import logging
import sys

# ВАЖНО: Настраиваем логирование ПЕРЕД импортом модулей, которые используют логгеры
# Устанавливаем уровень на корневом логгере и создаем обработчик для stdout
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Удаляем существующие обработчики и добавляем новый для stdout
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(message)s'))
root_logger.addHandler(handler)

from model2.types.base_types import *
from model2.utils.ResolutionAlgorithm import ResolutionAlgorithm
from model2.utils.FullConverter import FullConverter


def test_resolution_simple_contradiction():
    print("=== Тест 1: Простое противоречие ===")
    
    # Клаузы: P, ¬P
    # Цель: любая (противоречие в исходных клаузах)
    p = AtomicFormula(Atom("P", []))
    not_p = NegativeFormula(p)
    
    clauses = [p, not_p]
    goal = p  # Цель не важна, так как уже есть противоречие
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print()


def test_resolution_simple_implication():
    print("=== Тест 2: Простая импликация (Modus Ponens) ===")
    
    # Клаузы: ¬P ∨ Q, P
    # Цель: Q
    # Ожидается: True (доказано)
    
    p = AtomicFormula(Atom("P", []))
    q = AtomicFormula(Atom("Q", []))
    not_p = NegativeFormula(p)
    
    # ¬P ∨ Q
    clause1 = BinaryFormula(not_p, LogicalConnectives.OR, q)
    # P
    clause2 = p
    
    clauses = [clause1, clause2]
    goal = q
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


def test_resolution_chain():
    print("=== Тест 3: Цепочка резолюций ===")
    
    # Клаузы: P ∨ Q, ¬P ∨ R, ¬Q
    # Цель: R
    # Ожидается: True (доказано)
    
    p = AtomicFormula(Atom("P", []))
    q = AtomicFormula(Atom("Q", []))
    r = AtomicFormula(Atom("R", []))
    not_p = NegativeFormula(p)
    not_q = NegativeFormula(q)
    
    # P ∨ Q
    clause1 = BinaryFormula(p, LogicalConnectives.OR, q)
    # ¬P ∨ R
    clause2 = BinaryFormula(not_p, LogicalConnectives.OR, r)
    # ¬Q
    clause3 = not_q
    
    clauses = [clause1, clause2, clause3]
    goal = r
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


def test_resolution_false_goal():
    print("=== Тест 4: Недоказуемая цель ===")
    
    # Клаузы: P, Q
    # Цель: R
    # Ожидается: False (не доказано)
    
    p = AtomicFormula(Atom("P", []))
    q = AtomicFormula(Atom("Q", []))
    r = AtomicFormula(Atom("R", []))
    
    clauses = [p, q]
    goal = r
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: НЕ ДОКАЗАНО")
    print()


def test_resolution_complex_disjunction():
    print("=== Тест 5: Сложная дизъюнкция ===")
    
    # Клаузы: P ∨ Q ∨ R, ¬P, ¬Q
    # Цель: R
    # Ожидается: True (доказано)
    
    p = AtomicFormula(Atom("P", []))
    q = AtomicFormula(Atom("Q", []))
    r = AtomicFormula(Atom("R", []))
    not_p = NegativeFormula(p)
    not_q = NegativeFormula(q)
    
    # P ∨ Q ∨ R
    clause1 = BinaryFormula(p, LogicalConnectives.OR, 
                           BinaryFormula(q, LogicalConnectives.OR, r))
    # ¬P
    clause2 = not_p
    # ¬Q
    clause3 = not_q
    
    clauses = [clause1, clause2, clause3]
    goal = r
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


def test_resolution_modus_tollens():
    print("=== Тест 6: Modus Tollens ===")
    
    # Клаузы: ¬P ∨ Q, ¬Q
    # Цель: ¬P
    # Ожидается: True (доказано)
    
    p = AtomicFormula(Atom("P", []))
    q = AtomicFormula(Atom("Q", []))
    not_p = NegativeFormula(p)
    not_q = NegativeFormula(q)
    
    # ¬P ∨ Q
    clause1 = BinaryFormula(not_p, LogicalConnectives.OR, q)
    # ¬Q
    clause2 = not_q
    
    clauses = [clause1, clause2]
    goal = not_p
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


def test_resolution_with_converter():
    print("=== Тест 7: Резолюция с преобразованием формулы в клаузы ===")
    
    # Формула: ∀x(Человек(x) → Смертен(x))
    # Предположение: Человек(Сократ)
    # Цель: Смертен(Сократ)
    # 
    # ВАЖНО: Этот тест требует унификации для работы с переменными!
    # Без унификации алгоритм не может связать переменную x_1 с константой Сократ.
    # После реализации унификации ожидается: True (доказано)
    # Без унификации ожидается: False (не доказано)
    
    # Сначала создаем клаузы из формулы
    human_x = AtomicFormula(Atom("Человек", ["x"]))
    mortal_x = AtomicFormula(Atom("Смертен", ["x"]))
    implies = BinaryFormula(human_x, LogicalConnectives.THEN, mortal_x)
    formula = QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", implies)
    
    converter = FullConverter()
    clauses = converter.to_clauses(formula)
    
    # Добавляем факт: Человек(Сократ)
    human_socrates = AtomicFormula(Atom("Человек", ["Сократ"]))
    clauses.append(human_socrates)
    
    # Цель: Смертен(Сократ)
    mortal_socrates = AtomicFormula(Atom("Смертен", ["Сократ"]))
    goal = mortal_socrates
    
    print("Исходная формула:", formula)
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    print("\nПримечание: Этот тест требует унификации для работы с переменными.")
    print("Без унификации алгоритм не может связать переменную x_1 с константой Сократ.")
    print("После реализации унификации тест должен проходить.")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    if result:
        print(f"Ожидалось: ДОКАЗАНО (унификация реализована)")
    else:
        print(f"Ожидалось: НЕ ДОКАЗАНО (без унификации)")
        print("После реализации унификации должно быть: ДОКАЗАНО")
    print()


def test_resolution_multiple_atoms():
    print("=== Тест 8: Резолюция с несколькими атомами в клаузах ===")
    
    # Клаузы: A ∨ B, ¬A ∨ C, ¬B ∨ D, ¬C
    # Цель: D
    # Ожидается: True (доказано)
    
    a = AtomicFormula(Atom("A", []))
    b = AtomicFormula(Atom("B", []))
    c = AtomicFormula(Atom("C", []))
    d = AtomicFormula(Atom("D", []))
    not_a = NegativeFormula(a)
    not_b = NegativeFormula(b)
    not_c = NegativeFormula(c)
    
    # A ∨ B
    clause1 = BinaryFormula(a, LogicalConnectives.OR, b)
    # ¬A ∨ C
    clause2 = BinaryFormula(not_a, LogicalConnectives.OR, c)
    # ¬B ∨ D
    clause3 = BinaryFormula(not_b, LogicalConnectives.OR, d)
    # ¬C
    clause4 = not_c
    
    clauses = [clause1, clause2, clause3, clause4]
    goal = d
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


def test_resolution_goal_already_in_clauses():
    print("=== Тест 9: Цель уже есть в клаузах ===")
    
    # Клаузы: P, Q
    # Цель: P
    # Ожидается: True (доказано через противоречие)
    # 
    # Объяснение: Алгоритм резолюции работает через доказательство от противного.
    # Если мы хотим доказать P, мы отрицаем его (¬P) и добавляем к клаузам.
    # Если P уже есть в клаузах, то получаем противоречие: P и ¬P.
    # Это означает, что P действительно следует из клауз.
    
    p = AtomicFormula(Atom("P", []))
    q = AtomicFormula(Atom("Q", []))
    
    clauses = [p, q]
    goal = p
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    print("Примечание: Цель уже есть в клаузах. Алгоритм добавит ¬P и найдет противоречие.")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО (противоречие между P и ¬P)")
    print()


def test_resolution_no_resolution_possible():
    print("=== Тест 10: Невозможно доказать (нет противоречия) ===")
    
    # Клаузы: P, Q
    # Цель: R
    # Ожидается: False (не доказано)
    # 
    # Объяснение: R не следует из клауз [P, Q].
    # Алгоритм добавит ¬R, но не сможет найти противоречие,
    # так как нет связи между P, Q и R.
    
    p = AtomicFormula(Atom("P", []))
    q = AtomicFormula(Atom("Q", []))
    r = AtomicFormula(Atom("R", []))
    
    clauses = [p, q]
    goal = r
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    print("Примечание: Цель R не связана с клаузами P и Q.")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: НЕ ДОКАЗАНО (нет противоречия)")
    print()


if __name__ == "__main__":
    test_resolution_simple_contradiction()
    test_resolution_simple_implication()
    test_resolution_chain()
    test_resolution_false_goal()
    test_resolution_complex_disjunction()
    test_resolution_modus_tollens()
    test_resolution_with_converter()
    test_resolution_multiple_atoms()
    test_resolution_goal_already_in_clauses()
    test_resolution_no_resolution_possible()

