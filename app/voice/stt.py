import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SITE_PACKAGES = PROJECT_ROOT / ".venv" / "Lib" / "site-packages"

CUDA_DLL_DIRS = [
    SITE_PACKAGES / "nvidia" / "cublas" / "bin",
    SITE_PACKAGES / "nvidia" / "cudnn" / "bin",
]

for dll_dir in CUDA_DLL_DIRS:
    if dll_dir.exists():
        os.add_dll_directory(str(dll_dir))
        os.environ["PATH"] = str(dll_dir) + os.pathsep + os.environ["PATH"]

from faster_whisper import WhisperModel


MODEL_SIZE = "small"

model = WhisperModel(
    MODEL_SIZE,
    device="cuda",
    compute_type="float16",
)


def transcribe(audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path)

    return " ".join(segment.text.strip() for segment in segments)