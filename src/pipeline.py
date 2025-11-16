from __future__ import annotations

import os
import sys

# По хорошему отдельно каждому файлу указывать, с какой директорией работать, 
# но здесь это применимо, так как все файлы работают в директории с запускаемым скриптом
def setup_dir():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(script_dir)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)


setup_dir()


import argparse
import logging
from io import StringIO
from typing import Dict, List, Tuple

from model1.LLMFormalizer import convert_to_predicate_logic
from model2.types.BaseTypes import Formula
from model2.utils.Parser import Parser
from model2.utils.ResolutionAlgorithm import ResolutionAlgorithm
from model3.LLMExplainer import explain_proof


DEFAULT_TASK = "Сократ — человек. Все люди смертны. Докажи, что Сократ смертен."


def run_pipeline(user_text: str) -> Dict[str, object]:
    """Запускает полный логический пайплайн (Модуль 1 → Модуль 2 → Модуль 3)."""

    # === Модуль 1: формализация ===
    formalized = convert_to_predicate_logic(user_text)

    parser = Parser()
    parsed_formulas = parser.parse_input(formalized)
    clauses, goal = _split_premises_and_goal(parsed_formulas)

    # === Модуль 2: резолюция ===
    resolver = ResolutionAlgorithm()
    proved, resolution_log = _run_resolution_with_logs(resolver, clauses, goal)

    # === Модуль 3: объяснение (LLM) ===
    explanation_md = explain_proof(
        user_text=user_text,
        formalized=formalized,
        log=resolution_log,
        proved=proved,
    )

    return {
        "input": user_text,
        "formalized": formalized,
        "clauses": clauses,
        "goal": goal,
        "proved": proved,
        "logs": resolution_log,
        "explanation": explanation_md,
    }


def _split_premises_and_goal(formulas: List[Formula]) -> Tuple[List[Formula], Formula]:
    if not formulas or len(formulas) < 2:
        raise ValueError(
            "Недостаточно формул: требуется минимум одна предпосылка и цель для алгоритма резолюции."
        )

    clauses = formulas[:-1]
    goal = formulas[-1]
    return clauses, goal


def _run_resolution_with_logs(
    resolver: ResolutionAlgorithm, clauses: List[Formula], goal: Formula
) -> Tuple[bool, str]:
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    original_level = root_logger.level
    root_logger.addHandler(handler)
    if original_level > logging.INFO:
        root_logger.setLevel(logging.INFO)

    try:
        proved = resolver.resolve(clauses, goal)
    finally:
        root_logger.removeHandler(handler)
        root_logger.setLevel(original_level)

    return proved, log_stream.getvalue().strip()


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "text",
        nargs="?",
        default=DEFAULT_TASK,
        help="Задача на естественном языке, которую нужно доказать",
    )
    return parser


def main() -> None:
    args = _build_argument_parser().parse_args()
    result = run_pipeline(args.text)

    lines: List[str] = []

    lines.append("=== Формализация (Модуль 1) ===")
    lines.append(str(result["formalized"]))
    lines.append("")

    lines.append("=== Логи резолюции (Модуль 2) ===")
    lines.append(str(result["logs"]))
    lines.append("")

    lines.append("=== Статус доказательства ===")
    lines.append("ДОКАЗАНО" if result["proved"] else "НЕ ДОКАЗАНО")
    lines.append("")

    lines.append("=== Объяснение (Модуль 3) ===")
    lines.append(str(result["explanation"]))
    lines.append("")

    full_output = "\n".join(lines)

    print(full_output)

    try:
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(full_output)
        print("Полный вывод также сохранён в файл: output.txt")
    except Exception as e:
        print(f"Не удалось сохранить output.txt: {e}")

    try:
        with open("explanation.md", "w", encoding="utf-8") as f:
            f.write(str(result["explanation"]))
        print("Объяснение также сохранено в файл: explanation.md")
    except Exception as e:
        print(f"Не удалось сохранить explanation.md: {e}")


if __name__ == "__main__":
    main()
