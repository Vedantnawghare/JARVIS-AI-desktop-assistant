import re
import time

import soundfile as sf

from app.voice.kokoro_tts import KokoroTTS
from app.voice.listener import LiveListener
from app.voice.stt import transcribe
from app.voice.speaker import SpeakerVerifier

from app.brain.agent import decide, recover

from app.tools.registry import ToolRegistry

from app.tools.system import (
    open_application,
    open_path,
    close_application,
    volume_up,
    volume_down,
    mute,
    unmute,
    lock_pc,
)

from app.tools.desktop import (
    type_text,
    press_key,
    hotkey,
)

from app.tools.mouse import (
    click,
    double_click,
    move_mouse,
    scroll,
)

from app.tools.screen import screenshot

from app.tools.window import (
    focus_window,
    minimize_window,
    maximize_window,
)

from app.tools.ui import (
    find_ui_element,
    click_ui_element,
    type_into_ui_element,
    read_ui_element,
)

from app.tools.memory import (
    remember,
    recall,
    forget,
)


WAKE_AUDIO = "tests/audio/wake_word.wav"
COMMAND_AUDIO = "tests/audio/command.wav"
REFERENCE_AUDIO = "tests/audio/reference_voice.wav"


class Jarvis:

    def __init__(self):

        print("Loading speaker verification...")

        self.speaker = SpeakerVerifier()

        print("Speaker verification ready.")

        self.listener = LiveListener()

        self.registry = ToolRegistry()

        self.registry.register(
            "open_application",
            open_application,
        )

        self.registry.register(
            "close_application",
            close_application,
        )

        self.registry.register(
            "open_path",
            open_path,
        )

        self.registry.register(
            "focus_window",
            focus_window,
        )

        self.registry.register(
            "minimize_window",
            minimize_window,
        )

        self.registry.register(
            "maximize_window",
            maximize_window,
        )

        self.registry.register(
            "volume_up",
            volume_up,
        )

        self.registry.register(
            "volume_down",
            volume_down,
        )

        self.registry.register(
            "mute",
            mute,
        )

        self.registry.register(
            "unmute",
            unmute,
        )

        self.registry.register(
            "lock_pc",
            lock_pc,
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

        self.registry.register(
            "click",
            click,
        )

        self.registry.register(
            "double_click",
            double_click,
        )

        self.registry.register(
            "move_mouse",
            move_mouse,
        )

        self.registry.register(
            "scroll",
            scroll,
        )

        self.registry.register(
            "screenshot",
            screenshot,
        )

        self.registry.register(
            "find_ui_element",
            find_ui_element,
        )

        self.registry.register(
            "click_ui_element",
            click_ui_element,
        )

        self.registry.register(
            "type_into_ui_element",
            type_into_ui_element,
        )

        self.registry.register(
            "read_ui_element",
            read_ui_element,
        )

        self.registry.register(
            "remember",
            remember,
        )

        self.registry.register(
            "recall",
            recall,
        )

        self.registry.register(
            "forget",
            forget,
        )

        print("Loading Kokoro...")

        self.tts = KokoroTTS(
            voice="bm_lewis",
            speed=1.12,
        )

        print("Kokoro ready.")

        self.running = True
        self.active = False
        self.context = []

        self.max_recovery_attempts = 2

    def normalize_text(self, text):

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

        return text

    def normalize_wake_text(self, text):

        text = self.normalize_text(text)

        replacements = {
            "hirvs": "jarvis",
            "hervs": "jarvis",
            "jervis": "jarvis",
            "jarv": "jarvis",
            "jairvis": "jarvis",
            "jairus": "jarvis",
            "jairvs": "jarvis",
        }

        return " ".join(
            replacements.get(
                word,
                word,
            )
            for word in text.split()
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

    def is_shutdown_command(self, text):

        normalized = self.normalize_text(text)

        return (
            normalized in {
                "shutdown",
                "shut down",
                "exit",
                "quit",
                "jarvis shutdown",
                "jarvis shut down",
                "jarvis exit",
                "jarvis quit",
            }
            or normalized.startswith(
                "jarvis shutdown"
            )
            or normalized.startswith(
                "jarvis shut down"
            )
        )

    def record_audio(self, path):

        audio = self.listener.listen()

        sf.write(
            path,
            audio,
            16000,
        )

        return audio

    def authenticate_audio(self, audio):

        print("Authenticating speaker...")

        sf.write(
            COMMAND_AUDIO,
            audio,
            16000,
        )

        authorized = self.speaker.verify(
            REFERENCE_AUDIO,
            COMMAND_AUDIO,
        )

        if authorized:
            print(
                "Speaker authenticated."
            )
        else:
            print(
                "Speaker rejected."
            )

        return authorized

    def wait_for_activation(self):

        print(
            "\nJARVIS is idle. "
            "Say 'Hey Jarvis'..."
        )

        while self.running:

            audio = self.record_audio(
                WAKE_AUDIO
            )

            text = transcribe(
                WAKE_AUDIO
            )

            print(
                f"Heard: {text}"
            )

            if not self.contains_wake_word(
                text
            ):
                continue

            print(
                "Wake word detected!"
            )

            if not self.authenticate_audio(
                audio
            ):
                continue

            self.active = True

            print(
                "\nJARVIS ACTIVE"
            )

            self.tts.speak(
                "Yes?"
            )

            return True

        return False

    def listen_for_authenticated_command(
        self
    ):

        print(
            "Listening..."
        )

        audio = self.record_audio(
            COMMAND_AUDIO
        )

        text = transcribe(
            COMMAND_AUDIO
        )

        return audio, text

    def needs_reauthentication(
        self,
        decision,
    ):

        high_risk_tools = {
            "delete_file",
            "delete_path",
            "send_message",
            "send_email",
            "run_command",
            "shutdown_computer",
            "restart_computer",
            "lock_pc",
        }

        if (
            decision.get("action")
            != "plan"
        ):
            return False

        return any(
            step.get("tool")
            in high_risk_tools
            for step in decision.get(
                "steps",
                [],
            )
        )

    def execute_step(
        self,
        tool_name,
        arguments,
    ):

        print(
            f"Executing: {tool_name}"
        )

        return self.registry.execute(
            tool_name,
            **arguments,
        )

    def execute_plan(
        self,
        steps,
        user_text,
    ):

        results = []

        recovery_count = 0

        current_steps = steps

        while True:

            failed = False

            for index, step in enumerate(
                current_steps,
                start=1,
            ):

                tool_name = step["tool"]

                arguments = step.get(
                    "arguments",
                    {},
                )

                print(
                    f"Step {index}: "
                    f"{tool_name}"
                )

                try:

                    tool_start = (
                        time.perf_counter()
                    )

                    result = (
                        self.execute_step(
                            tool_name,
                            arguments,
                        )
                    )

                    elapsed = (
                        time.perf_counter()
                        - tool_start
                    )

                    print(
                        "Tool execution time: "
                        f"{elapsed:.2f}s"
                    )

                    print(
                        f"Result: {result}"
                    )

                    results.append(
                        f"{tool_name}: "
                        f"{result}"
                    )

                    if (
                        tool_name
                        == "press_key"
                        and str(
                            arguments.get(
                                "key",
                                "",
                            )
                        ).lower()
                        == "enter"
                    ):

                        time.sleep(
                            1.5
                        )

                except Exception as exc:

                    failed = True

                    print(
                        f"Tool failed: "
                        f"{tool_name}"
                    )

                    print(
                        f"Error: {exc}"
                    )

                    if (
                        recovery_count
                        >= self.max_recovery_attempts
                    ):

                        return {
                            "success": False,
                            "results": results,
                            "error": str(exc),
                        }

                    recovery_count += 1

                    recovery_plan = recover(
                        user_text,
                        tool_name,
                        str(exc),
                    )

                    print(
                        "Recovery plan:",
                        recovery_plan,
                    )

                    if (
                        recovery_plan.get(
                            "action"
                        )
                        == "respond"
                    ):

                        return {
                            "success": False,
                            "results": results,
                            "error": (
                                recovery_plan.get(
                                    "response",
                                    "Recovery failed.",
                                )
                            ),
                        }

                    current_steps = (
                        recovery_plan.get(
                            "steps",
                            [],
                        )
                    )

                    break

            if not failed:

                return {
                    "success": True,
                    "results": results,
                    "error": None,
                }

    def add_context(
        self,
        role,
        content,
    ):

        self.context.append(
            {
                "role": role,
                "content": content,
            }
        )

        self.context = self.context[-8:]

    def process_command(
        self,
        text,
    ):

        start = time.perf_counter()

        context_for_agent = (
            self.context.copy()
        )

        context_for_agent.append(
            {
                "role": "system",
                "content": (
                    "Use the currently visible "
                    "browser through UI automation. "
                    "Do not launch another browser "
                    "for navigation or search."
                ),
            }
        )

        print(
            "\nAgent thinking..."
        )

        decision = decide(
            text,
            context_for_agent,
        )

        print(
            f"Decision: {decision}"
        )

        print(
            "Agent decision time: "
            f"{time.perf_counter() - start:.2f}s"
        )

        self.add_context(
            "user",
            text,
        )

        if (
            decision.get("action")
            == "respond"
        ):

            response = decision.get(
                "response",
                "",
            )

            self.add_context(
                "assistant",
                response,
            )

            return {
                "type": "response",
                "content": response,
            }

        if (
            decision.get("action")
            != "plan"
        ):

            response = (
                "I could not understand "
                "what action to take."
            )

            self.add_context(
                "assistant",
                response,
            )

            return {
                "type": "response",
                "content": response,
            }

        if self.needs_reauthentication(
            decision
        ):

            print(
                "High-risk action detected."
            )

            audio = self.record_audio(
                COMMAND_AUDIO
            )

            if not self.authenticate_audio(
                audio
            ):

                response = (
                    "Speaker verification "
                    "failed."
                )

                self.add_context(
                    "assistant",
                    response,
                )

                return {
                    "type": "response",
                    "content": response,
                }

        execution = self.execute_plan(
            decision["steps"],
            text,
        )

        if not execution["success"]:

            response = execution[
                "error"
            ]

            self.add_context(
                "assistant",
                response,
            )

            return {
                "type": "response",
                "content": response,
            }

        results = execution[
            "results"
        ]

        results_text = "\n".join(
            results
        )

        self.add_context(
            "assistant",
            results_text,
        )

        response = (
            self.direct_confirmation(
                results
            )
        )

        self.add_context(
            "assistant",
            response,
        )

        return {
            "type": "direct",
            "content": response,
        }

    def direct_confirmation(
        self,
        results,
    ):

        if not results:
            return "Done."

        if len(results) == 1:

            result = str(
                results[0]
            )

            prefixes = (
                "Opened and focused ",
                "Opened ",
                "Closed application: ",
                "Focused window: ",
                "Minimized window: ",
                "Maximized window: ",
                "Typed: ",
                "Pressed: ",
                "Clicked at ",
                "Double-clicked at ",
                "Moved mouse to ",
                "Scrolled ",
                "Found ",
                "Clicked ",
                "Typed ",
                "I'll remember",
                "is ",
                "I forgot ",
                "Volume increased",
                "Volume decreased",
                "Volume muted",
                "Volume unmuted",
                "PC locked",
            )

            for prefix in prefixes:

                if result.startswith(
                    prefix
                ):
                    return result

            return result

        return "Done."

    def clean_for_speech(
        self,
        text,
    ):

        text = re.sub(
            r"<think>.*?</think>",
            " ",
            text,
            flags=re.DOTALL,
        )

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

    def speak_stream(
        self,
        prompt,
    ):

        print(
            "\nJARVIS: ",
            end="",
            flush=True,
        )

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

                complete = (
                    sentences[:-1]
                )

                buffer = sentences[-1]

                for sentence in complete:

                    sentence = (
                        self.clean_for_speech(
                            sentence
                        )
                    )

                    if sentence:
                        self.tts.speak_sentence(
                            sentence
                        )

        if buffer.strip():

            sentence = (
                self.clean_for_speech(
                    buffer
                )
            )

            if sentence:
                self.tts.speak_sentence(
                    sentence
                )

        print()

    def shutdown(self):

        message = (
            "Bye-bye, sir. "
            "Shutting down Jarvis."
        )

        print(
            f"\nJARVIS: {message}"
        )

        self.tts.speak(
            message
        )

        self.running = False
        self.active = False

    def handle_command(
        self,
        text,
    ):

        result = self.process_command(
            text
        )

        if (
            result["type"]
            == "response"
        ):

            response = result[
                "content"
            ]

            print(
                f"\nJARVIS: {response}"
            )

            self.tts.speak(
                self.clean_for_speech(
                    response
                )
            )

        elif (
            result["type"]
            == "direct"
        ):

            response = (
                self.clean_for_speech(
                    result["content"]
                )
            )

            print(
                f"\nJARVIS: {response}"
            )

            self.tts.speak(
                response
            )

        elif (
            result["type"]
            == "stream"
        ):

            self.speak_stream(
                result["content"]
            )

    def run(self):

        try:

            if not self.wait_for_activation():
                return

            while (
                self.running
                and self.active
            ):

                audio, text = (
                    self.listen_for_authenticated_command()
                )

                if not text.strip():
                    continue

                print(
                    f"\nYou: {text}"
                )

                if not self.authenticate_audio(
                    audio
                ):
                    print(
                        "Command rejected."
                    )
                    continue

                if self.is_shutdown_command(
                    text
                ):
                    self.shutdown()
                    break

                self.handle_command(
                    text
                )

        except KeyboardInterrupt:

            print(
                "\nStopping JARVIS..."
            )

        finally:

            self.running = False
            self.active = False

            print(
                "\nJARVIS stopped."
            )


if __name__ == "__main__":

    jarvis = Jarvis()

    jarvis.run()