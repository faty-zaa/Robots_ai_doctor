
import ollama


class LLMClient:
    def __init__(self, model: str = "gemma3:1b") -> None:       
        self.model = model

    def generate(self, prompt: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={
            "num_predict": 180,
            "temperature": 0.2,
        },
        )
        return response["message"]["content"]
