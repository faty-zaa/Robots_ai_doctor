
import re

from src.RAG.retriever import Retriever
from src.llm.client import LLMClient


class RoboDoctor:
    def __init__(self) -> None:
        self.retriever = Retriever()
        self.llm = LLMClient()

    def is_robot_problem(self, problem: str) -> bool:
        text = problem.lower()

        robot_terms = {
            "robot", "robotics", "drone", "turtlebot",
            "motor", "sensor", "wheel", "battery", "lidar",
            "ros", "ros2", "actuator", "gripper", "servo",
            "firmware", "odometry", "robotic arm",
        }

        problem_terms = {
            "turn on", "start", "move", "moving", "turn",
            "rotate", "spin", "stop", "stuck", "power",
            "connect", "connection", "detect", "follow",
            "navigate", "charge", "work", "respond",
            "error", "broken", "overheat", "vibrate",
        }

        words = set(re.findall(r"[a-z0-9]+", text))
        has_robot_term = bool(words & robot_terms)
        has_problem_term = any(term in text for term in problem_terms)

        return has_robot_term or has_problem_term

    def diagnose(self, problem: str) -> str:
        problem = problem.strip()

        if not problem:
            return "Please describe the robot problem."

        if not self.is_robot_problem(problem):
            return (
                "I'm RoboDoctor, a robotics troubleshooting "
                "assistant. Please describe a problem with your robot."
            )

        evidence = self.retriever.search(problem)
        context = "\n\n".join(
            f"Source: {item['source']}\n{item['content']}"
            for item in evidence
        ) or "No relevant documentation was found."

        prompt = f"""
You are RoboDoctor, a robotics troubleshooting assistant.

Problem: {problem}

Documentation:
{context}

Give a concise diagnosis in English:
1. Three possible causes at most.
2. Three practical checks at most.
3. One recommended next action.

Use general robotics knowledge if documentation is missing.
Distinguish possibilities from confirmed facts.
Include safety precautions when needed.
Maximum 120 words.
"""
        return self.llm.generate(prompt)
