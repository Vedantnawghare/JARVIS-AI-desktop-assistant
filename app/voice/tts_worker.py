import re
import sys

from app.voice.kokoro_tts import KokoroTTS


def clean_for_speech(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = re.sub(r"[→←↑↓]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


tts = KokoroTTS()


def main():
    text = sys.stdin.read().strip()

    if not text:
        return

    text = text.replace("JARVIS", "Jarvis")
    text = text.replace("J.A.R.V.I.S.", "Jarvis")
    text = text.replace("J-A-R-V-I-S", "Jarvis")

    text = clean_for_speech(text)

    tts.speak(text)


if __name__ == "__main__":
    main()