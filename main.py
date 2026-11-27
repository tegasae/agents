import json
import os
from typing import cast

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)


def multiply(a: float, b: float) -> float:
    return a * b


client = OpenAI(
    api_key="sk-d665306c3bec46a7a2f225010db520a9",
    base_url="https://api.deepseek.com",
)

tools: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Перемножает два числа.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
                "additionalProperties": False,
            },
        },
    },
]

# ИЗМЕНИЛИ 1. Задача требует двух последовательных вызовов.
messages: list[ChatCompletionMessageParam] = [
    {
        "role": "user",
        "content": (
            "Вызови multiply для 17 и 23. Дождись результата, затем "
            "отдельным вызовом multiply умножь его на 2."
        ),
    }
]

# ИЗМЕНИЛИ 2. Вместо двух отдельных create() теперь один в цикле.
# На каждом шаге передаём tools и разрешаем модели вызвать инструмент.
for _ in range(5):
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=messages,
        tools=tools,
        extra_body={"thinking": {"type": "disabled"}},
    )
    message = response.choices[0].message

    # ИЗМЕНИЛИ 3. Если вызовов нет, выводим ответ и выходим из цикла.
    if not message.tool_calls:
        print("Ответ DeepSeek:", message.content)
        break

    # Сохраняем сообщение модели с запросами на вызов.
    assistant_message = cast(
        ChatCompletionAssistantMessageParam,
        message.model_dump(include={"role", "content", "tool_calls"}),
    )
    messages.append(assistant_message)

    for call in message.tool_calls:
        if call.type != "function" or call.function.name != "multiply":
            raise ValueError("Неизвестный инструмент")

        arguments = json.loads(call.function.arguments)
        result = multiply(**arguments)
        print("Результат Python:", result)

        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": str(result),
        })

    # ИЗМЕНИЛИ 4. Следующая итерация отправит историю с результатами.
else:
    # Эта ветка for выполняется, если все пять итераций прошли без break.
    print("Достигнут лимит запросов к модели.")