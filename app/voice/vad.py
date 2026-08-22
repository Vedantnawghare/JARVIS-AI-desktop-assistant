import torch
import soundfile as sf
from silero_vad import load_silero_vad, get_speech_timestamps


class VoiceActivityDetector:
    def __init__(self):
        self.model = load_silero_vad()

    def has_speech(self, audio_path: str) -> bool:
        audio, sample_rate = sf.read(audio_path, dtype="float32")

        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        waveform = torch.from_numpy(audio)

        speech = get_speech_timestamps(
            waveform,
            self.model,
            sampling_rate=sample_rate,
        )

        return len(speech) > 0