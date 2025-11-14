from __future__ import annotations

import argparse
import logging
from io import StringIO
from typing import Dict, List, Tuple

from model1.LLMFormalizer import convert_to_predicate_logic
from model1.OpenRouterChat import send_message
from model2.types.BaseTypes import Formula
from model2.utils.Parser import Parser
from model2.utils.ResolutionAlgorithm import ResolutionAlgorithm


EXPLANATION_SYSTEM_PROMPT = (
    "Ты — учитель логики. Объясни доказательство, представленное в виде последовательности "
    "логических шагов, как если бы ты объяснял его студенту. Будь последовательным и ясным. "
    "Используй естественный русский язык."
)

DEFAULT_TASK = "Сократ — человек. Все люди смертны. Докажи, что Сократ смертен."


def run_pipeline(user_text: str) -> Dict[str, object]:
    """Runs the two-stage reasoning pipeline and returns all intermediate artifacts."""

    formalized = convert_to_predicate_logic(user_text)

    parser = Parser()
    parsed_formulas = parser.parse_input(formalized)
    clauses, goal = _split_premises_and_goal(parsed_formulas)

    resolver = ResolutionAlgorithm()
    proved, resolution_log = _run_resolution_with_logs(resolver, clauses, goal)

    explanation_prompt = _build_explanation_prompt(
        user_text=user_text,
        formalized=formalized,
        log=resolution_log,
        proved=proved,
    )

    explanation = send_message(explanation_prompt, system_prompt=EXPLANATION_SYSTEM_PROMPT)

    return {
        "input": user_text,
        "formalized": formalized,
        "clauses": clauses,
        "goal": goal,
        "proved": proved,
        "logs": resolution_log,
        "explanation": explanation,
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


def _build_explanation_prompt(*, user_text: str, formalized: str, log: str, proved: bool) -> str:
    status_line = "Доказательство завершилось успехом." if proved else "Доказательство не удалось завершить."
    log_text = log or "Лог алгоритма пуст."
    return (
        "Исходная задача:\n"
        f"{user_text}\n\n"
        "Формулы (выход Модуля 1):\n"
        f"{formalized}\n\n"
        f"{status_line}\n"
        "Журнал работы алгоритма резолюции:\n"
        f"{log_text}\n\n"
        "Поясни ход рассуждений и сделай вывод."
    )


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="End-to-end логический пайплайн")
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

    print("=== Формализация (Модуль 1) ===")
    print(result["formalized"])
    print()

    print("=== Логи резолюции (Модуль 2) ===")
    print(result["logs"])
    print()

    print("=== Статус доказательства ===")
    print("ДОКАЗАНО" if result["proved"] else "НЕ ДОКАЗАНО")
    print()

    print("=== Объяснение (LLM) ===")
    print(result["explanation"])


if __name__ == "__main__":
    main()