import asyncio

import edge_tts


VOICE = "en-US-GuyNeural"
RATE = "+15%"


async def _speak(text: str) -> None:
    communicate = edge_tts.Communicate(
        text,
        VOICE,
        rate=RATE,
    )

    await communicate.save("tests/audio/tts_test.mp3")


def speak(text: str) -> None:
    asyncio.run(_speak(text))