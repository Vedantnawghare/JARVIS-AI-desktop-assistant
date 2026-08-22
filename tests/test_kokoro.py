from app.voice.kokoro_tts import KokoroTTS


def main():
    print("JARVIS is speaking...")

    tts = KokoroTTS()

    tts.speak(
        "Good evening. I am Jarvis. "
        "How may I assist you?"
    )

    print("Done.")


if __name__ == "__main__":
    main()