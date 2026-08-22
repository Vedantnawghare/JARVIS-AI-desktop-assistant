from app.voice.listener import LiveListener
from app.voice.stt import transcribe
import soundfile as sf


AUDIO_FILE = "tests/audio/wake_word.wav"


def main():
    listener = LiveListener()

    print('Say "Jarvis" followed by anything...')
    audio = listener.listen()

    sf.write(
        AUDIO_FILE,
        audio,
        16000,
    )

    print("Transcribing...")
    text = transcribe(AUDIO_FILE)

    print(f"Heard: {text}")

    if "jarvis" in text.lower():
        print("🔥 Wake word detected!")
    else:
        print("❌ Wake word not detected.")


if __name__ == "__main__":
    main()