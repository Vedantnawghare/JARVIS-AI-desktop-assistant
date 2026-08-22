from app.voice.microphone import record_audio
from app.voice.vad import VoiceActivityDetector


AUDIO_FILE = "tests/audio/vad_test.wav"


def main():
    print("🎤 Speak for a few seconds...")
    record_audio(AUDIO_FILE, duration=5)

    vad = VoiceActivityDetector()

    if vad.has_speech(AUDIO_FILE):
        print("✅ Speech detected.")
    else:
        print("❌ No speech detected.")


if __name__ == "__main__":
    main()