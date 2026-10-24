
from src.Agent.agent import RoboDoctor


def main() -> None:
    doctor = RoboDoctor()
    print("RoboDoctor is ready! Type 'exit' to quit.")

    while True:
        problem = input("\nDescribe the robot problem: ")

        if problem.lower().strip() == "exit":
            break

        if not problem.strip():
            continue

        print("\nDiagnosing...")
        print(doctor.diagnose(problem))


if __name__ == "__main__":
    main()
