import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ..utils.Unificator import *
from ..types.base_types import *
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler()  # Вывод в консоль
    ]
)


def test1():
    first = Atom('Человек', 'x')
    second = Atom('Человек', 'Сократ')

    variables.clear()
    variables.append('x')
    unificator = Unificator()

    result = unificator.unify_atoms(first, second)

    new_first, new_second, replaces = result
    print(f"Первый атом: {new_first}")
    print(f"Второй атом: {new_second}")
    print(f"Подстановки: {replaces}")
    print()


def test2():
    first = Atom('Человек', 'Олег')
    second = Atom('Человек', 'Сократ')

    variables.clear()
    variables.append('x')
    unificator = Unificator()

    result = unificator.unify_atoms(first, second)

    new_first, new_second, replaces = result
    print(f"Первый атом: {new_first}")
    print(f"Второй атом: {new_second}")
    print(f"Подстановки: {replaces}")
    print()

def test3():
    first = Atom('Человек', ['x', 'Сократ'])
    second = Atom('Человек', ['y', 'z'])

    variables.clear()
    variables.append('x')
    variables.append('y')
    variables.append('z')
    unificator = Unificator()

    result = unificator.unify_atoms(first, second)

    new_first, new_second, replaces = result
    print(f"Первый атом: {new_first}")
    print(f"Второй атом: {new_second}")
    print(f"Подстановки: {replaces}")
    print()

def test4():
    first = AtomicFormula(Atom('Человек', ['x', 'Сократ']))
    second = AtomicFormula(Atom('Человек', ['y', 'z']))

    variables.clear()
    variables.append('x')
    variables.append('y')
    variables.append('z')
    unificator = Unificator()

    result = unificator.unify_formules(first, second)

    new_first, new_second, replaces = result
    print(f"Первая формула: {new_first}")
    print(f"Вторая формула: {new_second}")
    print(f"Подстановки: {replaces}")
    print()

def test5():
    first = BinaryFormula(AtomicFormula(Atom('НеЧеловек', 'z')),
                          LogicalConnectives.OR,
                          AtomicFormula(Atom('Человек', ['x', 'Сократ'])))
    second = AtomicFormula(Atom('Человек', ['y', 'z']))

    variables.clear()
    variables.append('x')
    variables.append('y')
    variables.append('z')
    unificator = Unificator()

    result = unificator.unify_formules(first, second)

    new_first, new_second, replaces = result
    print(f"Первая формула: {new_first}")
    print(f"Вторая формула: {new_second}")
    print(f"Подстановки: {replaces}")
    print()

def test6():
    first = BinaryFormula(NegativeFormula(AtomicFormula(Atom('Человек', 'x'))),
                          LogicalConnectives.OR,
                          BinaryFormula(AtomicFormula(Atom('НеЧеловек', ['y', 'x'])),
                                        LogicalConnectives.AND,
                                        AtomicFormula(Atom('Рыбы', 'Карась'))))
    second = BinaryFormula(BinaryFormula(AtomicFormula(Atom('НеЧеловек', ['Лосось', 'Посейдон'])),
                                        LogicalConnectives.AND,
                                        AtomicFormula(Atom('Рыбы', 'Карась'))),
                          LogicalConnectives.OR,
                          BinaryFormula(AtomicFormula(Atom('НеЧеловек', ['y', 'y'])),
                                        LogicalConnectives.AND,
                                        AtomicFormula(Atom('Рыбы', 'z'))))
    variables.clear()
    variables.append('x')
    variables.append('y')
    variables.append('z')
    unificator = Unificator()

    result = unificator.unify_formules(first, second)

    new_first, new_second, replaces = result
    print(f"Первая формула: {new_first}")
    print(f"Вторая формула: {new_second}")
    print(f"Подстановки: {replaces}")
    print()

if __name__ == '__main__':
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()