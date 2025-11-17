from openai import OpenAI
import os
from typing import Optional, Dict, List

DEFAULT_MODEL = "tngtech/deepseek-r1t2-chimera:free"
DEFAULT_HEADERS: Dict[str, str] = {
    "HTTP-Referer": "https://github.com/bimov/MLITA",
    "X-Title": "MLITA",
}

class OpenRouterChat:
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL,
                 base_url: str = "https://openrouter.ai/api/v1", extra_headers: Optional[Dict[str, str]] = None,) -> None:
        api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("Укажите OPENROUTER_API_KEY в окружении или передайте api_key в конструктор.")

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.extra_headers = extra_headers or DEFAULT_HEADERS

    def send(self, content: str, system_prompt: Optional[str] = None) -> str:
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": content})
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            extra_headers=self.extra_headers,
            extra_body={},
        )
        return completion.choices[0].message.content


def send_message(content: str, model: str = DEFAULT_MODEL, system_prompt: Optional[str] = None) -> str:
    return OpenRouterChat(model=model).send(content, system_prompt=system_prompt)
