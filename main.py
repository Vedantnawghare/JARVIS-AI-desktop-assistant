from app.brain.llm import ask


def main():
    print("JARVIS is online.")
    response = ask("In one sentence, explain what an AI agent is.")
    print(f"JARVIS: {response}")


if __name__ == "__main__":
    main()