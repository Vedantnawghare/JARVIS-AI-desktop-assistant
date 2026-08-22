from app.voice.kokoro_tts import KokoroTTS


def main():
    text = (
        "Good evening. I am Jarvis. "
        "How may I assist you today?"
    )

    voices = [
        ("bm_george", "George"),
        ("bm_lewis", "Lewis"),
        ("bm_daniel", "Daniel"),
    ]

    for voice, name in voices:
        print(f"Generating {name}...")
        tts = KokoroTTS(voice=voice, speed=1.12)
        tts.speak(text)

        input(f"Press Enter after listening to {name}...")


if __name__ == "__main__":
    main()