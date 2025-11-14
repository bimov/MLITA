import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ..types.base_types import *
from ..utils.FullConverter import FullConverter

def test_full_conversion_simple():
    print("=== Тест 1: Простая импликация ===")
    
    # ∀x(Человек(x) → Смертен(x))
    human_x = AtomicFormula(Atom("Человек", ["x"]))
    mortal_x = AtomicFormula(Atom("Смертен", ["x"]))
    implies = BinaryFormula(human_x, LogicalConnectives.THEN, mortal_x)
    formula = QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", implies)
    
    print("Исходная формула:", formula)
    
    converter = FullConverter()
    clauses = converter.to_clauses(formula)
    
    print("\nРезультирующие дизъюнкты:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print()


def test_full_conversion_nested_quantifiers():
    print("=== Тест 2: Вложенные кванторы ===")
    
    # ∀x∃y(Любит(x, y) ∧ Женщина(y))
    loves_xy = AtomicFormula(Atom("Любит", ["x", "y"]))
    woman_y = AtomicFormula(Atom("Женщина", ["y"]))
    conj = BinaryFormula(loves_xy, LogicalConnectives.AND, woman_y)
    exists_y = QuantifiedFormula(Quantifiers.EXISTENCE, "y", conj)
    formula = QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", exists_y)
    
    print("Исходная формула:", formula)
    
    converter = FullConverter()
    clauses = converter.to_clauses(formula)
    
    print("\nРезультирующие дизъюнкты:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print()


def test_full_conversion_complex():
    print("=== Тест 3: Сложная формула с импликацией ===")
    
    # ∀x(Студент(x) → ∃y(Преподаватель(y) ∧ Изучает(x, y)))
    student_x = AtomicFormula(Atom("Студент", ["x"]))
    teacher_y = AtomicFormula(Atom("Преподаватель", ["y"]))
    studies_xy = AtomicFormula(Atom("Изучает", ["x", "y"]))
    conj = BinaryFormula(teacher_y, LogicalConnectives.AND, studies_xy)
    exists_y = QuantifiedFormula(Quantifiers.EXISTENCE, "y", conj)
    implies = BinaryFormula(student_x, LogicalConnectives.THEN, exists_y)
    formula = QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", implies)
    
    print("Исходная формула:", formula)
    
    converter = FullConverter()
    clauses = converter.to_clauses(formula)
    
    print("\nРезультирующие дизъюнкты:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print()


def test_full_conversion_with_negation():
    print("=== Тест 4: Формула с отрицанием ===")
    
    # ∃x(Студент(x) ∧ ¬Сдал(x))
    student_x = AtomicFormula(Atom("Студент", ["x"]))
    passed_x = AtomicFormula(Atom("Сдал", ["x"]))
    not_passed = NegativeFormula(passed_x)
    conj = BinaryFormula(student_x, LogicalConnectives.AND, not_passed)
    formula = QuantifiedFormula(Quantifiers.EXISTENCE, "x", conj)
    
    print("Исходная формула:", formula)
    
    converter = FullConverter()
    clauses = converter.to_clauses(formula)
    
    print("\nРезультирующие дизъюнкты:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print()


def test_full_conversion_disjunction():
    print("=== Тест 5: Дизъюнкция с кванторами ===")
    
    # ∀x(Человек(x) → (Мужчина(x) ∨ Женщина(x)))
    human_x = AtomicFormula(Atom("Человек", ["x"]))
    man_x = AtomicFormula(Atom("Мужчина", ["x"]))
    woman_x = AtomicFormula(Atom("Женщина", ["x"]))
    disj = BinaryFormula(man_x, LogicalConnectives.OR, woman_x)
    implies = BinaryFormula(human_x, LogicalConnectives.THEN, disj)
    formula = QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", implies)
    
    print("Исходная формула:", formula)
    
    converter = FullConverter()
    clauses = converter.to_clauses(formula)
    
    print("\nРезультирующие дизъюнкты:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print()


def test_full_conversion_multiple_universal():
    print("=== Тест 6: Несколько универсальных кванторов ===")
    
    # ∀x∀y(Родитель(x, y) → Старше(x, y))
    parent_xy = AtomicFormula(Atom("Родитель", ["x", "y"]))
    older_xy = AtomicFormula(Atom("Старше", ["x", "y"]))
    implies = BinaryFormula(parent_xy, LogicalConnectives.THEN, older_xy)
    forall_y = QuantifiedFormula(Quantifiers.UNIVERSALITY, "y", implies)
    formula = QuantifiedFormula(Quantifiers.UNIVERSALITY, "x", forall_y)
    
    print("Исходная формула:", formula)
    
    converter = FullConverter()
    clauses = converter.to_clauses(formula)
    
    print("\nРезультирующие дизъюнкты:")
    for i, clause in enumerate(clauses, 1):
        print(f"  {i}. {clause}")
    print()


if __name__ == "__main__":
    test_full_conversion_simple()
    test_full_conversion_nested_quantifiers()
    test_full_conversion_complex()
    test_full_conversion_with_negation()
    test_full_conversion_disjunction()
    test_full_conversion_multiple_universal()