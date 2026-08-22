import time

import numpy as np
import sounddevice as sd
import torch
from silero_vad import load_silero_vad


class LiveListener:
    def __init__(
        self,
        sample_rate=16000,
        block_size=512,
        silence_duration=1.0,
        max_duration=15.0,
    ):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.silence_duration = silence_duration
        self.max_duration = max_duration

        self.vad = load_silero_vad()
        self.vad.reset_states()

    def listen(self) -> np.ndarray:
        print("🎤 Listening...")

        chunks = []
        speech_started = False
        silence_start = None
        start_time = time.time()

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=self.block_size,
        ) as stream:

            while True:
                audio, _ = stream.read(self.block_size)
                chunk = audio[:, 0].copy()

                chunks.append(chunk)

                waveform = torch.from_numpy(chunk)

                speech_probability = self.vad(
                    waveform,
                    self.sample_rate,
                ).item()

                if speech_probability >= 0.5:
                    if not speech_started:
                        speech_started = True
                        print("🗣️ Speech detected...")

                    silence_start = None

                elif speech_started:
                    if silence_start is None:
                        silence_start = time.time()

                    elif time.time() - silence_start >= self.silence_duration:
                        print("🛑 Speech ended.")
                        break

                if time.time() - start_time >= self.max_duration:
                    print("⏱️ Maximum listening time reached.")
                    break

        return np.concatenate(chunks)