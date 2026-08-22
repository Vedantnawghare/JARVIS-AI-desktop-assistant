from app.voice.tts import speak


def main():
    speak(
        "Hello. I am Jarvis. "
        "Your local AI assistant is coming online."
    )

    print("Speech generated.")


if __name__ == "__main__":
    main()