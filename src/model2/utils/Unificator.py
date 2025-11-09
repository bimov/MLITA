from typing import Union
from model2.types.base_types import *
import logging

class Unificator:
    def __init__(self):
        pass

    def unify_atoms(self, first: Atom, second: Atom, replaces = None):
        if replaces is None:
            replaces = {}

        first_values = first.get_values()
        second_values = second.get_values()
        global variables

        if first.get_func() != second.get_func() or len(first_values) != len(second_values):
            return None

        if first == second:
            return first, second, replaces

        for i in range(len(first_values)):
            # Применяем существующие подстановки
            if isinstance(first_values[i], str) and first_values[i] in replaces:
                first_values[i] = replaces[first_values[i]]
            if isinstance(second_values[i], str) and second_values[i] in replaces:
                second_values[i] = replaces[second_values[i]]
            try:
                if first_values[i] == second_values[i]:
                    continue
            except:
                pass

            if isinstance(first_values[i], Atom) and isinstance(second_values[i], Atom):
                first_values[i], second_values[i], replaces = self.unify_atoms(first_values[i], second_values[i])
            elif isinstance(first_values[i], str) and isinstance(second_values[i], str):
                if first_values[i] not in variables:
                    logging.info(f"[Унификация {second_values[i]}/{first_values[i]} в {second}]")
                    replaces[second_values[i]] = first_values[i]
                    second_values[i] = first_values[i]
                else:
                    logging.info(f"[Унификация {first_values[i]}/{second_values[i]} в {first}]")
                    replaces[first_values[i]] = second_values[i]
                    first_values[i] = second_values[i]
            else:
                if isinstance(first_values[i], str):
                    if first_values[i] not in variables:
                        logging.info(f"[Унификация {second_values[i]}/{first_values[i]} в {second}]")
                        replaces[second_values[i]] = first_values[i]
                        second_values[i] = first_values[i]
                    elif second_values[i].is_constant():
                        logging.info(f"[Унификация {first_values[i]}/{second_values[i]} в {first}]")
                        replaces[first_values[i]] = second_values[i]
                        first_values[i] = second_values[i]
                    else:
                        logging.info(f"[Унификация {second_values[i]}/{first_values[i]} в {second}]")
                        replaces[second_values[i]] = first_values[i]
                        second_values[i] = first_values[i]
                else:
                    if second_values[i] not in variables:
                        logging.info(f"[Унификация {first_values[i]}/{second_values[i]} в {first}]")
                        replaces[first_values[i]] = second_values[i]
                        first_values[i] = second_values[i]
                    elif first_values[i].is_constant():
                        logging.info(f"[Унификация {second_values[i]}/{first_values[i]} в {second}]")
                        replaces[second_values[i]] = first_values[i]
                        second_values[i] = first_values[i]
                    else:
                        logging.info(f"[Унификация {first_values[i]}/{second_values[i]} в {first}]")
                        replaces[first_values[i]] = second_values[i]
                        first_values[i] = second_values[i]

        return first, second, replaces



    def unify_formules(self, first: Formula, second: Formula, replaces = None):
        if replaces is None:
            replaces = {}

        first_atoms = self._extract_atoms(first)
        second_atoms = self._extract_atoms(second)

        current_replaces = replaces.copy()
        changed = True

        while changed:
            changed = False
            found_new_unification = False

            for first_atom_data in first_atoms:
                for second_atom_data in second_atoms:

                    if first_atom_data['negative'] != second_atom_data['negative']:
                        continue

                    result = self.unify_atoms(
                        first_atom_data['atom'], second_atom_data['atom'], current_replaces.copy()
                    )

                    if result:
                        unified_first_atom, unified_second_atom, new_replaces = result

                        if unified_first_atom is not None and unified_second_atom is not None:
                            if new_replaces != current_replaces:
                                current_replaces = new_replaces
                                changed = True
                                found_new_unification = True
                                break
                if found_new_unification:
                    break

        if current_replaces != replaces:
            final_first = self._apply_substitution_to_formula(first, current_replaces)
            final_second = self._apply_substitution_to_formula(second, current_replaces)
            return final_first, final_second, current_replaces

        return None, None, replaces

    def _extract_atoms(self, formula: Formula):
        atoms = []

        if isinstance(formula, AtomicFormula):
            atoms.append({'atom': formula.atom, 'negative': False})

        elif isinstance(formula, NegativeFormula):
            if isinstance(formula.formula, AtomicFormula):
                atoms.append({'atom': formula.formula.atom, 'negative': True})
            else:
                inner_atoms = self._extract_atoms(formula.formula)
                for atom_data in inner_atoms:
                    atoms.append({'atom': atom_data['atom'], 'negative': not atom_data['negative']})

        elif isinstance(formula, BinaryFormula):
            left_atoms = self._extract_atoms(formula.left)
            right_atoms = self._extract_atoms(formula.right)
            atoms.extend(left_atoms)
            atoms.extend(right_atoms)

        return atoms

    def _apply_substitution_to_formula(self, formula: Formula, substitution):
        if isinstance(formula, AtomicFormula):
            new_atom = self._apply_substitution_to_atom(formula.atom, substitution)
            return AtomicFormula(new_atom)

        elif isinstance(formula, NegativeFormula):
            new_inner = self._apply_substitution_to_formula(formula.formula, substitution)
            return NegativeFormula(new_inner)

        elif isinstance(formula, BinaryFormula):
            new_left = self._apply_substitution_to_formula(formula.left, substitution)
            new_right = self._apply_substitution_to_formula(formula.right, substitution)
            return BinaryFormula(new_left, formula.connective, new_right)

        return formula

    def _apply_substitution_to_atom(self, atom: Atom, substitution):
        new_values = []
        for value in atom.values:
            if isinstance(value, str) and value in substitution:
                new_values.append(substitution[value])
            elif isinstance(value, Atom):
                new_values.append(self._apply_substitution_to_atom(value, substitution))
            else:
                new_values.append(value)
        return Atom(atom.func, new_values)