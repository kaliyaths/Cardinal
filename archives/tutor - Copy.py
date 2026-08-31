
from ollama import chat
from prompts import SYSTEM_PROMPT

messages = [
    {
        "role":"system",
        "content":SYSTEM_PROMPT
        }
    ]

def ask_tutor(question):
    messages.append(
        {
            "role": "user",
            "content":question
            }
        )

    response =chat(
        model="gemma3:4b",
        messages=messages
        )

    answer =response["message"]["content"]

    messages.append(
        {
            "role":"assistant",
            "content": answer
            }
        )

    return answer
