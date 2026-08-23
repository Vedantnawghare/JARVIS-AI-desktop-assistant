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
        silence_duration=0.55,
        max_duration=12.0,
        speech_threshold=0.5,
    ):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.silence_duration = silence_duration
        self.max_duration = max_duration
        self.speech_threshold = speech_threshold

        self.vad = load_silero_vad()
        self.vad.reset_states()

    def listen(self) -> np.ndarray:
        print("🎤 Listening...")

        chunks = []

        speech_started = False
        silence_start = None

        start_time = time.perf_counter()
        speech_start_time = None

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=self.block_size,
        ) as stream:

            while True:
                audio, _ = stream.read(
                    self.block_size
                )

                chunk = audio[:, 0].copy()
                chunks.append(chunk)

                waveform = torch.from_numpy(
                    chunk
                )

                speech_probability = self.vad(
                    waveform,
                    self.sample_rate,
                ).item()

                now = time.perf_counter()

                if (
                    speech_probability
                    >= self.speech_threshold
                ):
                    if not speech_started:
                        speech_started = True
                        speech_start_time = now

                        print(
                            "🗣️ Speech detected..."
                        )

                    silence_start = None

                elif speech_started:
                    if silence_start is None:
                        silence_start = now

                        print(
                            "🤫 Silence detected..."
                        )

                    elif (
                        now - silence_start
                        >= self.silence_duration
                    ):
                        total_time = (
                            now - start_time
                        )

                        silence_time = (
                            now - silence_start
                        )

                        speech_time = (
                            silence_start
                            - speech_start_time
                        )

                        print(
                            "🛑 Speech ended."
                        )

                        print(
                            f"Speech duration: "
                            f"{speech_time:.2f}s"
                        )

                        print(
                            f"End-silence wait: "
                            f"{silence_time:.2f}s"
                        )

                        print(
                            f"Total listener time: "
                            f"{total_time:.2f}s"
                        )

                        break

                if (
                    now - start_time
                    >= self.max_duration
                ):
                    print(
                        "⏱️ Maximum listening time reached."
                    )
                    break

        return np.concatenate(chunks)