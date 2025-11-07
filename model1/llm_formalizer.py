import os
import json
import requests

# ==== Конфигурация ====
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("Переменная окружения OPENROUTER_API_KEY не установлена")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "gpt-4o-mini"

# ==== Системный промпт ====
SYSTEM_PROMPT = """Ты — экспертный ассистент по формальной логике. 
Преобразуй текстовую задачу на естественном языке в набор формул логики предикатов.

Правила:
1. Выведи ТОЛЬКО формулы, разделённые запятыми. Без пояснений, примеров, нумерации или слов.
2. Формулы должны быть вида: Предикат(Объект) или ¬Предикат(Объект).
3. Допустимые логические связки: ¬, ∧, ∨, →.
4. Допустимо использовать переменные (x, y, z) и константы (Сократ, Петя и т.п.).
5. Для всеобщих утверждений используй явный квантор ∀, например: ∀x (Человек(x) → Смертен(x)).
6. Для экзистенциальных утверждений используй ∃, например: ∃x (Птица(x) ∧ УмеетЛетать(x)).

Пример:
Вход: 'Сократ — человек. Все люди смертны. Докажи, что Сократ смертен.'
Выход: 'Человек(Сократ), ∀x (Человек(x) → Смертен(x)), Смертен(Сократ)'
"""

# ==== Основная функция ====
def send_message(user_text: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.0,
        "max_tokens": 400
    }

    resp = requests.post(API_URL, headers=headers, data=json.dumps(data))
    if resp.status_code != 200:
        raise RuntimeError(f"Ошибка API ({resp.status_code}): {resp.text}")

    result = resp.json()
    return result["choices"][0]["message"]["content"].strip()


# ==== Тест ====
if __name__ == "__main__":
    test_inputs = [
        "Сократ — человек. Все люди смертны. Докажи, что Сократ смертен.",
        "Если кто-то человек, то он смертен.",
        "Существует кто-то, кто говорит правду и бессмертен.",
         "Сократ — человек. Все люди смертны. Докажи, что Сократ смертен.",
        "Все кошки — животные. Мурка — кошка. Докажи, что Мурка — животное.",
        "Некоторые птицы умеют летать. Пингвин — птица. Докажи, что пингвин умеет летать.",
        "Если идет дождь, то улица мокрая. Улица мокрая. Докажи, что идет дождь.",
        "Все студенты сдают экзамены. Петя — студент. Докажи, что Петя сдает экзамены."
    ]
    for inp in test_inputs:
        print(f"\nВход: {inp}")
        print("Выход:", send_message(inp))
