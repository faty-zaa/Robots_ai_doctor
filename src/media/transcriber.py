from faster_whisper import WhisperModel


class Transcriber:
    """Speech-to-text. The model loads on first use so the app starts fast."""

    def __init__(self, model_size: str = "tiny") -> None:
        # "tiny" is fastest; try "base" or "small" if transcripts are inaccurate.
        self.model_size = model_size
        self._model: WhisperModel | None = None

    def transcribe(self, audio_path: str) -> str:
        if self._model is None:
            self._model = WhisperModel(
                self.model_size, device="cpu", compute_type="int8"
            )

        segments, _ = self._model.transcribe(
            audio_path, beam_size=1, vad_filter=True
        )
        # `segments` is a lazy generator, so it must be consumed here.
        return " ".join(s.text.strip() for s in segments).strip()