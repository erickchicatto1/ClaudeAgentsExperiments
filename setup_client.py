from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-haiku-4-5"

if __name__ == "__main__":
    respuesta = client.messages.create(
        model=model,
        max_tokens=100,
        messages=[{"role": "user", "content": "Responde solo: conexión OK"}],
    )
    print(respuesta.content[0].text)
