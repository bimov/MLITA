from typing import Union
import re
from ..types.BaseTypes import *


class Parser:
    def __init__(self):
        self.quantifiers = [quantifier.value for quantifier in Quantifiers]
        variables.clear()


    def parse_input(self, input_data: Union[str, None]):
        if input_data is None:
            return None                             #TODO

        parsed_data = []
        messages = input_data.split(',')
        for message in messages:
            current_data = self.__regex_parse(message)
            polish_notation = self.__create_polish_notation(current_data)
            parsed_data.append(self.__create_formula(polish_notation))

        return parsed_data


    def __regex_parse(self, input_data: Union[str, None]):
        if input_data is None:
            return None

        patterns = [
            (r'∀[a-z][a-z0-9]*|∃[a-z][a-z0-9]*', 'QUANTIFIER'),
            (r'→|¬|∧|∨|↔|⊕', 'OPERATOR'),
            (r'[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё0-9_]*', 'IDENTIFIER'),
            (r'\(', 'LPAREN'),
            (r'\)', 'RPAREN'),
            (r';', 'COMMA'),
            (r'\s+', 'WHITESPACE')
        ]

        regex_patterns = [(re.compile(pattern), token_type) for pattern, token_type in patterns]

        tokens = []
        pos = 0

        while pos < len(input_data):
            match = None

            for pattern, token_type in regex_patterns:
                match = pattern.match(input_data, pos)
                if match:
                    value = match.group(0)
                    if token_type != 'WHITESPACE':
                        if token_type == 'IDENTIFIER':
                            if re.match(r'^[a-z]+', value):
                                actual_type = 'VARIABLE'
                                variables.append(value)
                            else:
                                actual_type = 'FUNCTION'
                        else:
                            actual_type = token_type

                        tokens.append({'type': actual_type, 'value': value, 'stage': 0, 'args': 0})

                    pos = match.end()
                    break

            if not match:
                raise ValueError(f"Неизвестный символ в позиции {pos}: '{input_data[pos]}'")

        args = [1]
        for i in range(len(tokens) - 2, -1, -1):
            if tokens[i]['type'] == 'COMMA':
                args[-1] += 1
            if tokens[i]['type'] == 'RPAREN':
                args.append(1)
            if tokens[i]['type'] == 'LPAREN':
                if tokens[i-1]['type'] == 'FUNCTION':
                    tokens[i-1]['args'] = args[-1]
                args.pop(-1)
            if tokens[i]['type'] == 'FUNCTION':
                if tokens[i + 1]['type'] in ['RPAREN', 'COMMA']:
                    tokens[i]['type'] = 'CONSTANT'

        return tokens


    def __pop_other(self, stack: list, write_notation: list, value: int):
        while len(stack) > 0 and stack[-1][1] >= value:
            if value == 0 and stack[-1][1] == 0:
                stack.pop()
                break
            write_notation.append(stack.pop()[0])


    def __create_polish_notation(self, indexes: list[str]):
        stack = []
        first_lvl = [LogicalConnectives.IFF.value]    # ↔
        second_lvl = [LogicalConnectives.THEN.value]          # →
        third_lvl = [LogicalConnectives.OR.value]             # ∨
        fourth_lvl = [LogicalConnectives.XOR.value]           # ⊕
        fifth_lvl = [LogicalConnectives.AND.value]            # ∧
        sixth_lvl = ['¬']
        write_notation = []
        bracket = ['(', ')']

        for i in indexes:
            value = i['value']
            if value[0] in self.quantifiers:
                self.__pop_other(stack, write_notation, 5)
                stack.append((i, 5))
            elif value in first_lvl:
                self.__pop_other(stack, write_notation, 1)
                stack.append((i, 1))
            elif value in second_lvl:
                self.__pop_other(stack, write_notation, 2)
                stack.append((i, 2))
            elif value in third_lvl:
                self.__pop_other(stack, write_notation, 3)
                stack.append((i, 3))
            elif value in fourth_lvl:
                self.__pop_other(stack, write_notation, 4)
                stack.append((i, 4))
            elif value in fifth_lvl:
                self.__pop_other(stack, write_notation, 4)
                stack.append((i, 5))
            elif value in sixth_lvl:
                self.__pop_other(stack, write_notation, 4)
                stack.append((i, 6))
            elif value in bracket:
                if value == '(':
                    stack.append((i, 0))
                else:
                    self.__pop_other(stack, write_notation, 0)
            else:
                if i['type'] == 'COMMA':
                    continue
                if i['type'] == 'FUNCTION':
                    self.__pop_other(stack, write_notation, 6)
                    stack.append((i, 6))
                else:
                    write_notation.append(i)

        while len(stack) > 0:
            write_notation.append(stack.pop()[0])
        return write_notation


    def __create_formula(self, polish_notation: list[str]):
        stack = []

        for token in polish_notation:
            if token['type'] in ['CONSTANT', 'VARIABLE']:
                stack.append(token['value'])
            elif token['type'] == 'FUNCTION':
                args = []
                for _ in range(token['args']):
                    if stack:
                        args.insert(0, stack.pop())
                stack.append(AtomicFormula(Atom(token['value'], args)))
            elif token['value'] == '¬':
                if stack:
                    operand = stack.pop()
                    stack.append(NegativeFormula(operand))
            elif token['type'] == 'OPERATOR' and token['value'] != '¬':
                if len(stack) >= 2:
                    right = stack.pop()
                    left = stack.pop()
                    connective = LogicalConnectives.get(token['value'])
                    stack.append(BinaryFormula(left, connective, right))
            elif token['type'] == 'QUANTIFIER':
                if stack:
                    formula = stack.pop()
                    quantifier = Quantifiers.get(token['value'][0])
                    variable = token['value'][1:]
                    stack.append(QuantifiedFormula(quantifier, variable, formula))

        return stack[0] if stack else None
