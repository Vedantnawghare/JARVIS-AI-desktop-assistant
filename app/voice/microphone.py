import sounddevice as sd
import soundfile as sf


SAMPLE_RATE = 16000
CHANNELS = 1


def record_audio(
    output_path: str,
    duration: float = 5.0,
) -> None:
    print("🎤 Speak now...")

    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
    )

    sd.wait()

    sf.write(
        output_path,
        recording,
        SAMPLE_RATE,
    )

    print("Recording saved.")