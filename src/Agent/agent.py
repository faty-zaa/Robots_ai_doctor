import re

from src.RAG.retriever import Retriever
from src.llm.client import LLMClient, LLMError


def _normalize(words: set[str]) -> set[str]:
    return {w.rstrip("s") for w in words}


ROBOT_TERMS = _normalize({
    "robot", "robots", "robotics", "robotic", "drone", "turtlebot",
    "motor", "sensor", "wheel", "battery", "lidar", "ros", "ros2",
    "actuator", "gripper", "servo", "firmware", "odometry", "arm",
    "encoder", "chassis", "wiring", "esp32", "arduino", "raspberry",
})


class RoboDoctor:
    def __init__(self) -> None:
        self.retriever = Retriever()
        self.llm = LLMClient()

    @staticmethod
    def is_robot_problem(text: str) -> bool:
        words = _normalize(set(re.findall(r"[a-z0-9]+", text.lower())))
        return bool(words & ROBOT_TERMS)

    def _describe(self, paths: list[str], is_video: bool, notes: list[str]) -> str:
        descriptions = []
        for path in paths:
            try:
                text = self.llm.describe_image(path)
            except LLMError as exc:
                notes.append(f"⚠️ Visual analysis failed: {exc}")
                break  # same error would repeat for every frame
            if text:
                descriptions.append(text)

        if is_video and len(descriptions) > 1:
            return "\n".join(f"Frame {i}: {d}" for i, d in enumerate(descriptions, 1))
        return " ".join(descriptions)

    def diagnose(
        self,
        problem: str = "",
        image_path: str | None = None,
        image_paths: list[str] | None = None,
        is_video: bool = False,
    ) -> str:
        problem = (problem or "").strip()
        paths = list(image_paths or [])
        if image_path:
            paths.insert(0, image_path)

        notes: list[str] = []
        visual = self._describe(paths, is_video, notes) if paths else ""

        if not problem and not visual:
            return "\n".join(notes) or "Please describe the robot problem or attach a photo/video."

        if not visual and not self.is_robot_problem(problem):
            return (
                "I'm RoboDoctor, a robotics troubleshooting assistant. "
                "Please describe a problem with your robot."
            )

        query = f"{problem} {visual}".strip()
        evidence = self.retriever.search(query)
        context = "\n\n".join(
            f"Source: {item['source']}\n{item['content']}" for item in evidence
        ) or "No relevant documentation was found."

        if visual:
            label = (
                "Video frames in time order (auto-generated, may be inaccurate)"
                if is_video else
                "Photo description (auto-generated, may be inaccurate)"
            )
            visual_block = f"\n{label}:\n{visual}\n"
        else:
            visual_block = ""

        prompt = f"""You are RoboDoctor, a robotics troubleshooting assistant.

Problem reported by the user:
{problem or "(none given, see visual description)"}
{visual_block}
Documentation:
{context}

Give a concise diagnosis in English:
1. Three possible causes at most.
2. Three practical checks at most.
3. One recommended next action.

Use general robotics knowledge if documentation is missing.
Distinguish possibilities from confirmed facts.
Include safety precautions when needed.
Maximum 120 words."""

        answer = self.llm.generate(prompt)

        parts = notes[:]
        if visual:
            icon = "🎞️ Video seen as" if is_video else "📷 Photo seen as"
            parts.append(f"{icon}:\n{visual}")
        parts.append(answer)
        return "\n\n".join(parts)
