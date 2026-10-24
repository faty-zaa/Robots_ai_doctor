import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.Agent.agent import RoboDoctor
from src.llm.client import LLMError

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def ask_image() -> str | None:
    raw = input("Photo path (Enter to skip): ").strip().strip("'\"")
    if not raw:
        return None
    path = Path(raw).expanduser()
    if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
        print("  ⚠️ Not an image file, ignoring it.")
        return None
    return str(path)


def main() -> None:
    doctor = RoboDoctor()
    print("🤖 RoboDoctor  (type 'q' to quit)")

    while True:
        print()
        problem = input("Describe the problem: ").strip()
        if problem.lower() in {"q", "quit", "exit"}:
            break

        image_path = ask_image()
        print("\n🩺 Diagnosing…\n")

        try:
            print(doctor.diagnose(problem, image_path=image_path))
        except LLMError as exc:
            print(f"❌ {exc}")
        except Exception as exc:
            print(f"❌ Something went wrong: {exc}")


if __name__ == "__main__":
    main()