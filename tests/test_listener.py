import soundfile as sf

from app.voice.listener import LiveListener


OUTPUT = "tests/audio/live_listener.wav"


def main():
    listener = LiveListener()

    audio = listener.listen()

    sf.write(
        OUTPUT,
        audio,
        16000,
    )

    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()