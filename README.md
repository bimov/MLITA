# MLITA

1. Регистрируемся на сатйе [https://openrouter.ai](OpenRouter)
2. Создаем API-ключ здесь [https://openrouter.ai/settings/keys](OpenRouterApi)
3. На Linux/MacOS создаем виртуальное окружение:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. Задаем переменную OPENROUTER_API_KEY:
   ```sh
   export OPENROUTER_API_KEY=sk_**
   ```
5. Теперь можно использовать функцию `send_message`:
   ```py
   from main import send_message
   
   print(send_message('Какой сейчас год?'))
   ```
