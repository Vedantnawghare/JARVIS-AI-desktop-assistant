import re
import time

import soundfile as sf

from app.voice.kokoro_tts import KokoroTTS
from app.voice.listener import LiveListener
from app.voice.stt import transcribe
from app.voice.speaker import SpeakerVerifier

from app.brain.agent import decide, recover
from app.brain.llm import stream

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

from app.tools.files import (
    open_file_explorer,
    open_file_or_folder,
    create_folder,
    create_file,
    copy_file_or_folder,
    move_file_or_folder,
    delete_file_or_folder,
)

from app.tools.power import (
    close_all_applications,
    shutdown_pc,
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

        self.registry.register(
            "open_file_explorer",
            open_file_explorer,
        )

        self.registry.register(
            "open_file_or_folder",
            open_file_or_folder,
        )

        self.registry.register(
            "create_folder",
            create_folder,
        )

        self.registry.register(
            "create_file",
            create_file,
        )

        self.registry.register(
            "copy_file_or_folder",
            copy_file_or_folder,
        )

        self.registry.register(
            "move_file_or_folder",
            move_file_or_folder,
        )

        self.registry.register(
            "delete_file_or_folder",
            delete_file_or_folder,
        )

        self.registry.register(
            "close_all_applications",
            close_all_applications,
        )

        self.registry.register(
            "shutdown_pc",
            shutdown_pc,
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

        self.pending_confirmation = None

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

        normalized = self.normalize_wake_text(
            text
        )

        if "jarvis" in normalized:
            return True

        compact = re.sub(
            r"[^a-z]",
            "",
            normalized,
        )

        return "jarvis" in compact


    def conversational_response(self, text):

        normalized = self.normalize_text(
            text
        )

        if normalized in {
            "hi",
            "hello",
            "hey",
            "hello jarvis",
            "hi jarvis",
            "hey jarvis",
        }:
            return (
                "Hello, Sir. It's good to hear from you. "
                "What can I do for you?"
            )

        if normalized in {
            "good morning",
            "good morning jarvis",
        }:
            return (
                "Good morning, Sir. "
                "I hope you're doing well. "
                "What are we working on today?"
            )

        if normalized in {
            "good afternoon",
            "good afternoon jarvis",
        }:
            return (
                "Good afternoon, Sir. "
                "I'm here and ready whenever you are."
            )

        if normalized in {
            "good evening",
            "good evening jarvis",
        }:
            return (
                "Good evening, Sir. "
                "What can I help you with?"
            )

        if normalized in {
            "welcome",
            "welcome jarvis",
        }:
            return (
                "Thank you, Sir. "
                "I'm right here and ready to help."
            )

        if normalized in {
            "how are you",
            "how are you jarvis",
            "how are things",
        }:
            return (
                "I'm doing well, Sir. "
                "Everything is up and running. "
                "What would you like to do?"
            )

        if normalized in {
            "thank you",
            "thanks",
            "thanks jarvis",
        }:
            return (
                "You're welcome, Sir. "
                "Anytime."
            )

        if normalized in {
            "good job",
            "well done",
            "nice job",
        }:
            return (
                "Thank you, Sir. "
                "Glad I could help."
            )

        return None

    def is_shutdown_command(
        self,
        text,
    ):

        normalized = self.normalize_text(
            text
        )

        return normalized in {
            "shutdown jarvis",
            "shut down jarvis",
            "exit jarvis",
            "quit jarvis",
            "stop jarvis",
            "stop yourself",
            "go to sleep",
            "go offline",
        }

    def is_yes_response(self, text):

        normalized = self.normalize_text(
            text
        )

        if normalized in {
            "yes",
            "yeah",
            "yep",
            "yup",
            "sure",
            "okay",
            "ok",
            "do it",
            "go ahead",
            "proceed",
            "confirm",
        }:
            return True

        if normalized.startswith("yes "):
            return True

        if normalized.startswith("yeah "):
            return True

        if normalized.startswith("yep "):
            return True

        if normalized.startswith("sure "):
            return True

        return False


    def is_no_response(self, text):

        normalized = self.normalize_text(
            text
        )

        if normalized in {
            "no",
            "nope",
            "nah",
            "cancel",
            "cancel it",
            "dont",
            "do not",
            "stop",
            "never mind",
            "never",
        }:
            return True

        if normalized.startswith("no "):
            return True

        if normalized.startswith("no,"):
            return True

        if normalized.startswith("nope "):
            return True

        if normalized.startswith("dont "):
            return True

        return False


    def is_close_all_command(self, text):

        normalized = self.normalize_text(
            text
        )

        return normalized in {
            "close everything",
            "close everything down",
            "close all",
            "close all applications",
            "close all apps",
            "close all windows",
            "close every application",
            "close every app",
        }


    def is_shutdown_laptop_command(self, text):

        normalized = self.normalize_text(
            text
        )

        return normalized in {
            "shutdown",
            "shut down",
            "shutdown laptop",
            "shut down laptop",
            "shutdown my laptop",
            "shut down my laptop",
            "shutdown computer",
            "shut down computer",
            "shutdown my computer",
            "shut down my computer",
            "turn off laptop",
            "turn off my laptop",
            "turn off computer",
            "turn off my computer",
        }


    def is_close_and_shutdown_command(self, text):

        normalized = self.normalize_text(
            text
        )

        close_words = (
            "close everything",
            "close all",
            "close all applications",
            "close all apps",
            "close all windows",
        )

        shutdown_words = (
            "shutdown",
            "shut down",
            "shutdown laptop",
            "shut down laptop",
            "shutdown my laptop",
            "shut down my laptop",
            "shutdown computer",
            "shut down computer",
            "shutdown my computer",
            "shut down my computer",
            "turn off laptop",
            "turn off my laptop",
            "turn off computer",
            "turn off my computer",
        )

        has_close = any(
            word in normalized
            for word in close_words
        )

        has_shutdown = any(
            word in normalized
            for word in shutdown_words
        )

        return has_close and has_shutdown


    def ask_shutdown_confirmation(
        self,
        close_everything=True,
    ):

        if close_everything:

            message = (
                "Should I close all open "
                "applications and shut down "
                "the laptop, Sir?"
            )

        else:

            message = (
                "Should I shut down the "
                "laptop, Sir?"
            )

        self.pending_confirmation = {
            "close_everything": close_everything,
        }

        print(
            f"\nJARVIS: {message}"
        )

        self.tts.speak(
            message
        )


    def cancel_pending_confirmation(self):

        self.pending_confirmation = None

        message = (
            "Understood, Sir. "
            "I won't do anything."
        )

        print(
            f"\nJARVIS: {message}"
        )

        self.tts.speak(
            message
        )


    def execute_pending_confirmation(self):

        pending = self.pending_confirmation

        if pending is None:
            return False

        close_everything = pending.get(
            "close_everything",
            False,
        )

        self.pending_confirmation = None

        if close_everything:

            print(
                "\nClosing applications..."
            )

            result = (
                close_all_applications()
            )

            print(
                f"Result: {result}"
            )

            time.sleep(1)

        message = (
            "Understood, Sir. "
            "Shutting down the laptop."
        )

        print(
            f"\nJARVIS: {message}"
        )

        self.tts.speak(
            message
        )

        shutdown_pc()

        self.running = False
        self.active = False

        return True


    def record_audio(self, path):

        audio = self.listener.listen()

        sf.write(
            path,
            audio,
            16000,
        )

        return audio


    def authenticate_audio(self, audio):

        print(
            "Authenticating speaker..."
        )

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

            greeting = (
                "Hello, Sir. "
                "I'm listening. "
                "What can I do for you?"
            )

            print(
                f"\nJARVIS: {greeting}"
            )

            self.tts.speak(
                greeting
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
    def process_command(
        self,
        text,
    ):

        conversational = (
            self.conversational_response(
                text
            )
        )

        if conversational:

            return {
                "type": "response",
                "content": conversational,
            }


        normalized = self.normalize_text(
            text
        )

        if normalized in {
            "bye",
            "goodbye",
            "bye jarvis",
            "goodbye jarvis",
            "go to sleep",
            "sleep jarvis",
        }:

            return {
                "type": "response",
                "content": (
                    "Alright, Sir. "
                    "I'll be here when you need me."
                ),
            }


        if self.is_shutdown_command(
            text
        ):

            self.active = False

            return {
                "type": "response",
                "content": (
                    "Alright, Sir. "
                    "I'll go offline now. "
                    "Call me whenever you need me."
                ),
            }


        print(
            "\nAgent thinking..."
        )

        started = time.time()

        try:

            decision = decide(
                text,
                context=self.context,
            )

        except Exception as exc:

            print(
                f"Agent error: {exc}"
            )

            return {
                "type": "response",
                "content": (
                    "I ran into a problem "
                    "understanding that command, Sir."
                ),
            }

        elapsed = (
            time.time()
            - started
        )

        print(
            f"Decision: {decision}"
        )

        print(
            f"Agent decision time: "
            f"{elapsed:.2f}s"
        )


        action = decision.get(
            "action"
        )


        if action == "respond":

            response = decision.get(
                "response",
                "Alright, Sir.",
            )

            self.context.append(
                {
                    "role": "user",
                    "content": text,
                }
            )

            self.context.append(
                {
                    "role": "assistant",
                    "content": response,
                }
            )

            return {
                "type": "response",
                "content": response,
            }


        if action != "plan":

            return {
                "type": "response",
                "content": (
                    "I'm not sure how to "
                    "handle that yet, Sir."
                ),
            }


        steps = decision.get(
            "steps",
            [],
        )

        if not steps:

            return {
                "type": "response",
                "content": (
                    "I couldn't find an action "
                    "to perform for that, Sir."
                ),
            }


        execution = self.execute_plan(
            text,
            steps,
        )

        return {
            "type": "direct",
            "content": execution,
        }


    def execute_step(
        self,
        tool,
        arguments,
    ):

        print(
            f"Executing: {tool}"
        )

        started = time.time()

        result = self.registry.execute(
            tool,
            arguments,
        )

        elapsed = (
            time.time()
            - started
        )

        print(
            f"Tool execution time: "
            f"{elapsed:.2f}s"
        )

        print(
            f"Result: {result}"
        )

        return result


    def execute_plan(
        self,
        user_input,
        steps,
    ):

        results = []

        for index, step in enumerate(
            steps,
            start=1,
        ):

            tool = step.get(
                "tool"
            )

            arguments = step.get(
                "arguments",
                {},
            )

            if not tool:

                continue

            print(
                f"Step {index}: {tool}"
            )

            attempts = 0

            while True:

                try:

                    result = self.execute_step(
                        tool,
                        arguments,
                    )

                    results.append(
                        {
                            "tool": tool,
                            "result": result,
                        }
                    )

                    break

                except Exception as exc:

                    attempts += 1

                    print(
                        f"Tool failed: {tool}"
                    )

                    print(
                        f"Error: {exc}"
                    )

                    if (
                        attempts
                        > self.max_recovery_attempts
                    ):

                        results.append(
                            {
                                "tool": tool,
                                "result": (
                                    f"Failed: {exc}"
                                ),
                            }
                        )

                        break


                    try:

                        recovery_plan = recover(
                            user_input,
                            tool,
                            str(exc),
                        )

                    except Exception as recovery_exc:

                        print(
                            "Recovery failed:"
                            f" {recovery_exc}"
                        )

                        results.append(
                            {
                                "tool": tool,
                                "result": (
                                    f"Failed: {exc}"
                                ),
                            }
                        )

                        break


                    print(
                        f"Recovery plan: "
                        f"{recovery_plan}"
                    )

                    recovery_steps = (
                        recovery_plan.get(
                            "steps",
                            [],
                        )
                    )

                    if not recovery_steps:

                        results.append(
                            {
                                "tool": tool,
                                "result": (
                                    f"Failed: {exc}"
                                ),
                            }
                        )

                        break

                    tool = recovery_steps[
                        0
                    ].get(
                        "tool"
                    )

                    arguments = (
                        recovery_steps[
                            0
                        ].get(
                            "arguments",
                            {},
                        )
                    )


        if not results:

            return (
                "I couldn't complete that "
                "command, Sir."
            )


        successful = []

        for item in results:

            result = item.get(
                "result"
            )

            if result is not None:

                successful.append(
                    str(result)
                )


        if len(successful) == 1:

            return successful[0]


        return "\n".join(
            successful
        )


    def clean_for_speech(
        self,
        text,
    ):

        if not text:
            return ""

        text = str(text)

        text = re.sub(
            r"https?://\S+",
            "",
            text,
        )

        text = re.sub(
            r"[*_`#]+",
            "",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()


    def speak_stream(
        self,
        content,
    ):

        collected = []

        print(
            "\nJARVIS: ",
            end="",
            flush=True,
        )

        for chunk in stream(
            content
        ):

            if not chunk:
                continue

            print(
                chunk,
                end="",
                flush=True,
            )

            collected.append(
                chunk
            )

        print()

        response = "".join(
            collected
        )

        speech = (
            self.clean_for_speech(
                response
            )
        )

        if speech:

            self.tts.speak(
                speech
            )

        return response
    def handle_command(
        self,
        text,
    ):

        # --------------------------------------------------------
        # PENDING CONFIRMATION
        # --------------------------------------------------------

        if self.pending_confirmation is not None:

            if self.is_yes_response(text):

                self.execute_pending_confirmation()

                return

            if self.is_no_response(text):

                self.cancel_pending_confirmation()

                return

            message = (
                "Please say yes to confirm "
                "or no to cancel, Sir."
            )

            print(
                f"\nJARVIS: {message}"
            )

            self.tts.speak(
                message
            )

            return


        # --------------------------------------------------------
        # POWER COMMANDS
        # --------------------------------------------------------

        if self.is_close_and_shutdown_command(
            text
        ):

            self.ask_shutdown_confirmation(
                close_everything=True
            )

            return


        if self.is_shutdown_laptop_command(
            text
        ):

            self.ask_shutdown_confirmation(
                close_everything=False
            )

            return


        if self.is_close_all_command(
            text
        ):

            result = (
                close_all_applications()
            )

            print(
                f"\nJARVIS: {result}"
            )

            self.tts.speak(
                self.clean_for_speech(
                    result
                )
            )

            return


        # --------------------------------------------------------
        # NORMAL COMMAND
        # --------------------------------------------------------

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

            return


        if (
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

            return


        if (
            result["type"]
            == "stream"
        ):

            self.speak_stream(
                result["content"]
            )

            return


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


                # ------------------------------------------------
                # IMPORTANT:
                #
                # Once a command has already been authenticated
                # and JARVIS is waiting for YES/NO confirmation,
                # don't authenticate the tiny confirmation phrase
                # again.
                # ------------------------------------------------

                if (
                    self.pending_confirmation
                    is None
                ):

                    if not self.authenticate_audio(
                        audio
                    ):

                        print(
                            "Command rejected."
                        )

                        continue


                self.handle_command(
                    text
                )


        except KeyboardInterrupt:

            print(
                "\nStopping JARVIS..."
            )


        except Exception as exc:

            print(
                "\nJARVIS encountered "
                f"an unexpected error: {exc}"
            )

            raise


        finally:

            self.running = False
            self.active = False

            print(
                "\nJARVIS stopped."
            )


if __name__ == "__main__":

    jarvis = Jarvis()

    jarvis.run()
