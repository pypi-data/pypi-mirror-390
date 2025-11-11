from abc import ABC
from dotenv import load_dotenv
import os
from HowdenLLM.providers.base_provider import BaseProvider

class OpenAIProvider(BaseProvider, ABC):
    provider = "openai"

    def __init__(self):
        import openai
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def complete(self, system: str, prompt: str, model: str) -> str:

        if model in ["gpt-5", "gpt-5-mini", "gpt-5-nano"]:
            response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=16000)
        else:
            raise Exception(f"Unsupported model: {model}")

        return response.choices[0].message.content
