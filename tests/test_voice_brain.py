from app.brain.llm import ask
from app.voice.microphone import record_audio
from app.voice.stt import transcribe
from app.voice.kokoro_tts import KokoroTTS


AUDIO_FILE = "tests/audio/live_test.wav"


def main():
    tts = KokoroTTS()

    record_audio(AUDIO_FILE, duration=5)

    print("Transcribing...")
    text = transcribe(AUDIO_FILE)

    print(f"\nYou: {text}")

    print("\nThinking...")
    response = ask(text)

    print(f"\nJARVIS: {response}")

    print("\nSpeaking...")
    tts.speak(response)

    print("Done.")


if __name__ == "__main__":
    main()