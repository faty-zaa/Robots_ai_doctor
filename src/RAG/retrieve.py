from pathlib import Path


class Retriever:
    def __init__(self, path: str = "data/robot_manual.md") -> None:
        self.path = Path(path)
        self.content = self.path.read_text(encoding="utf-8")
        self.chunks = [
            section.strip()
            for section in self.content.split("\n## ")
            if section.strip()
        ]

    def search(self, query: str) -> list[str]:
        words = set(query.lower().split())
        results = []

        for chunk in self.chunks:
            score = sum(
                word in chunk.lower()
                for word in words
            )
            if score:
                results.append((score, chunk))

        results.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in results[:3]]