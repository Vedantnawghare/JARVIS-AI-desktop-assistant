import sounddevice as sd
import torch
from kokoro import KPipeline


class KokoroTTS:
    def __init__(self, voice="bm_lewis", speed=1.12):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.voice = voice
        self.speed = speed

        self.pipeline = KPipeline(
            lang_code="a",
            device=self.device,
        )

    def speak(self, text: str) -> None:
        if not text or not text.strip():
            return

        generator = self.pipeline(
            text,
            voice=self.voice,
            speed=self.speed,
        )

        for _, _, audio in generator:
            sd.play(audio, 24000)
            sd.wait()

    def speak_sentence(self, sentence: str) -> None:
        if not sentence or not sentence.strip():
            return

        self.speak(sentence.strip())