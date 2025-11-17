import logging
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Настройка логирования
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(message)s'))
root_logger.addHandler(handler)

from ..types.BaseTypes import *
from ..utils.ResolutionAlgorithm import ResolutionAlgorithm
from ..utils.FullConverter import FullConverter


def test_resolution_complex_predicates():
    print("=== Тест 11: Сложные предикаты с несколькими переменными ===")
    
    # Клаузы: Отец(Иван, Петр), Отец(Петр, Мария), ∀x∀y(Отец(x,y) → Предок(x,y)), 
    #         ∀x∀y∀z(Предок(x,y) ∧ Предок(y,z) → Предок(x,z))
    # Цель: Предок(Иван, Мария)
    # Ожидается: True (доказано)
    
    # Факты
    father_ivan_peter = AtomicFormula(Atom("Отец", ["Иван", "Петр"]))
    father_peter_maria = AtomicFormula(Atom("Отец", ["Петр", "Мария"]))
    
    # Правила
    # ∀x∀y(Отец(x,y) → Предок(x,y))
    father_xy = AtomicFormula(Atom("Отец", ["x", "y"]))
    ancestor_xy = AtomicFormula(Atom("Предок", ["x", "y"]))
    rule1 = BinaryFormula(father_xy, LogicalConnectives.THEN, ancestor_xy)
    quantified_rule1 = QuantifiedFormula(Quantifiers.UNIVERSALITY, "y", 
                                        QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", rule1))
    
    # ∀x∀y∀z(Предок(x,y) ∧ Предок(y,z) → Предок(x,z))
    ancestor_xy2 = AtomicFormula(Atom("Предок", ["x", "y"]))
    ancestor_yz = AtomicFormula(Atom("Предок", ["y", "z"]))
    ancestor_xz = AtomicFormula(Atom("Предок", ["x", "z"]))
    antecedent = BinaryFormula(ancestor_xy2, LogicalConnectives.AND, ancestor_yz)
    rule2 = BinaryFormula(antecedent, LogicalConnectives.THEN, ancestor_xz)
    quantified_rule2 = QuantifiedFormula(Quantifiers.UNIVERSALITY, "z",
                                        QuantifiedFormula(Quantifiers.UNIVERSALITY, "y",
                                        QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", rule2)))
    
    converter = FullConverter()
    clauses_rule1 = converter.to_clauses(quantified_rule1)
    clauses_rule2 = converter.to_clauses(quantified_rule2)
    
    clauses = [father_ivan_peter, father_peter_maria] + clauses_rule1 + clauses_rule2
    goal = AtomicFormula(Atom("Предок", ["Иван", "Мария"]))
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


def test_resolution_functional_terms():
    print("=== Тест 12: Унификация с функциональными термами ===")
    
    # Клаузы: P(f(a), g(b)), ∀x∀y(P(x,y) → Q(x,y))
    # Цель: Q(f(a), g(b))
    # Ожидается: True (доказано)
    
    p_func = AtomicFormula(Atom("P", ["f(a)", "g(b)"]))
    
    # ∀x∀y(P(x,y) → Q(x,y))
    p_xy = AtomicFormula(Atom("P", ["x", "y"]))
    q_xy = AtomicFormula(Atom("Q", ["x", "y"]))
    rule = BinaryFormula(p_xy, LogicalConnectives.THEN, q_xy)
    quantified_rule = QuantifiedFormula(Quantifiers.UNIVERSALITY, "y",
                                      QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", rule))
    
    converter = FullConverter()
    clauses_rule = converter.to_clauses(quantified_rule)
    
    clauses = [p_func] + clauses_rule
    goal = AtomicFormula(Atom("Q", ["f(a)", "g(b)"]))
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


def test_resolution_nested_quantifiers():
    print("=== Тест 13: Вложенные кванторы ===")
    
    # Клаузы: ∀x∃y(Любит(x,y)), ∀x∀y(Любит(x,y) → Счастлив(x))
    # Цель: ∀x(Счастлив(x))
    # Ожидается: True (доказано)
    
    # ∀x∃y(Любит(x,y))
    loves_xy = AtomicFormula(Atom("Любит", ["x", "y"]))
    exists_loves = QuantifiedFormula(Quantifiers.EXISTENCE, "y", loves_xy)
    forall_exists_loves = QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", exists_loves)
    
    # ∀x∀y(Любит(x,y) → Счастлив(x))
    loves_xy2 = AtomicFormula(Atom("Любит", ["x", "y"]))
    happy_x = AtomicFormula(Atom("Счастлив", ["x"]))
    implication = BinaryFormula(loves_xy2, LogicalConnectives.THEN, happy_x)
    forall_implication = QuantifiedFormula(Quantifiers.UNIVERSALITY, "y",
                                         QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", implication))
    
    # Цель: ∀x(Счастлив(x))
    goal_formula = QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", happy_x)
    
    converter = FullConverter()
    clauses1 = converter.to_clauses(forall_exists_loves)
    clauses2 = converter.to_clauses(forall_implication)
    
    clauses = clauses1 + clauses2
    goal = goal_formula
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


def test_resolution_equality():
    print("=== Тест 14: Равенство и симметричные отношения ===")
    
    # Клаузы: ∀x∀y(Друг(x,y) → Друг(y,x)), Друг(Анна, Боб)
    # Цель: Друг(Боб, Анна)
    # Ожидается: True (доказано)
    
    friend_anna_bob = AtomicFormula(Atom("Друг", ["Анна", "Боб"]))
    
    # ∀x∀y(Друг(x,y) → Друг(y,x))
    friend_xy = AtomicFormula(Atom("Друг", ["x", "y"]))
    friend_yx = AtomicFormula(Atom("Друг", ["y", "x"]))
    symmetry_rule = BinaryFormula(friend_xy, LogicalConnectives.THEN, friend_yx)
    quantified_rule = QuantifiedFormula(Quantifiers.UNIVERSALITY, "y",
                                      QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", symmetry_rule))
    
    converter = FullConverter()
    clauses_rule = converter.to_clauses(quantified_rule)
    
    clauses = [friend_anna_bob] + clauses_rule
    goal = AtomicFormula(Atom("Друг", ["Боб", "Анна"]))
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


def test_resolution_transitive_closure():
    print("=== Тест 15: Транзитивное замыкание ===")
    
    # Клаузы: Связь(A,B), Связь(B,C), Связь(C,D), 
    #         ∀x∀y(Связь(x,y) → Достижимо(x,y)),
    #         ∀x∀y∀z(Достижимо(x,y) ∧ Достижимо(y,z) → Достижимо(x,z))
    # Цель: Достижимо(A,D)
    # Ожидается: True (доказано)
    
    # Факты о связях
    link_ab = AtomicFormula(Atom("Связь", ["A", "B"]))
    link_bc = AtomicFormula(Atom("Связь", ["B", "C"]))
    link_cd = AtomicFormula(Atom("Связь", ["C", "D"]))
    
    # Правила
    # ∀x∀y(Связь(x,y) → Достижимо(x,y))
    link_xy = AtomicFormula(Atom("Связь", ["x", "y"]))
    reachable_xy = AtomicFormula(Atom("Достижимо", ["x", "y"]))
    rule1 = BinaryFormula(link_xy, LogicalConnectives.THEN, reachable_xy)
    quantified_rule1 = QuantifiedFormula(Quantifiers.UNIVERSALITY, "y",
                                       QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", rule1))
    
    # ∀x∀y∀z(Достижимо(x,y) ∧ Достижимо(y,z) → Достижимо(x,z))
    reachable_xy2 = AtomicFormula(Atom("Достижимо", ["x", "y"]))
    reachable_yz = AtomicFormula(Atom("Достижимо", ["y", "z"]))
    reachable_xz = AtomicFormula(Atom("Достижимо", ["x", "z"]))
    antecedent = BinaryFormula(reachable_xy2, LogicalConnectives.AND, reachable_yz)
    rule2 = BinaryFormula(antecedent, LogicalConnectives.THEN, reachable_xz)
    quantified_rule2 = QuantifiedFormula(Quantifiers.UNIVERSALITY, "z",
                                       QuantifiedFormula(Quantifiers.UNIVERSALITY, "y",
                                       QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", rule2)))
    
    converter = FullConverter()
    clauses_rule1 = converter.to_clauses(quantified_rule1)
    clauses_rule2 = converter.to_clauses(quantified_rule2)
    
    clauses = [link_ab, link_bc, link_cd] + clauses_rule1 + clauses_rule2
    goal = AtomicFormula(Atom("Достижимо", ["A", "D"]))
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


def test_resolution_complex_unification():
    print("=== Тест 16: Сложная унификация с несколькими переменными ===")
    
    # Клаузы: P(a,b,c), ∀x∀y∀z(P(x,y,z) → Q(y,x,z))
    # Цель: Q(b,a,c)
    # Ожидается: True (доказано)
    
    p_abc = AtomicFormula(Atom("P", ["a", "b", "c"]))
    
    # ∀x∀y∀z(P(x,y,z) → Q(y,x,z))
    p_xyz = AtomicFormula(Atom("P", ["x", "y", "z"]))
    q_yxz = AtomicFormula(Atom("Q", ["y", "x", "z"]))
    rule = BinaryFormula(p_xyz, LogicalConnectives.THEN, q_yxz)
    quantified_rule = QuantifiedFormula(Quantifiers.UNIVERSALITY, "z",
                                      QuantifiedFormula(Quantifiers.UNIVERSALITY, "y",
                                      QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", rule)))
    
    converter = FullConverter()
    clauses_rule = converter.to_clauses(quantified_rule)
    
    clauses = [p_abc] + clauses_rule
    goal = AtomicFormula(Atom("Q", ["b", "a", "c"]))
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


def test_resolution_negative_unification():
    print("=== Тест 17: Унификация с отрицательными литералами ===")
    
    # Клаузы: ¬P(a) ∨ Q(b), P(x) ∨ R(x), ¬R(a)
    # Цель: Q(b)
    # Ожидается: True (доказано)
    
    not_p_a = NegativeFormula(AtomicFormula(Atom("P", ["a"])))
    q_b = AtomicFormula(Atom("Q", ["b"]))
    clause1 = BinaryFormula(not_p_a, LogicalConnectives.OR, q_b)
    
    p_x = AtomicFormula(Atom("P", ["x"]))
    r_x = AtomicFormula(Atom("R", ["x"]))
    clause2 = BinaryFormula(p_x, LogicalConnectives.OR, r_x)
    
    not_r_a = NegativeFormula(AtomicFormula(Atom("R", ["a"])))
    
    clauses = [clause1, clause2, not_r_a]
    goal = q_b
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


def test_resolution_function_composition():
    print("=== Тест 18: Композиция функций ===")
    
    # Клаузы: P(f(g(a))), ∀x(P(x) → Q(x))
    # Цель: Q(f(g(a)))
    # Ожидается: True (доказано)
    
    p_fga = AtomicFormula(Atom("P", ["f(g(a))"]))
    
    # ∀x(P(x) → Q(x))
    p_x = AtomicFormula(Atom("P", ["x"]))
    q_x = AtomicFormula(Atom("Q", ["x"]))
    rule = BinaryFormula(p_x, LogicalConnectives.THEN, q_x)
    quantified_rule = QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", rule)
    
    converter = FullConverter()
    clauses_rule = converter.to_clauses(quantified_rule)
    
    clauses = [p_fga] + clauses_rule
    goal = AtomicFormula(Atom("Q", ["f(g(a))"]))
    
    print("Клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print(f"Цель: {goal}")
    
    resolver = ResolutionAlgorithm()
    result = resolver.resolve(clauses, goal)
    
    print(f"\nРезультат: {'ДОКАЗАНО' if result else 'НЕ ДОКАЗАНО'}")
    print(f"Ожидалось: ДОКАЗАНО")
    print()


if __name__ == "__main__":
    # Существующие тесты

    
    # Новые сложные тесты
    test_resolution_complex_predicates()
    test_resolution_functional_terms()
    test_resolution_nested_quantifiers()
    test_resolution_equality()
    test_resolution_transitive_closure()
    test_resolution_complex_unification()
    test_resolution_negative_unification()
    test_resolution_function_composition()