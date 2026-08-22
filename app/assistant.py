import re
import time
import soundfile as sf

from app.voice.kokoro_tts import KokoroTTS
from app.voice.listener import LiveListener
from app.voice.stt import transcribe
from app.voice.speaker import SpeakerVerifier

from app.brain.agent import decide
from app.brain.llm import stream

from app.browser.manager import BrowserManager
from app.browser.browser import BrowserTools
from app.tools.registry import ToolRegistry
from app.tools.system import open_application, open_path
from app.tools.desktop import type_text, press_key, hotkey


WAKE_AUDIO = "tests/audio/wake_word.wav"
COMMAND_AUDIO = "tests/audio/command.wav"
REFERENCE_AUDIO = "tests/audio/reference_voice.wav"


class Jarvis:
    def __init__(self):
        print("Loading speaker verification...")
        self.speaker = SpeakerVerifier()
        print("Speaker verification ready.")

        self.listener = LiveListener()

        self.browser = None
        self.browser_tools = None

        self.registry = ToolRegistry()

        self.registry.register(
            "open_application",
            open_application,
        )
        self.registry.register(
            "open_path",
            open_path,
        )
        self.registry.register(
            "type_text",
            type_text,
        )
        self.registry.register(
            "press_key",
            press_key,
        )
        self.registry.register(
            "hotkey",
            hotkey,
        )

        print("Loading Kokoro...")
        self.tts = KokoroTTS(
            voice="bm_lewis",
            speed=1.12,
        )
        print("Kokoro ready.")

        self.running = True

    def start_browser(self):
        if self.browser is not None:
            return

        print("Starting browser...")

        self.browser = BrowserManager()
        self.browser.start()

        self.browser_tools = BrowserTools(
            self.browser
        )

        self.registry.register(
            "open_url",
            self.browser_tools.open_url,
        )
        self.registry.register(
            "search_youtube",
            self.browser_tools.search_youtube,
        )
        self.registry.register(
            "web_search",
            self.browser_tools.web_search,
        )

        print("Browser tools ready.")

    def normalize_wake_text(self, text):
        text = text.lower().strip()
        text = re.sub(r"[\.\-_]+", "", text)
        text = re.sub(r"\s+", " ", text)

        replacements = {
            "hirvs": "jarvis",
            "hervs": "jarvis",
            "jervis": "jarvis",
            "jarv": "jarvis",
        }

        words = text.split()

        return " ".join(
            replacements.get(word, word)
            for word in words
        )

    def contains_wake_word(self, text):
        normalized = self.normalize_wake_text(text)

        if "jarvis" in normalized:
            return True

        compact = re.sub(
            r"[^a-z]",
            "",
            normalized,
        )

        return "jarvis" in compact

    def wait_for_wake_word(self):
        print("\nJARVIS is waiting...")

        while self.running:
            audio = self.listener.listen()

            sf.write(
                WAKE_AUDIO,
                audio,
                16000,
            )

            text = transcribe(WAKE_AUDIO)

            print(f"Heard: {text}")

            if self.contains_wake_word(text):
                print("Wake word detected!")
                return True

        return False

    def listen_for_command(self):
        print("Listening for command...")

        audio = self.listener.listen()

        sf.write(
            COMMAND_AUDIO,
            audio,
            16000,
        )

        return audio

    def verify_speaker(self, audio):
        print("Verifying speaker...")

        sf.write(
            COMMAND_AUDIO,
            audio,
            16000,
        )

        return self.speaker.verify(
            REFERENCE_AUDIO,
            COMMAND_AUDIO,
        )

    def is_exit_command(self, text):
        text = text.lower().strip()

        text = re.sub(
            r"[^\w\s]",
            " ",
            text,
        )
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        exit_phrases = {
            "shutdown",
            "shut down",
            "exit",
            "quit",
            "stop",
            "stop jarvis",
            "jarvis stop",
            "stop yourself",
            "goodbye",
            "goodbye jarvis",
            "bye",
            "bye jarvis",
        }

        return (
            text in exit_phrases
            or text.startswith("jarvis stop")
            or text.startswith("stop jarvis")
            or text.startswith("shutdown")
            or text.startswith("shut down")
        )

    def run_tool_plan(self, steps):
        results = []

        browser_tools = {
            "open_url",
            "search_youtube",
            "web_search",
        }

        for index, step in enumerate(
            steps,
            start=1,
        ):
            tool_name = step["tool"]
            arguments = step.get(
                "arguments",
                {},
            )

            if tool_name in browser_tools:
                self.start_browser()

            print(
                f"Step {index}: {tool_name}"
            )

            result = self.registry.execute(
                tool_name,
                **arguments,
            )

            print(
                f"Result: {result}"
            )

            results.append(
                f"{tool_name}: {result}"
            )

        return "\n".join(results)

    def process_command(self, text):
        start = time.perf_counter()

        print("\nAgent thinking...")

        decision = decide(text)

        print(
            f"Decision: {decision}"
        )

        print(
            f"Agent decision time: "
            f"{time.perf_counter() - start:.2f}s"
        )

        if decision["action"] == "respond":
            return {
                "type": "response",
                "content": decision["response"],
            }

        if decision["action"] != "plan":
            return {
                "type": "response",
                "content": (
                    "I could not understand "
                    "what action to take."
                ),
            }

        results = self.run_tool_plan(
            decision["steps"]
        )

        synthesis_prompt = f"""
You are JARVIS, a desktop AI assistant.

The user asked:
{text}

The following actions were performed:
{results}

Give a concise confirmation of what was done.

Rules:
- Do not invent actions that were not performed.
- Keep it natural for voice.
- No Markdown.
- No tables.
- No emojis.
"""

        return {
            "type": "stream",
            "content": synthesis_prompt,
        }

    def clean_for_speech(self, text):
        text = re.sub(
            r"```.*?```",
            " ",
            text,
            flags=re.DOTALL,
        )
        text = re.sub(
            r"`([^`]*)`",
            r"\1",
            text,
        )
        text = re.sub(
            r"\*\*(.*?)\*\*",
            r"\1",
            text,
        )
        text = re.sub(
            r"\*(.*?)\*",
            r"\1",
            text,
        )
        text = re.sub(
            r"__(.*?)__",
            r"\1",
            text,
        )
        text = re.sub(
            r"_(.*?)_",
            r"\1",
            text,
        )
        text = re.sub(
            r"^#{1,6}\s*",
            "",
            text,
            flags=re.MULTILINE,
        )
        text = re.sub(
            r"^\s*[-*+]\s+",
            "",
            text,
            flags=re.MULTILINE,
        )
        text = re.sub(
            r"^\s*\d+\.\s+",
            "",
            text,
            flags=re.MULTILINE,
        )
        text = re.sub(
            r"\[(.*?)\]\(.*?\)",
            r"\1",
            text,
        )
        text = re.sub(
            r"[→←↑↓]",
            " ",
            text,
        )
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        text = text.replace(
            "J.A.R.V.I.S.",
            "Jarvis",
        )
        text = text.replace(
            "J-A-R-V-I-S",
            "Jarvis",
        )
        text = text.replace(
            "JARVIS",
            "Jarvis",
        )

        return text.strip()

    def speak_stream(self, prompt):
        print("\nJARVIS: ", end="", flush=True)

        buffer = ""

        for chunk in stream(prompt):
            print(
                chunk,
                end="",
                flush=True,
            )

            buffer += chunk

            sentences = re.split(
                r"(?<=[.!?])\s+",
                buffer,
            )

            if len(sentences) > 1:
                complete = sentences[:-1]
                buffer = sentences[-1]

                for sentence in complete:
                    sentence = self.clean_for_speech(
                        sentence
                    )

                    if sentence:
                        self.tts.speak_sentence(
                            sentence
                        )

        if buffer.strip():
            sentence = self.clean_for_speech(
                buffer
            )

            if sentence:
                self.tts.speak_sentence(
                    sentence
                )

        print()

    def handle_command(self, text):
        if self.is_exit_command(text):
            print(
                "Shutting down JARVIS..."
            )
            self.running = False
            return

        result = self.process_command(text)

        if result["type"] == "response":
            response = result["content"]

            print(
                f"\nJARVIS: {response}"
            )

            self.tts.speak(
                self.clean_for_speech(
                    response
                )
            )

        elif result["type"] == "stream":
            self.speak_stream(
                result["content"]
            )

    def run_once(self):
        try:
            detected = self.wait_for_wake_word()

            if not detected:
                return

            print(
                "\nJARVIS activated."
            )
            print(
                "You can now speak commands directly."
            )

            while self.running:
                audio = self.listen_for_command()

                if not self.verify_speaker(
                    audio
                ):
                    print(
                        "Speaker rejected."
                    )
                    continue

                text = transcribe(
                    COMMAND_AUDIO
                )

                if not text.strip():
                    print(
                        "No command detected."
                    )
                    continue

                print(
                    f"\nYou: {text}"
                )

                self.handle_command(
                    text
                )

        except KeyboardInterrupt:
            print(
                "\nStopping JARVIS..."
            )

        finally:
            self.running = False

            if self.browser is not None:
                self.browser.close()

            print(
                "\nJARVIS stopped."
            )


if __name__ == "__main__":
    Jarvis().run_once()