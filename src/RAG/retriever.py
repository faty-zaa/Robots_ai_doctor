import re
from pathlib import Path

STOPWORDS = {
    "the", "is", "a", "an", "my", "it", "by", "and", "of", "to", "in", "on",
    "at", "for", "with", "does", "do", "not", "doesnt", "dont", "this", "that",
    "i", "me", "but", "or", "are", "was", "be", "have", "has", "when", "so",
}


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


class Retriever:
    def __init__(self, data_dir: str | Path | None = None) -> None:
        self.data_dir = (
            Path(data_dir)
            if data_dir is not None
            else Path(__file__).resolve().parents[2] / "robodoctor_docs" / "data"
        )
        self.chunks: list[dict] = []
        self.load_documents()

    def load_documents(self) -> None:
        for path in self.data_dir.glob("*.md"):
            content = path.read_text(encoding="utf-8")

            for section in content.split("\n## "):
                section = section.strip()
                if section:
                    self.chunks.append({
                        "source": path.name,
                        "content": section,
                        "tokens": tokenize(section),  # computed once, not per query
                    })

    def search(self, query: str, k: int = 3) -> list[dict[str, str]]:
        words = tokenize(query) - STOPWORDS
        if not words:
            return []

        scored = [(len(words & chunk["tokens"]), chunk) for chunk in self.chunks]
        scored = [(score, chunk) for score, chunk in scored if score > 0]
        scored.sort(key=lambda item: item[0], reverse=True)

        return [
            {"source": chunk["source"], "content": chunk["content"]}
            for _, chunk in scored[:k]
        ]