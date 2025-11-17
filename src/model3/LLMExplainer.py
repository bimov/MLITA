from __future__ import annotations

from model1.OpenRouterChat import send_message
from model3.promts import EXPLANATION_SYSTEM_PROMPT, build_explanation_prompt


def explain_proof(*, user_text: str, formalized: str, log: str, proved: bool,) -> str:
    """
    Принимает исходный текст задачи, формализацию, лог резолюции и статус доказательства,
    а возвращает красивое объяснение в формате Markdown.
    """
    user_prompt = build_explanation_prompt(
        user_text=user_text,
        formalized=formalized,
        log=log,
        proved=proved,
    )

    explanation_md = send_message(
        user_prompt,
        system_prompt=EXPLANATION_SYSTEM_PROMPT,
    )
    return explanation_md
