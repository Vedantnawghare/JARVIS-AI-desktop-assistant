import time

from app.voice.stt import transcribe

AUDIO_FILE = "tests/audio/test_voice.wav"


def main():
    start = time.perf_counter()

    print("Transcribing...")
    text = transcribe(AUDIO_FILE)

    elapsed = time.perf_counter() - start

    print(f"Transcription: {text}")
    print(f"Time: {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()