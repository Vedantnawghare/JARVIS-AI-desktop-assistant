import torch
import soundfile as sf
from speechbrain.inference.speaker import SpeakerRecognition
from speechbrain.utils.fetching import LocalStrategy


class SpeakerVerifier:
    def __init__(self):
        self.verifier = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="models/speaker",
            run_opts={"device": "cuda:0"},
            local_strategy=LocalStrategy.COPY,
        )

    def _load_audio(self, path: str):
        audio, sample_rate = sf.read(path, dtype="float32")

        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        waveform = torch.from_numpy(audio).unsqueeze(0)

        return waveform, sample_rate

    def verify(self, reference_audio: str, test_audio: str) -> bool:
        reference, reference_sr = self._load_audio(reference_audio)
        test, test_sr = self._load_audio(test_audio)

        score, prediction = self.verifier.verify_batch(
            reference,
            test,
        )

        score = float(score.squeeze())
        prediction = bool(prediction.squeeze())

        print(f"Speaker score: {score:.4f}")
        print(f"Prediction: {prediction}")

        return prediction