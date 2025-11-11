from string import Template
from typing import Tuple
from dotenv import load_dotenv
from pathlib import Path
from HowdenLLM.providers.provider_factory import ProviderFactory

class LLM:
    def __init__(self,
                 provider_and_model: str,
                 template: Template,
                 system: str = None,
                 name: str = None):
        load_dotenv()
        self.provider_name = provider_and_model.split(":")[0].lower()
        self.model = provider_and_model.split(":")[1]
        self.template = template
        self.name: str = name
        self.system: str = system
        self.provider = ProviderFactory.create(self.provider_name)

        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_runs = 0

    def _count_tokens(self, text: str) -> int:
        """Try to count tokens with tiktoken; fallback to rough word count."""
        try:
            import tiktoken
            enc = tiktoken.encoding_for_model(self.model)
            return len(enc.encode(text))
        except (KeyError, LookupError, AttributeError, ImportError):
            return len(text.split())

    def __call__(self, filepath: Path) -> Tuple[str, int, int]:
        """
        Execute one completion round and return:
        (output_text, input_token_count, output_token_count)
        """
        content = filepath.read_text(encoding="utf-8")
        prompt = self.template.substitute(content=content)

        # --- count input tokens ---
        input_text = f"{self.system or ''}\n{prompt}"
        input_tokens = self._count_tokens(input_text)

        # --- run model ---
        output = self.provider.complete(self.system, prompt, self.model)

        # --- count output tokens ---
        output_tokens = self._count_tokens(output)

        # --- update totals ---
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_runs += 1
        print(f"[{self.name or 'LLM'}] "
              f"Input tokens: {input_tokens}, "
              f"Output tokens: {output_tokens}, "
              f"Total_input: {self.total_input_tokens}, "
              f"Total_output: {self.total_output_tokens}, "
              f"Total_input_average: {round(self.total_input_tokens / self.total_runs, 2)}, "
              f"Total_output_average: {round(self.total_output_tokens / self.total_runs, 2)}")

        return output
