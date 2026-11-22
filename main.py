
##
import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

client = OpenAI(

    base_url="https://api.deepseek.com",
    api_key="sk-d665306c3bec46a7a2f225010db520a9",
)

messages: list[ChatCompletionMessageParam] = [
    {"role": "user", "content": "Привет! Ответь одним предложением."}
]

response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
)
print(response.choices[0].message.content)