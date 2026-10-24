from pathlib import Path
import re


class Retriever:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.chunks: list[dict[str, str]] = []
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
                    })

    def search(self, query: str) -> list[dict[str, str]]:
        words = set(re.findall(r"\b[a-z0-9]+\b", query.lower()))
        ignored = {"the", "is", "a", "an", "my", "it", "by", "and"}
        words -= ignored

        results = []

        for chunk in self.chunks:
            content = chunk["content"].lower()
            score = sum(
                word in set(re.findall(r"\b[a-z0-9]+\b", content))
                for word in words
            )

            if score > 0:
                results.append((score, chunk))

        results.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in results[:3]]