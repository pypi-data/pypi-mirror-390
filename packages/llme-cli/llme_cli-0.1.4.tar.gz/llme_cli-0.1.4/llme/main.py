#!/usr/bin/env python3

# Copyright (C) 2025 Jean Privat, based from the work of Dory
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""A command-line assistant for local LLMs"""

import argparse
import inspect
import itertools
import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
import tomllib

import prompt_toolkit
import requests
from termcolor import colored, cprint
try:
    from termcolor import can_colorize # Exported since v3.2.0
except ImportError:
    from termcolor.termcolor import _can_do_colour as can_colorize # Was private before v3.2.0

# The global logger of the module
logger = logging.getLogger('llme')


class LLME:
    """The God class of the application."""

    def __init__(self, config):
        self.config = config
        self.model = config.model
        self.prompts = config.prompts # Initial prompts to process
        self.messages = [] # the sequence of messages with the LLM
        self.raw_messages = [] # the sequence of messages really communicated with the LLM server to work-around their various API limitations
        self.history = [] # A parallel history of messages with generations information
        self.generations = [] # the messages causing new generations (forks). They are the non-first children of messages
        self.roots = [] # The first system messages (roots without parent)
        self.current_generation = 0 # The generation number of the current conversation (for prompt prefix)
        self.message_index = None # The current message in the history (for /undo and history navigation)

        self.slash_commands = [
            "/models       list available models",
            "/tools        list available tools",
            "/metrics      list current metrics",
            "/history      list condensed conversation history",
            "/full-history list hierarchical conversation history (with forks)",
            "/redo         cancel and regenerate the last assistant message",
            "/undo         cancel the last user message (and the response) [PageUp]",
            "/pass         go forward in history (cancel /undo) [PageDown]",
            "/edit         run EDITOR on the chat (save,editor,load)",
            "/save FILE    save chat",
            "/load FILE    load chat",
            "/clear        clear the conversation history",
            "/goto M       jump after message M (e.g /goto 5c)",
            "/config       list configuration options",
            "/set OPT=VAL  change a config option",
            "/quit         exit the program",
            "/help         show this help",
        ]

        self.warmup = None
        if self.config.batch or not sys.stdin.isatty() or not sys.stdout.isatty():
            # prompt_toolkit is disabled in batch mode
            # and need a tty
            self.session = None
        else:
            kb = prompt_toolkit.key_binding.KeyBindings()
            kb.add("pageup")(self.on_pageup)
            kb.add("pagedown")(self.on_pagedown)
            self.session = prompt_toolkit.PromptSession(
                    complete_while_typing=True,
                    key_bindings=kb,
                    completer=SlashCompleter(self),
                    complete_style=prompt_toolkit.shortcuts.CompleteStyle.MULTI_COLUMN,
            )
        self.failsafe = False # when True, its mean we are failing. this variable helps to prevent a loop of failure on the catch-all error handling

        self.api_headers = {} # additional headers for the server
        if self.config.api_key:
            self.api_headers["Authorization"] = f"Bearer {self.config.api_key}"

        self.metrics = Metrics()

        tool(self.run_command)

    def cancel_prompt(self):
        """Cancel the current prompt and go back to the main loop"""
        app = prompt_toolkit.application.current.get_app()
        app.erase_when_done = True
        app.exit(exception=CancelEvent())

    def on_pageup(self, event):
        """Keybinding for /undo"""
        if not self.rollback("user"):
            return
        self.cancel_prompt()

    def on_pagedown(self, event):
        """Keybinding for /pass"""
        if not self.rollforward("user"):
            return
        self.cancel_prompt()

    def build_message_object(self, message):
        """Add a message to the history"""

        n = len(self.messages)
        if n > 0:
            parent = self.history[n-1]
            gen = parent.generation
            sibling = parent.children
        else:
            parent = None
            gen = 0
            sibling = self.roots

        if sibling:
            for s in sibling:
                if s.data == message:
                    # Already known, reuse it
                    self.history.append(s)
                    self.current_generation = s.generation
                    return
            # Need a new generation number
            self.generations.append(message)
            gen = len(self.generations)

        self.current_generation = gen
        message_obj = Message(message, parent, n, gen)
        sibling.append(message_obj)
        self.history.append(message_obj)

    def add_message(self, message):
        """
        Append a new message.
        Add it as is in message but transform it in raw_messages.
        """

        self.fork_if_required()

        logger.debug("Add %s message: %s", message['role'], message)
        self.build_message_object(message)
        self.messages.append(message)

        # Special filtering for some models/servers
        # TODO make it configurable and modular
        if isinstance(message["content"], list):
            text_content = []
            # unpack file content parts
            for part in message["content"]:
                if part["type"] == "text":
                    text_content.append(part["text"])
                if part["type"] == "file":
                    # replace the file content with its path.
                    text_content.append(f"The file is {part['file']['filename']}. You can cat its content.")
                if part["type"] == "image_url":
                    self.raw_messages.append(message)
            self.raw_messages.append({"role": message["role"], "content": "\n".join(text_content)})
            return

        if message["role"] == "tool" and self.config.tool_mode != "native":
            message = message.copy()
            message["role"] = "user"

        self.raw_messages.append(message)

    def fork_if_required(self):
        """Fork the conversation to a new generation, if required.
        This will reset the conversation history"""
        if self.message_index is None:
            return
        # Here we need to reset the current conversation to fork it
        # And replace the "message_index" wit a new one
        self.reset_messages(self.messages[:self.message_index])
        logger.debug(f"Fork performed. New history: %s", self.history)


    def get_models(self):
        """List the available models"""
        if self.config.dummy:
            return ['dummy']
        url = f"{self.config.base_url}/models"
        logger.info("Get models from %s", url)
        try:
            response = requests.get(url, headers=self.api_headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise AppError(extract_requests_error(e))
        models = response.json()
        ids = [m["id"] for m in models["data"]]
        logger.info("Available models: %s", ids)
        return ids


    def prompt_prefix(self):
        """Return the prefix number to use in the prompt"""
        res = str(len(self.messages))
        return res

    def confirm(self, question, default=""):
        """Ask a yes/no confirmation to the user"""
        if self.config.yolo:
            cprint(f"{question}: YOLO!", color="light_red")
            return True
        if self.config.batch:
            raise AppError("Confirmation unavailable in batch mode")
        try:
            if self.session:
                x = self.session.prompt([("#ff0000", f"{question}? ")], placeholder=[("#7f7f7f", "Enter to confirm, or give a prompt to cancel")], default=default)
            else:
                x = input(colored(f"{question}? ", "light_red"))
            self.failsafe = False # user input still alive
            if x == "":
                return True
            self.prompts.insert(0, x)
            return False
        except KeyboardInterrupt:
            raise EOFError("Confirmation interrupted") # ugly

    def cat_write(self, file, stdin):
        if not os.path.exists(file):
            cprint(stdin, color="green")
            return

        import difflib
        with open(file, "r") as f:
            old = f.readlines()
        new = stdin.splitlines(keepends=True)
        for line in difflib.unified_diff(old, new, file, file):
            if line[0] == '+':
                color = "green"
            elif line[0] == '-':
                color = "red"
            else:
                color = "white"
            cprint(line.rstrip("\n"), color=color)


    def run_command(self, command: str, stdin: str = ""):
        """Execute a standard shell command and return its result.
        If needed, the input content can be provided.
        To run python code, use `python` as command and the code in `stdin`.
        To write file use `cat > "filepath"` as command and the content in `stdin`.
        To patch a file, use `patch "originalfile"` as command and the unified diff in `stdin`.
        To fetch a website use `w3m -dump "https://example.com/foo.html"` as command and no stdin.
        To fetch a page use `curl -L "https://example.com/foo.html"` as command and no stdin.
        Etc.
        """

        command = command.strip()
        if command == "":
            command = "sh" # assume shell

        import shlex
        try:
            cmd = shlex.split(command, posix=True)
        except ValueError:
            # no closing quotation. Let subprocess handle and returns the error
            cmd = None

        # special known commands
        need_confirm = True
        if not cmd:
            pass
        elif len(cmd) <= 2 and cmd[0] in ["cat", "ls", "pwd", "echo"]:
            need_confirm = False
        elif len(cmd) == 3 and cmd[0] == "cat" and cmd[1] == ">":
            self.cat_write(cmd[2], stdin)
        elif stdin:
            cprint("$ " + command, color="light_red")
            cprint(stdin)

        if self.message_index is not None:
            need_confirm = True # Always confirm when replaying a specific message
            prompt = f"{self.message_index}/{self.prompt_prefix()} RUN {command}"
            message = self.messages[self.message_index]
            if message["role"] == "user":
                default = message["content"]
            else:
                default = ""
        else:
            prompt = f"{self.prompt_prefix()} RUN {command}"
            default = ""

        if need_confirm and not self.confirm(prompt, default=default):
            return None

        # hack for unbuffered python
        if command == "python":
            cmd = "python -u"
        else:
            cmd = command

        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="backslashreplace", # Avoid encoding errors in the output
            bufsize=1  # line-buffered
        )
        logger.debug("Starting sub-process %s", command)

        # send data to stdin
        # FIXME: avoid deadlock...
        # It's weird there isn't a lib or something to do this properly...
        proc.stdin.write(stdin)
        proc.stdin.close()

        content = ''
        with Spinner("light_red", self.config.plain) as am:
            while line := proc.stdout.readline():
                am.stop()
                print(line, end='', flush=True)
                content += line
        proc.wait()
        printn(content)

        if proc.returncode != 0:
            cprint(f"EXIT {proc.returncode}", "light_red")

        return f"command: {command}\nexitcode: {proc.returncode}\nstdout:\n{content}\n"


    def next_asset(self):
        """Get the next asset from the user. or None"""
        if len(self.prompts) == 0:
            return None

        # peek a the next "prompt" to see if it's a file
        user_input = self.prompts[0]
        if not os.path.exists(user_input):
            return None

        # it's a file, so remove it from prompts and add it to files
        self.prompts.pop(0)
        file = Asset(user_input)
        # Test to handle input redirection from /dev/null
        if len(file.raw_content) > 0:
            return file
        return None


    def input_prompt(self):
        """Return a prompt from stdim"""
        try:
            if self.warmup:
                self.warmup.start()
            if self.message_index is not None:
                prompt = f"{self.message_index}/{self.prompt_prefix()}> "
                default = self.messages[self.message_index]["content"]
            else:
                prompt = f"{self.prompt_prefix()}> "
                default = ""
            if self.session:
                user_input = self.session.prompt([("#00ff00", prompt)], default=default, placeholder=[("#7f7f7f", "A prompt, /h for help, Ctrl-C to interrupt")])
            else:
                user_input = input(colored(prompt, "light_green"))
            self.failsafe = False
            if self.warmup:
                self.warmup.stop()
                # No more needed. We are on our own
                self.warmup = None
            return user_input
        except KeyboardInterrupt:
            raise EOFError("interrupted") # ugly


    def next_input(self):
        """ Get the next prompt or slash command"""
        if len(self.prompts) > 0:
            user_input = self.prompts.pop(0)
            if not self.config.plain:
                print(colored(f"{self.prompt_prefix()}>", "light_green"), user_input)
        elif self.config.batch:
            raise EOFError("end of batch") # ugly
        else:
            user_input = self.input_prompt()
        return user_input

    def next_prompt(self):
        """Get the next prompt from the user.
        Returns None or a user message"""
        logger.debug("Get the next prompt. Prompts queue: %d", len(self.prompts))

        files = [] # the list of files to send to the LLM for the next prompt
        while file := self.next_asset():
            files.append(file)

        user_input = self.next_input()

        if user_input == '':
            return None
        if user_input[0] == '/':
            self.slash_command(user_input)
            return None

        while file := self.next_asset():
            files.append(file)

        content_parts = []
        for asset in files:
            content_part = asset.content_part()
            if content_part:
                content_parts.append(content_part)
        if len(content_parts) > 0:
            content_parts.insert(0, {"type": "text", "text": user_input})
            return {"role": "user", "content": content_parts}
        else:
            return {"role": "user", "content": user_input}


    def post_chat_completion(self):
        """Prepare and send the POST request.
        Returns a response"""
        url = f"{self.config.base_url}/chat/completions"
        data = {
            "model": self.model,
            "messages": self.raw_messages,
            "stream": not self.config.bulk,
            "stream_options": {"include_usage": True},
        }
        if self.config.tool_mode == "native":
            data["tools"] = [tool.schema for tool in all_tools.values()]
        if self.config.temperature is not None:
            data["temperature"] = self.config.temperature
        logger.debug("Sending %d raw messages to %s", len(self.raw_messages), url)
        return requests.post(
            url,
            json=data,
            headers=self.api_headers,
            stream=not self.config.bulk,
            timeout=600,  # high enough
        )


    def receive_chat_completion_message(self, response):
        """Process the server response to extract and return the message.
        This function handle; stream mode, tools, thinking, metrics, etc."""

        start_time = time.perf_counter()
        full_content = ''
        full_reasoning_content = ''
        full_tool_calls = []
        mode = None # reasoning, content or none
        message = None # The whole message, if any
        last_chunk = None
        first_token = True
        reasoning_label = None
        for data in SSEReader(response):
            processed = False
            choices = data.get("choices")
            if not choices:
                # assume an empty chunk. This avoids None tests below
                choices = [{"delta":{}}]
            elif len(choices) > 1:
                logger.warning("chunk: too much choices: %s", data)
            choice0 = choices[0]

            message = choice0.get('message')
            if message:
                # A whole message is just a big delta! So reuse the whole code path
                delta = message
            else:
                delta = choice0['delta']

            # last_chunk is used for debugging, it's usually too much to print each chunk
            last_chunk = data
            self.completion_metrics["chunk_n"] += 1

            # Some reasoning models like qwen3 of gpt-oss have a reasoning_content field, with various names
            # It's non-standard but helps to distinguish the reasoning content from the main content
            for label in ["reasoning_content", "reasoning"]:
                reasoning_content = delta.get(label)
                if reasoning_content:
                    reasoning_label = label
                    break # We found one
            if reasoning_content:
                processed = True
                if mode and mode != full_reasoning_content:
                    printn(mode)
                full_reasoning_content += reasoning_content
                mode = full_reasoning_content
                cprint(reasoning_content, "light_magenta", end='', flush=True)

            content = delta.get("content")
            if content:
                processed = True
                if mode and mode != full_content:
                    printn(mode)
                full_content += content
                mode = full_content
                print(content, end='', flush=True)

            tool_calls = delta.get("tool_calls")
            if tool_calls:
                processed = True
                i =- 1
                for tool_call in tool_calls:
                    i = i + 1
                    idx = tool_call.get("index", i)
                    f = tool_call["function"]
                    while len(full_tool_calls) <= idx:
                        full_tool_calls.append(None)
                    if "name" in f:
                        full_tool_calls[idx] = tool_call
                        cprint(f["name"], color="red", end='', flush=True)
                        cprint(f["arguments"], color="red", end='', flush=True)
                    else:
                        full_tool_calls[idx]["function"]["arguments"] += f["arguments"]
                        cprint(f["arguments"], color="red", end='', flush=True)
                    mode="." # force \n after the tool_call is fully outputed

            finish_reason = choice0.get('finish_reason')
            if finish_reason:
                processed = True
                # About: finish_reason
                # We do nothing with it for the moment
                # Some servers give Null for continue and "" for the uneventful finish reason
                # Some other gives "" for continue and a non empty string for finish reason
                # So do not trust anybody and continue the connection until the server closes it
                logger.info("Chunk: finish reason: %s", finish_reason)

            timings = data.get("timings")
            if timings:
                processed = True
                self.completion_metrics.update(timings)

            usage = data.get("usage")
            if usage:
                processed = True
                self.completion_metrics.update(usage)

            if not processed:
                logger.info("Chunk: Unexpected content: %s", data)
                continue
            elif first_token:
                first_token_time = time.perf_counter()
                self.completion_metrics["first_token_ms"] = (first_token_time - start_time) * 1000.0
                first_token = False

            #FIXME: this is fragile and ugly.
            if self.config.tool_mode == "markdown":
                cb = re.search(r"^```run([^\n]*)\n(.*?)^```$", full_content, re.DOTALL | re.MULTILINE)
                if not cb:
                    continue
                arguments = {"command": cb[1], "stdin": cb[2]}
                tool_call = {
                    "id": f"toolcallid-{len(self.messages)}",
                    "type": "function",
                    "function": {"name": "run_command", "arguments": json.dumps(arguments)}}
                full_tool_calls.append(tool_call)
                # Force the LLM to stop once a tool call is found
                break

        if mode:
            printn(mode)
        logger.debug("Chunk: Last one: %s", last_chunk)
        response.close()

        if not message:
            # construct the message from the deltas
            message = {"role": "assistant", "content": full_content}
            if full_reasoning_content:
                message[reasoning_label] = full_reasoning_content
            if full_tool_calls:
                message["tool_calls"] = full_tool_calls
        return message


    def chat_completion(self):
        """Post messages and get a response from the LLM."""
        self.completion_metrics = {}
        start_time = time.perf_counter()
        self.completion_metrics["chunk_n"] = 0
        self.completion_metrics["message_n"] = 1 # only one

        with Spinner("light_blue", self.config.plain):
            response = self.post_chat_completion()
            response.raise_for_status()

        response_time = time.perf_counter()
        self.completion_metrics["response_ms"] = (response_time - start_time) * 1000.0

        if not self.config.plain:
            cprint(f"{self.prompt_prefix()}< ", "light_blue", end='', flush=True)

        message = self.receive_chat_completion_message(response)
        message_time = time.perf_counter()
        self.completion_metrics["total_ms"] = (message_time - start_time) * 1000.0
        self.update_metrics()
        return message


    def update_metrics(self):
        """Display metrics information, and update the global metrics information"""
        data = self.completion_metrics
        logger.info("metrics: %s", data)
        if not "first_token_ms" in data:
            data["first_token_ms"] = 0.0
        data["last_token_ms"] = data["total_ms"] - data["first_token_ms"] - data["response_ms"]
        self.metrics.update(data)

        cprint(self.metrics.infoline(data), "light_grey", file=sys.stderr)

        if self.config.export_metrics:
            try:
                with open(self.config.export_metrics, "w") as file:
                    json.dump({"total": self.metrics.total, "history": self.metrics.history}, file, indent=2)
            except OSError as e:
                raise AppError(f"Can't save metrics to {self.config.export_metrics}") from e


    def do_user(self):
        """Add the user prompt to the conversation"""
        prompt = self.next_prompt()
        if prompt:
            self.add_message(prompt)

    def do_assisant(self):
        if self.config.dummy:
            content = "I'm assistant."
            print(colored(f"{self.prompt_prefix()}<", "light_blue"), content)
            self.add_message({"role": "assistant", "content": content})
            return
        """Add the assistant response to the conversation"""
        self.fork_if_required()
        message = self.chat_completion()
        if message:
            self.add_message(message)

    def run_tool(self, tool_call):
        """Run a tool and return the result as a message"""
        function = tool_call["function"]
        tool = all_tools.get(function["name"])
        if not tool:
            cprint(f"Unknown tool {function["name"]}", color="red")
            message = {"role": "tool", "content": f"Error: unknown tool {function["name"]}. Available tools: {", ".join(all_tools)}", "tool_call_id": tool_call["id"]}
            return message
        try:
            args = json.loads(function["arguments"])
        except json.JSONDecodeError as e:
            logger.debug("Tool arguments error: %r", e)
            cprint(f"{self.prompt_prefix}: Bad tool arguments for {function["name"]}: {e}", color="red")
            message = {"role": "tool", "content": f"Error: bad tool arguments {function["name"]}. {e}", "tool_call_id": tool_call["id"]}
            return message
        logger.info(f"CALL %s(%s)", tool.name, args)
        try:
            result = tool.fun(**args)
        except ToolError as e:
            logger.debug("Tool error: %r", e)
            if e.__cause__:
                e = e.__cause__
            cprint(f"Error during {function["name"]}: {e}", color="red")
            message = {"role": "tool", "content": f"Error during {function["name"]}: {e}", "tool_call_id": tool_call["id"]}
            self.add_message(message)
            return
        if result is None:
            return None
        message = {"role": "tool", "content": str(result), "tool_call_id": tool_call["id"]}
        return message

    def do_tools(self, tool_calls):
        """Run all the tools in the list, and add results to the conversation"""
        for tool_call in tool_calls:
            message = self.run_tool(tool_call)
            if message:
                self.add_message(message)
            else:
                # The user cancelled the tool execution. Let they answer instead of the tool
                self.do_user()

    def do_role(self):
        """Process the next role (user, assistant, tool...)"""
        if not self.messages:
            return self.do_user()

        if self.message_index:
            previous_message = self.messages[self.message_index-1]
        else:
            previous_message = self.messages[-1]
        previous_role = previous_message.get("role")
        if previous_role == "user" or previous_role == "tool":
            return self.do_assisant()
        elif previous_role == "system":
            return self.do_user()
        elif previous_role == "assistant":
            tool_calls = previous_message.get("tool_calls")
            if tool_calls:
                return self.do_tools(tool_calls)
            else:
                return self.do_user()

    def loop(self):
        """The main ping-pong loop between the user and the assistant"""
        while True:
            try:
                self.do_role()
                continue
            except requests.exceptions.RequestException as e:
                if self.config.batch:
                    raise
                logger.error("Server error: %s", extract_requests_error(e))
                self.rollback("user")
            except CancelEvent:
                self.session.app.erase_when_done = False
                logger.debug("Cancelled")
                continue
            except KeyboardInterrupt:
                logger.warning("Interrupted by user.")
                self.rollback("user")
            except EOFError as e:
                logger.info("Quitting: %s", str(e))
                break
            except AppError as e:
                # We got wrapped error to show.
                if self.config.batch:
                    raise
                logger.error("%s", e)
            except Exception as e:
                # catch-all in interactive session
                # it's not supposed to happen
                # but, at least, it allows the user to recover its work.
                if self.config.batch or self.failsafe:
                    raise
                self.failsafe = True
                import traceback
                traceback.print_exc()
                logger.error("Unexpected and uncatched exception: %s\nllme might be now, proceed with caution.", e)
                self.rollback("user")
            if self.config.batch:
                break


    def prepare_system_prompt(self):
        """Build the system message"""
        system_prompt = self.config.system_prompt
        if self.config.tool_mode == "markdown":
            tool = all_tools["run_command"]
            system_prompt += f"""## Tool run_command\n\nRun shell commands with a fenced code block and a `run` label. Format:\n\n```run $command\n$stdin\n```\n\nExample 1, list files:\n\n```run ls\n```\n\nExample 2, read file.txt:\n\n```run cat file.txt\n```\n\nExample 3, write "Hello" to file.txt\n\n```run cat > file.txt\nHello\n```\n\nExample 4, run a python script:\n\n```run python\nprint('Hello World')\n```\n\n"""
            system_prompt += tool.doc

        return {"role": "system", "content": system_prompt}


    def start(self):
        """Start, work, and terminate"""

        models = None
        if not self.model:
            models = self.get_models()
            self.model = models[0]
        if self.config.list_models:
            self.list_models()
            return
        logger.info("Use model %s from %s", self.model, self.config.base_url)

        if self.config.chat_input:
            self.load_chat(self.config.chat_input)
        elif self.config.system_prompt:
            self.add_message(self.prepare_system_prompt())

        stdinfile = None
        if self.config.batch:
            if len(self.prompts) > 0:
                if not sys.stdin.isatty():
                    # There are prompts, so use stdin as data for the first prompt
                    import tempfile
                    stdinfile = tempfile.NamedTemporaryFile(mode='wb', delete=False)
                    with stdinfile as f:
                        f.write(sys.stdin.buffer.read())
                    self.prompts.insert(0, stdinfile.name)
            else:
                # No prompts, so use whole stdin as single prompt.
                self.prompts = [sys.stdin.read()]

        if len(self.prompts) == 0 and not self.config.dummy:
            if not models:
                self.get_models()
            self.warmup = Warmup(self)

        try:
            self.loop()
        finally:
            if self.config.chat_output:
                self.save_chat(self.config.chat_output)
            if stdinfile:
                os.unlink(stdinfile.name)

        if self.metrics.total:
            cprint(f"Total: {self.metrics.infoline(self.metrics.total)}", "light_grey", file=sys.stderr)

    def load_chat(self, file):
        logger.info("Loading conversation from %s", file)
        try:
            with open(file, "r") as f:
                self.reset_messages(json.load(f))
        except OSError as e:
            raise AppError(f"Can't load chat from {file}") from e

    def reset_messages(self, messages):
        self.message_index = None
        self.messages.clear()
        self.history.clear()
        self.raw_messages.clear()
        for message in messages:
            self.add_message(message)
        logger.info("Reset %d messages", len(self.messages))

    def save_chat(self, file):
        logger.info("Dumping conversation to %s", file)
        try:
            with open(file, "w") as f:
                json.dump(self.messages, f, indent=2)
        except OSError as e:
            raise AppError(f"Can't save chat to {file}") from e

    def list_models(self):
        "Print the list of models"
        print(f"Models of {self.config.base_url}:")
        models = self.get_models()
        for m in models:
            sel = "-> " if m == self.model else "   "
            print(f"{sel}{m}")
        return models

    def print_message(self, i, message, before=""):
        role = message["role"]
        if before:
            colors = {"system": "yellow", "user": "green", "assistant": "blue", "tool": "red"}
        else:
            colors = {"system": "light_yellow", "user": "light_green", "assistant": "light_blue", "tool": "light_red"}
        color = colors[role]
        content = message["content"]
        tools = message.get("tool_calls")
        if tools:
            content += f"[tools: {', '.join(t['function']['name']+str(t['function']['arguments']) for t in tools)}]"
        content = re.sub(r"\s+", " ", content).strip()
        import shutil
        size = shutil.get_terminal_size()
        prefix = f"{i} {role}: "
        width = size.columns - len(prefix) - 5 - len(before)
        if len(content) > width:
            content = content[:width].rstrip() + "..."
        if before != "":
            content = colored(content, "light_grey")
        print(before + colored(prefix, color) + content)


    def list_history(self):
        "Print the history of messages"
        for i, message in enumerate(self.messages):
            if self.message_index and i >= self.message_index:
                break
            self.print_message(i, message)

    def list_full_history(self):
        "Print the full history with nice indentation."
        siblings = self.roots
        for i, message in enumerate(self.history):
            if self.message_index and i >= self.message_index:
                break
            self.print_tree(siblings, "", message)
            self.print_message(message.prefix(), message.data)
            siblings = message.children # next siblings
        self.print_tree(siblings, "", True)

    def print_tree(self, messages, prefix="", special=None):
        if not messages:
            return
        if special:
            last = -1
        else:
            last = len(messages) - 1
        for i, child in enumerate(messages):
            if child == special:
                continue
            cid = child.prefix()
            self.print_message(cid, child.data, prefix + ("├─" if i != last else ""))
            self.print_tree(child.children, prefix + ("│ " if i != last else ""))

    def slash_command(self, user_input):
        "Execute a slash command"
        #FIXME too much hardcoded
        args = user_input.split(None, 1)
        cmd = args.pop(0)
        arg = args[0].strip() if args else None
        if cmd in "/help" or cmd in "/?":
            for h in self.slash_commands:
                print(h)
        elif cmd in "/tools":
            list_tools()
        elif cmd in "/config":
            for k, v in vars(self.config).items():
                print(f"{k}: {repr(v)}")
        elif cmd in "/models":
            self.list_models()
        elif cmd in "/history":
            self.list_history()
        elif cmd in "/full-history":
            self.list_full_history()
        elif cmd in "/redo":
            if not self.rollback("assistant"):
                raise AppError("/redo: No assistant message to redo")
            self.list_history()
        elif cmd in "/undo":
            if not self.rollback("user"):
                raise AppError("/undo: No user message to undo")
            self.list_history()
        elif cmd in "/pass":
            if not self.rollforward("user"):
                raise AppError("/pass: Already at latest message")
            self.list_history()
        elif cmd in "/edit":
            self.edit()
        elif cmd in "/save":
            if not arg:
                raise AppError("/save: Missing filename")
            self.save_chat(arg)
        elif cmd in "/load":
            if not arg:
                raise AppError("/load: Missing filename")
            self.load_chat(arg)
        elif cmd in "/clear":
            self.reset_messages([self.prepare_system_prompt()])
        elif cmd in "/goto":
            if not arg:
                raise AppError("/goto: Missing message label")
            self.goto(arg)
        elif cmd in "/metrics":
            for k, v in self.metrics.total.items():
                print(f"{k}: {repr(v)}")
        elif cmd in "/set":
            if not arg:
                raise AppError("/set: Missing setting")
            args = arg.split('=', 1)
            if len(args) != 2:
                raise AppError("/set: Syntax error, expected name=value")
            else:
                self.set_config(*args)
        elif cmd in "/quit":
            raise EOFError("/quit")
        else:
            raise AppError(f"{user_input}: Unknown slash command. Use /help for help.")

    def rollback(self, role):
        "Move message_index to the previous message of role, return the message on success"
        candidate = None
        for i, message in enumerate(self.messages):
            if self.message_index and i >= self.message_index:
                break
            if message.get("role") == role:
                candidate = i
        if not candidate:
            return None
        self.message_index = candidate
        return self.messages[candidate]

    def rollforward(self, role):
        "Move message_index to the next message of role, return the message on success"
        if self.message_index is None:
            return None
        for i, message in enumerate(self.messages[self.message_index+1:]):
            if message.get("role") == role:
                self.message_index = i + self.message_index + 1
                return message
        self.message_index = None
        return "x"


    def edit(self):
        "Save the chat in a tmpfile, edit it, and load it back"
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=True) as tmp:
            import shlex
            self.save_chat(tmp.name)
            editor = os.environ.get("EDITOR", "editor")
            try:
                cmd = shlex.split(editor) + [tmp.name]
            except ValueError as e:
                raise AppError("Invalid editor command %s" % editor) from e
            logger.info( "Running %s", cmd)
            try:
                subprocess.run(cmd, check=True)
            except Exception as e:
                raise AppError("/edit") from e
            self.load_chat(tmp.name)


    def reset_to_history(self, message):
        """Reset the conversation to after a message in the full history"""
        self.current_generation = message.generation
        messages = []
        while message:
            messages.insert(0, message.data)
            message = message.parent
        self.reset_messages(messages)

    def find_label_in_history(self, n):
        """Return a labeled message from the full history"""
        match = re.match(r"(\d+)\s*([a-z]*)", n)
        if not match:
            raise AppError(f"Invalid message label {n}")
        num = int(match.group(1))
        if not match.group(2):
            # no gen, look in the local history first
            if num < len(self.history):
                message = self.history[num]
                logger.debug("goto %d -> %r", num, message)
                return message
            gen = self.current_generation
        else:
            gen = unbase26ish(match.group(2))

        message = self.find_in_history(num, gen)
        logger.debug("goto %s -> %d %d -> %r", n, num, gen, message)
        return message

    def goto(self, n):
        """Jump after a message in the full history"""
        message = self.find_label_in_history(n)
        if not message:
            raise AppError(f"Message {n} not found")
        if message not in self.history:
            self.reset_to_history(message)
        self.message_index = message.number

    def find_in_history(self, num, gen, messages = None):
        """Search a message in the full history with its number and generation."""
        if messages is None:
            messages = self.roots
        for message in messages:
            if message.number == num and message.generation == gen:
                return message
            found = self.find_in_history(num, gen, message.children)
            if found:
                return found
        return None


    def set_config(self, opt, val):
        "Dynamically change a config option"
        opt = opt.strip()
        val = val.strip()
        config = vars(self.config)
        opts = [ k for k in config  if k.startswith(opt)]
        if not opts:
            raise AppError(f"Unknown setting: {opt}")
        if len(opts) > 1:
            raise AppError(f"Ambiguous setting: {opt} could match {", ".join(opts)}")
        opt = opts[0]

        if opt == "verbose":
            val = int(val)
            set_verbose(val)
        elif opt == "model":
            self.model = val
        logger.info("set %s: %r", opt, val)
        # TODO convert types. but don't duplicate argparse
        setattr(self.config, opt, val)


class CancelEvent(Exception):
    """Raised when the prompt is cancelled."""
    pass


class Spinner:
    """A simple context manager for a spinner animation.
    It gives the user a feedback on long computation or network request.

    :param color: color of the spinner with termcolor nomenclature.
    :param disabled: if True, Spinner do nothing. The default is `not sys.stdout.isatty()`. Use False to force the spin.
    :param sequence: string of characters to animate.
    :param speed: animation speed in Hz.

    Usage:
        with Spinner("blue"):
            do_something()
    """
    def __init__(self, color="white", disabled=None, sequence="⠋⠙⠹⠽⠼⠴⠦⠧⠇⠏", speed=10):
        self.color = color
        if disabled is None:
            disabled = not sys.stdout.isatty()
        self.disabled = disabled
        self.sequence = sequence
        self.speed = speed
        self.stop_event = None
        self.animation_thread = None

    def _animate(self):
        """Animation loop, run in a thread."""
        for c in itertools.cycle(self.sequence):
            if self.stop_event.is_set():
                break
            sys.stdout.write(f"\r{colored(c, self.color)} ")
            sys.stdout.flush()
            time.sleep(1/self.speed)
        sys.stdout.write('\r')
        sys.stdout.flush()

    def stop(self):
        """Manually stop the spin."""
        if self.disabled:
            return
        if not self.stop_event.is_set():
            self.stop_event.set()
            self.animation_thread.join()

    def __enter__(self):
        if not self.disabled:
            self.stop_event = threading.Event()
            self.animation_thread = threading.Thread(target=self._animate)
            self.animation_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()


def base26ish(n):
    """Convert an integer to a base26ish string. Used to name generations.
    0 is 'a', 25 is 'z', 26 is 'aa', 27 is 'ab', etc.
    In genuine base26, 26 should be 'ba' since a stands for 0 and b for 1.
    """
    result = ""
    while n >= 0:
        result = chr(ord('a') + (n % 26)) + result
        n //= 26
        n -= 1
    return result

def unbase26ish(s):
    """Convert a base26ish string to an integer. Inverse of base26ish()."""
    result = 0
    for c in s:
        result = result * 26 + (ord(c) - ord('a')) + 1
    return result - 1

class Message:
    """A message in the conversation full history. This class is used to track message generations and children."""
    def __init__(self, data, parent, n, gen):
        self.data = data # The raw json data for the openai API
        self.parent = parent # The parent message in the conversation tree
        self.number = n # The message number in the conversation
        self.generation = gen # The generation number of the message
        self.children = [] # The children messages of this message

    def prefix(self):
        """Return the prefix for the message"""
        return f"{self.number}{base26ish(self.generation)}"

    def __repr__(self):
        return self.prefix()


def add_in_dict(total, delta):
    """Deep increase of all values in total"""
    for key, value in delta.items():
        if key in total:
            if isinstance(value, dict):
                add_in_dict(total[key], value)
            elif isinstance(value, int) or isinstance(value, float):
                total[key] += value
            else:
                logger.warning("Metrics: unmanaged type for key %s: %r", key, value)
        else:
            total[key] = value


class Metrics:
    """Help accounting various metrics"""
    def __init__(self):
        self.total = {}
        self.history = []

    def update(self, d):
        """Add all"""
        self.history.append(d)
        add_in_dict(self.total, d)

    def infoline(self, d):
        """Write a concise infoline"""
        info = []
        if "cache_n" in d:
            info.append(f"cache:%dt prompt:%dt %.2ft/s predicted:%dt %.2ft/s" % (
                d["cache_n"],
                d["prompt_n"],
                1000.0 * d["prompt_n"] / d["prompt_ms"],
                d["predicted_n"],
                1000.0 * d["predicted_n"] / d["predicted_ms"],
            ))
        elif "prompt_tokens" in d:
            info.append(f"prompt:%dt predicted:%dt" % (
                d["prompt_tokens"],
                d["completion_tokens"],
            ))
        info.append(f"resp:%.2fs + 1st:%.2fs + last:%.2fs = %.2fs" % (
            d["response_ms"] / 1000.0,
            d["first_token_ms"] / 1000.0,
            d["last_token_ms"] / 1000.0,
            d["total_ms"] / 1000.0,
        ))
        return " ".join(info)


class SSEReader:
    """Utility class to read the Server-Sent Events (SSE) used in stream mode"""
    def __init__(self, response):
        self.iter_lines = response.iter_lines()

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            line = next(self.iter_lines)
            if not line:
                continue
            if line[0] == 0x7b: # '{'
                # special case of no streaming
                data = json.loads(line.decode())
                return data
            # Handle classic SSE
            data = line.split(b':', 1)
            if len(data) != 2:
                logger.warning(f"Chunk: Unexpected: %s", line)
                continue
            event, data = data
            if event != b'data':
                logger.warning(f"Chunk: Unexpected event type: %s", line)
                continue
            if data in [b'[DONE]', b' [DONE]']:
                # We continue the connection until the server closes it. We do not trust it.
                continue
            try:
                data = json.loads(data.decode())
                return data
            except:
                logger.warning("Chunk: Got a weird one: %s", data)


class Warmup:
    """ A small empty chat request.
    It loads the model (if meeded) and checks that the server/model is ok.  Run in background while the user is typing its first prompt."""

    def __init__(self, llm):
        """The thread is started a soon as possible.
        But no signal is sent before start"""
        self.llm = llm
        self.thread = threading.Thread(target=self._process)
        self.thread.daemon = True
        self.message = None
        self.lock = threading.Lock()
        self.started = False
        self.stopped = False
        self.thread.start()


    def start(self):
        """Stop the program if the warmup failed.
        Or start the watch."""
        with self.lock:
            if self.message is not None:
                logger.error(self.message)
                sys.exit(1)
            self.started = True
        return


    def stop(self):
        """Stop caring about the warmup now.
        There is no clean way in Python to stop the running process or its requests. So just let ignore it and let it die."""
        with self.lock:
            self.stopped = True


    def _process(self):
        """ Thread,function.
        It justs wait for the completion of a small request.
        If everything is fine then the thread will just terminate.Otherwise it will signal am event for the main thread.
        Note: because of Python limitation there is no real way to cancel the request. This is mildly annoying."""

        url = f"{self.llm.config.base_url}/chat/completions"
        json = {
            "model": self.llm.model,
            "messages": [{"role":"user", "content":""}],
            "max_completion_tokens":1,
            "max_tokens":1,
            "temperature":0,
            "stream": True,
        }
        logger.info("warmup %s", url)
        try:
            # TODO maybe add a timeout? I'm not sure
            with requests.post(url=url, headers=self.llm.api_headers, json=json, stream=True) as response:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # store, signal or ignore
            with self.lock:
                logger.info("warmup: raise %s", e)
                if self.stopped: # ignore
                    return

                self.message = extract_requests_error(e)
                if not self.started: # stored
                    return

                # signal
                logger.error("%s", self.message)
                # sys.stdin.clode() don't cancel readline
                # sys.exit(1) don't stop the process
                # both approaches are not that much thread-safe
                # The remaining route is to send a signal that will interrupt the main thread
                import signal
                os.kill(os.getpid(), signal.SIGQUIT)
                return
        logger.info("warmup: completed")


# The dict of all registered tools
all_tools = {}

# Conversion between python and json-schema types
type_map = {int: "integer", str: "string"}

class Tool:
    """A tool usable by the LLM. Create them wit the `@tool` decorator"""
    def __init__(self, fun):
        self.name = fun.__name__
        self.fun = fun
        self.doc = fun.__doc__
        all_tools[self.name] = self
        self.build_schema()

    def build_schema(self):
        """Build the schema of the tool used to communicate with the LLM"""
        signature = inspect.signature(self.fun)
        self.signature = signature
        logger.info("Tool: %s%s", self.name, signature)
        params = {}
        reqs = []
        for n, p in signature.parameters.items():
            res = {}
            params[n] = res
            if p.annotation != inspect._empty:
                res["type"] = type_map[p.annotation]
            if p.default == inspect._empty:
                reqs.append(n)
            else:
                res["default"] = p.default

        self.schema = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.doc,
                "parameters": {
                    "type": "object",
                    "properties": params,
                    "required": reqs,
                }
            }
        }

def tool(fun):
    """ Tool decorator. This registers a function to be usable by the LLM."""
    tool = Tool(fun)
    return fun

class ToolError(Exception):
    """Exception raised by tools intended to the assistant.
    Other exceptions raised by tools are send-back to the user.
    You can wrap an existing exception e for the assistant with:

        raise ToolError() from e
    """
    pass


class Asset:
    "A loaded file"
    def __init__(self, path):
        self.path = path
        try:
            with open(path, 'rb') as f:
                self.raw_content = f.read()
        except OSError as e:
            logger.error("Can't load file %s: %s", path, e)
            sys.exit(1) # Make it better
        if len(self.raw_content) == 0:
            logger.info("Empty file %s", path)
            self.mime_type = "inode/x-empty"
            return
        import magic
        self.mime_type = magic.from_buffer(self.raw_content, mime=True)
        logger.info("File %s is %s", path, self.mime_type)

    def content_part(self):
        """Return the content part for the user message"""
        import base64
        if self.mime_type.startswith("image/"):
            data = base64.b64encode(self.raw_content).decode()
            url = f"data:{self.mime_type};base64,{data}"
            return {"type": "image_url", "image_url": {"url": url}}
        else:
            data = base64.b64encode(self.raw_content).decode()
            return {"type": "file", "file": {"file_data": data, "filename": self.path}}

class AppError(Exception):
    """Application error to give feedback to the user."""
    def __str__(self):
        if self.__cause__:
            return f"{super().__str__()}: {self.__cause__}"
        else:
            return super().__str__()

class SlashCompleter(prompt_toolkit.completion.Completer):
    """A completer for slash commands.
    For some reasons, the provided completers do not like 'words' with / at the beginning"""
    def __init__(self, llme):
        self.llme = llme # Strongly coupled, I allow it
        self.nesting = {}
        for command in self.llme.slash_commands:
            words = command.split()
            command = words[0][1:]
            if words[1] == "FILE":
                self.nesting[command] = prompt_toolkit.completion.PathCompleter(expanduser=True)
            else:
                self.nesting[command] = None
        notsettable = ["config", "plugins", "version", "dump_config", "list_tools", "list_models", "prompts"]
        settings = {x + "=" for x in vars(self.llme.config) if x not in notsettable}
        self.nesting["set"] = settings

        self.completer = prompt_toolkit.completion.NestedCompleter.from_nested_dict(self.nesting)

    def get_completions(self, document, complete_event):
        if not document.text.startswith("/"):
            return
        new_document = prompt_toolkit.document.Document(text=document.text[1:], cursor_position=len(document.text)-1)
        yield from self.completer.get_completions(new_document, complete_event)


def extract_requests_error(e):
    """Common handling of requests error"""
    logger.debug("request error: %s", e)
    if e.request is None:
        return str(e)
    if e.response is None:
        return f"{e} ({e.request.url})"

    """Server may format their error in plain text or json"""
    text = e.response.text
    if text and text[0] == '{':
        logger.debug("full error response: %s", text)
        try:
            data = json.loads(text)
        except:
            data = {}
        if "error" in data:
            data = data["error"]
            text = data
        if "message" in data:
            text = data["message"]

    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 80:
        text = text[:80] + "..."

    message = f"{text.strip()} ({e.response.status_code} {e.response.request.url})"
    return message


def printn(previous_string):
    """Print a newline if previous_string does not end with one"""
    if not previous_string.endswith("\n"):
        print()


def apply_config(args, config, path):
    """Apply a config dict to an args namespace without overwriting existing values (precedence).
    The method is a little ugly but it works... """
    #TODO check types
    variables = vars(args)
    for k in variables:
        if variables[k] is None and k in config:
            setattr(args, k, config[k])
    for k in config:
        if k not in variables:
            logger.warning("%s: Unknown config key %s", path, k)

def apply_env(args):
    """Apply environment variables to an args namespace without overwriting existing values (precedence)."""
    variables = vars(args)
    for k in variables:
        var = f"LLME_{k.upper()}"
        env = os.environ.get(var)
        if variables[k] is None and env:
            # TODO type conversion
            setattr(args, k, env)
    for k in os.environ:
        m = re.match(r'LLME_(.*)', k)
        if m and m[1].lower() not in variables:
            logger.warning("Unknown environment variable %s", k)

def load_config_file(path):
    """Load a TOML config file."""
    logger.debug("Loading config from %s", path)
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except OSError as e:
        raise AppError(f"Can't load config file {path}") from e
    except tomllib.TOMLDecodeError as e:
        raise AppError(f"Invalid config file {path}") from e

def resolve_config(args):
    """Compute config in order of precedence"""
    # 1. args have the highest precedence

    # 2. then explcit --config files in reverse order (last wins)
    if args.config:
        for path in reversed(args.config):
            config = load_config_file(path)
            apply_config(args, config, path)

    # 3. Then environment variables
    apply_env(args)

    # 4. The default config files: user, then system
    config_dirs = [
        os.path.expanduser("~/.config/llme"),
        os.path.dirname(os.path.abspath(__file__)),
    ]
    for directory in config_dirs:
        path = os.path.join(directory, "config.toml")
        if os.path.exists(path):
            config = load_config_file(path)
            apply_config(args, config, path)

    # 5. ultimate defaults where argparse default value is None
    if args.tool_mode is None:
        args.tool_mode = "native"
    if args.batch is None and not sys.stdin.isatty():
        args.batch = True

    logger.debug("Final config: %s", vars(args))


def load_module(path):
    """Just load a random python file. I'm not sure why its so complex"""
    import importlib.machinery
    basename = os.path.basename(path)
    name, ext = os.path.splitext(basename)
    try:
        return importlib.machinery.SourceFileLoader(name, path).load_module()
    except OSError as e:
        raise AppError(f"Can't load plugin {path}") from e

def load_plugin(path):
    """Load a single python module, or all python modules of a directory."""
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith(".py"):
                filepath = os.path.join(path, filename)
                load_module(filepath)
    else:
        load_module(path)

def list_tools():
    for name in all_tools:
        tool = all_tools[name]
        lines = tool.doc.splitlines()
        print(f"{name}{tool.signature} {lines[0]}")
        for line in lines[1:]:
            print(f"  {line}")

def show_version():
    """Print the version number.
    Note: version information with importlib.metadata is garbage as this mishandle both "dev" installation, and a possible concurrent old version. So we do it the old way with git and a _version file"""
    try:
        dirname = os.path.dirname(__file__)
        version = subprocess.check_output(["git", "-C", dirname, "describe", "--tags", "--dirty"], text=True, stderr=subprocess.DEVNULL).strip()
        print(f"llme development version: {version}")
    except subprocess.CalledProcessError:
        try:
            from . import _version
            print(f"llme version {_version.version}")
        except ImportError:
            print(f"llme standalone version")

def set_verbose(level):
    "Assign a global verbose level (in number of -v)"
    if level is None:
        level = 0
    consolehandler = logging.StreamHandler(sys.stderr)
    consolehandler.setFormatter(ColorFormatter())
    logger.addHandler(consolehandler)
    logging_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    logging_level = logging_levels[min(level, len(logging_levels) - 1)]
    logger.setLevel(logging_level)
    consolehandler.setLevel(logging_level)
    consolehandler.setFormatter(ColorFormatter())
    logger.info("Log level set to %s", logging.getLevelName(logger.level))

class ColorFormatter(logging.Formatter):
    """A simple colored formatter."""

    COLORS = [
        (logging.DEBUG, 'light_grey'),
        (logging.INFO, 'cyan'),
        (logging.WARNING, 'light_cyan'),
        (logging.ERROR, 'light_red'),
    ]

    def color(self, record):
        for level, color in self.COLORS:
            if record.levelno <= level:
                return color
        return 'white' # default color

    def format(self, record):
        return f"{colored(record.levelname, self.color(record))}: {record.getMessage()}"


def process_args():
    """Handle command line arguments and envs."""
    parser = argparse.ArgumentParser(
        usage='%(prog)s [options...] [prompts...]',
        description="OpenAI-compatible chat CLI.",
        epilog="Boolean flags can be negated with `--no-`. Example `--no-plain` to force colors in a non TTY",
    )
    # Trick: "store_true" options are defaulted to None, so we can distinguish between explicit --foo (True), --no-foo (False) and unset (None)
    parser.add_argument("-u", "--base-url", metavar="URL", help="API base URL [base_url]")
    parser.add_argument("-m", "--model", metavar="NAME", help="Model name or identifier [model]")
    parser.add_argument(      "--list-models", action="store_true", default=None, help="List available models then exit")
    parser.add_argument(      "--api-key", metavar="SECRET", help="The API key [api_key]")
    parser.add_argument("-b", "--batch", action="store_true", default=None, help="Run non-interactively. Implicit if stdin is not a tty [batch]")
    parser.add_argument("-p", "--plain", action="store_true", default=None, help="No colors or tty fanciness. Implicit if stdout is not a tty [plain]")
    parser.add_argument(      "--bulk", action="store_true", default=None, help="Disable stream-mode. Not that useful but it helps debugging APIs [bulk]")
    parser.add_argument("-o", "--chat-output", metavar="FILE", help="Export the full raw conversation in json")
    parser.add_argument("-i", "--chat-input", metavar="FILE", help="Continue a previous (exported) conversation")
    parser.add_argument(      "--export-metrics", metavar="FILE", help="Export metrics, usage, etc. in json")
    parser.add_argument("-s", "--system", dest="system_prompt", help="System prompt [system_prompt]")
    parser.add_argument(      "--temperature", type=float, help="Temperature of predictions [temperature]")
    parser.add_argument(      "--tool-mode", choices=["markdown", "native"], help="How tools and functions are given to the LLM [tool_mode]")
    parser.add_argument("-c", "--config", metavar="FILE", action="append", help="Custom configuration files")
    parser.add_argument(      "--list-tools", action="store_true", default=None, help="List available tools then exit")
    parser.add_argument(      "--dump-config", action="store_true", default=None, help="Print the effective config and quit")
    parser.add_argument(      "--plugin", metavar="PATH", action="append", dest="plugins", help="Add additional tool (python file or directory) [plugins]")
    parser.add_argument("-v", "--verbose", action="count", help="Increase verbosity level (can be used multiple times)")
    parser.add_argument(      "--log-file", metavar="FILE", help="Write logs to a file [log_file]")
    parser.add_argument("-Y", "--yolo", action="store_true", default=None, help="UNSAFE: Do not ask for confirmation before running tools. Combine with --batch to reach the singularity.")
    parser.add_argument(      "--version", action="store_true", default=None, help="Display version information and quit")
    parser.add_argument(      "--dummy", action="store_true", default=None, help=argparse.SUPPRESS) # Disable LLM for testing the UI alone
    parser.add_argument("prompts", nargs='*', help="An initial list of prompts")
    # Trick: iterate on store_true options to add the --no- variants
    for action in parser._actions:
        if action.const is True:
            for name in action.option_strings:
                if name.startswith("--") and not name.startswith("--no-"):
                    x=parser.add_argument("--no" + name[1:], dest=action.dest, action="store_false", help=argparse.SUPPRESS)

    args = parser.parse_intermixed_args()
    if args.version:
        show_version()
        sys.exit(0)

    # We need to that first because `can_colorize()` is cached.
    # So we need to "guess" the environment before printing anything, including logs
    if args.plain is None:
        args.plain = not can_colorize()
    elif args.plain:
        # For termcolor and subprocesses
        os.environ["NO_COLOR"] = "True" # https://no-color.org/
    else:
        # For termcolor and subprocesses
        os.environ["FORCE_COLOR"] = "True" # https://force-color.org/

    set_verbose(args.verbose)
    logger.debug("Given arguments %s", vars(args))
    if args.log_file:
        try:
            filehandler = logging.FileHandler(args.log_file)
        except OSError as e:
            raise AppError(f"Can't open log file {args.log_file}") from e
        filehandler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        filehandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(filehandler)

    resolve_config(args)

    if args.dump_config:
        json.dump(vars(args), sys.stdout, indent=2)
        sys.exit(0)

    if args.plugins:
        for plugin in args.plugins:
            load_plugin(plugin)

    if not args.base_url:
        logger.error("Error: --base-url required and not defined the config file.")
        sys.exit(2)

    return args


def main():
    """The main CLI entry point."""
    try:
        config = process_args()
        llme = LLME(config)
        if config.list_tools:
            list_tools()
            sys.exit(0)

        llme.start()
    except AppError as e:
        logger.error("%s", e)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logger.error("Server error: %s", extract_requests_error(e))
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
