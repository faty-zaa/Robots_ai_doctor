import ollama


class LLMError(RuntimeError):
    """Raised with a user-friendly message when Ollama fails."""


class LLMClient:
    def __init__(
        self,
        text_model: str = "gemma3:1b",
        vision_model: str = "moondream",
    ) -> None:
        self.text_model = text_model
        self.vision_model = vision_model

    def _chat(self, model: str, message: dict, max_tokens: int) -> str:
        try:
            response = ollama.chat(
                model=model,
                messages=[message],
                options={"num_predict": max_tokens, "temperature": 0.2},
            )
        except ollama.ResponseError as exc:
            if getattr(exc, "status_code", None) == 404:
                raise LLMError(
                    f"Model '{model}' is not installed. Run: ollama pull {model}"
                ) from exc
            raise LLMError(f"Ollama error: {exc}") from exc
        except ConnectionError as exc:
            raise LLMError(
                "Cannot reach Ollama. Make sure it is running (ollama serve)."
            ) from exc
        except Exception as exc:
            raise LLMError(f"Unexpected LLM error: {exc}") from exc

        return response["message"]["content"].strip()

    def generate(self, prompt: str) -> str:
        """Text-only generation with the main model."""
        return self._chat(
            self.text_model,
            {"role": "user", "content": prompt},
            max_tokens=260,
        )

    def describe_image(self, image_path: str) -> str:
        """Turn a photo into a short text description using a vision model."""
        prompt = (
            "Describe this photo of a robot or robot hardware in 2-3 sentences. "
            "Mention visible damage, loose or disconnected wires, burn marks, "
            "debris, bent parts, LEDs, screens, and any readable error text. "
            "Describe only what you see; do not guess causes."
        )
        return self._chat(
            self.vision_model,
            {"role": "user", "content": prompt, "images": [image_path]},
            max_tokens=160,
        )