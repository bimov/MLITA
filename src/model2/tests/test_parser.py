import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ..utils.Parser import *


def test1():
    data = 'Человек(Сократ), ¬Человек(x) ∨ Смертен(x), Смертен(Сократ)'
    parser = Parser()
    result = parser.parse_input(data)
    print(f'Вход: {data}')
    print(f'Выход: {result}\n')


def test2():
    data = '∀x (Человек(x) → Смертен(x))'
    parser = Parser()
    result = parser.parse_input(data)
    print(f'Вход: {data}')
    print(f'Выход: {result}\n')


def test3():
    data = '(∃x ГоворитПравду(x; Сократ; Магелан) ∧ (∃x0 Бессмертен(x0)))'
    parser = Parser()
    result = parser.parse_input(data)
    print(f'Вход: {data}')
    print(f'Выход: {result}\n')


def test4():
    data = '¬Смертен(Сократ), (∃x ГоворитПравду(x; Сократ; Магелан) ∧ (∃x0 Бессмертен(x0)))'
    parser = Parser()
    result = parser.parse_input(data)
    print(f'Вход: {data}')
    print(f'Выход: {result}\n')


if __name__ == '__main__':
    test1()
    test2()
    test3()
    test4()