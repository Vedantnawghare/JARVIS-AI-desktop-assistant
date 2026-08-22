from app.voice.speaker import SpeakerVerifier
from app.voice.microphone import record_audio


REFERENCE = "tests/audio/reference_voice.wav"
TEST = "tests/audio/speaker_test.wav"


def main():
    print("🎤 Record your reference voice")
    record_audio(REFERENCE, duration=5)

    print("\n🎤 Record your test voice")
    record_audio(TEST, duration=5)

    print("\n🔐 Checking speaker...")
    verifier = SpeakerVerifier()

    authorized = verifier.verify(
        REFERENCE,
        TEST,
    )

    if authorized:
        print("✅ Speaker verified.")
    else:
        print("❌ Speaker rejected.")


if __name__ == "__main__":
    main()