
from src.RAG.retriever import Retriever
from src.llm.client import LLMClient


class RoboDoctor:
    def __init__(self) -> None:
        self.retriever = Retriever()
        self.llm = LLMClient()

    def diagnose(self, problem: str) -> str:
        evidence = self.retriever.search(problem)

        if not evidence:
            return "No relevant information found in the documentation."

        context = "\n\n".join(
            item["content"] for item in evidence
        )

        prompt = f"""
You are RoboDoctor, a robotics troubleshooting assistant.

Use the documentation below as evidence.
Do not invent technical facts.
If the evidence is insufficient, say so.
Suggest safe checks and explain the likely causes.

Robot problem:
{problem}

Documentation:
{context}
"""
        return self.llm.generate(prompt)
