from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-haiku-4-5"


def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def chat(messages):
    message = client.messages.create(
        model=model,
        max_tokens=100,
        messages=messages,
    )
    return message.content[0].text


# main
messages = []

add_user_message(messages, "define quantum computing in one sentence")
answer = chat(messages)
print(answer)
add_assistant_message(messages, answer)

add_user_message(messages, "write another sentence")
final_answer = chat(messages)
print(final_answer)
