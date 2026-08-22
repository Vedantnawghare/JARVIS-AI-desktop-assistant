from app.voice.microphone import record_audio
from app.voice.stt import transcribe


AUDIO_FILE = "tests/audio/live_test.wav"


def main():
    record_audio(AUDIO_FILE, duration=5)

    print("Transcribing...")
    text = transcribe(AUDIO_FILE)

    print(f"JARVIS heard: {text}")


if __name__ == "__main__":
    main()