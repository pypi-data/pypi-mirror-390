# 🧠 LLM-ESQUE VIBRATIONS: llme - THE ULTIMATE CLI ASSISTANT FOR OPENAI-COMPATIBLE CHAT SERVERS

<div align="center">
  <img src="https://github.com/privat/llme/assets/2319754/f3e8d1e6-0d71-447f-b4c1-3f8f1b1c1d2a" alt="llme logo" width="200"/>
</div>

<p align="center">
  <em>🚀 THE ULTIMATE CLI ASSISTANT FOR OPENAI-COMPATIBLE CHAT SERVERS</em><br/>
  <em>✨ BUILT WITH PYTHON, POWERED BY LLM MAGIC ✨</em>
</p>

<div align="center">
  <a href="https://github.com/privat/llme/actions/workflows/test.yml"><img src="https://github.com/privat/llme/actions/workflows/test.yml/badge.svg" alt="CI Status"></a>
  <a href="https://pypi.org/project/llme-cli/"><img src="https://badge.fury.io/py/llme-cli.svg" alt="PyPI version"></a>
  <a href="https://github.com/privat/llme/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-GPLv3-blue.svg" alt="License"></a>
</div>

## 🌟 OVERVIEW: UNLEASH THE POWER OF LOCAL LLMs

**llme** is the **ultra-sleek**, **single-file** command-line chat client that effortlessly interfaces with any OpenAI-compatible API server. It's your **neural network-powered** assistant for inspecting configurations, running commands, editing files, and unleashing AI-powered chaos 🚀

> *"I just want to quickly test my model hosted with llama.cpp but don't want to spin up openwebui"* - The LLM enthusiast's mantra 💡

## 🔥 FEATURES: BURNING WITH INNOVATION

| 🧠 CORE CAPABILITIES | 🚀 TECHNICAL MIGHT |
|----------------------|-------------------|
| 🔄 **OpenAI API Compatible** | 🎯 **Extremely simple**: Single file, no installation required (but installation is still available) 📦 |
| 🔌 **CLI Interface** | 🧪 **Tools included**: Ask it to act on your file system and edit files (yolo) 💣 |
| ⚡ **Shell & Python Integration** | 🧬 **Neural Learning**: LLMs are trained on code and OS configuration and already machine-learnt to select probable tools 🤖 |

## 🚀 THE VIBRANT TECHNICAL STACK

🧠 **LLM Powered Intelligence**
> *"The basic idea is that LLMs are trained on code and OS configuration and already (machine) learnt to select the probable tools to use and actions to take. Therefore, there is no need to teach them to use made-up function and tools with bad json schemas."*

💻 **Interactive Terminal Experience**
> *"Just give them a shell, a python interpreter, and let you (only) live (once)."*

## 🛠️ INSTALLATION: GET READY TO UNLEASH POWER

### 🔧 Quick-start a local LLM server if you don't have one already

#### 🐧 With llama.cpp via Homebrew:
```bash
brew install llama.cpp
llama-server -hf unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF --ctx-size 0 --jinja
```

#### 🐳 With Ollama:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3-coder:30b
```

> **Qwen3-Coder-30b** is a **niche model** that delivers unparalleled performance.

### 📦 llme Installation Options

#### 📦 PyPI (possibly an old version)
```bash
pipx install llme-cli
llme --help
```

#### 🚀 GitHub Direct Install (latest dev version)
```bash
pipx install -f git+https://github.com/privat/llme.git
llme --help
```

#### 🛠️ Clone then install in development mode
```bash
git clone https://github.com/privat/llme.git
pipx install -e ./llme
llme --help
```

#### 💻 Clone and run from source (no installation)
```bash
git clone https://github.com/privat/llme.git
pip install -r llme/requirements.txt
./llme/llme/main.py --help
```

## 🎮 USAGE: POWER UP YOUR TERMINAL SESSIONS

### 🗣️ Run an interactive chat session

```bash
llme --base-url "http://localhost:8080/v1" # for default llama-server (llama.cpp)
llme --base-url "http://localhost:11434/v1" # for default ollama server
```

Or if you want a specific model:
```bash
llme --base-url "http://localhost:8080/v1" --model "unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF"
```

### 🧭 Configuration (Recommended)

Edit `~/.config/llme/config.toml`

> 🔍 Look at [config.toml](llme/config.toml) for an example.

### ⚙️ Prompt Engineering: The Art of Influence

The REPL interface allows you to **navigate** in the conversation history, **fork** it, and even **edit** it. It's easy to **replay token generation**, **try different prompts**, **update parameters**, or **gaslight** the assistant.

### 📡 One-shot Queries: Precision Execution

Each prompt is run in order in the same chat session:
```bash
llme "What is the capital of France?" \
  "What the content of the current directory?" \
  "What is the current operating system?" \
  "What is the factorial of 153?" \
  "What is the weather at Tokyo right now?"
```

Or pipe the query:
```bash
echo "What is the capital of France?" | llme
```

> 🚨 Interactive sessions are often better because, if needed, the model is loaded at the start of the command, so is loading while you type. Also no issues with escaping `"` or `'`

## 🔧 TOOLS: POWERFUL CAPABILITIES

### ⚡ Shell Integration
The LLM has **direct access** to your shell (and files) and a python interpreter.
> **⚠️ USER CONFIRMATION REQUIRED** before executing any command.

### 🤖 YOLO Mode: Unleash the Chaos
> 🔥 **WARNING**: No warranty, yada yada, etc. llme can just **kill** your **OS** and **cats**.
> 💣 **DO NOT RUN** without understanding what it does.
```bash
sudo llme --batch --yolo "Distupgrade the system. You are root! Do as you wish."
```

## 📊 OPTIONS & CONFIGURATION: CUSTOMIZE YOUR EXPERIENCE

<!--help-->
```console
$ llme --help
usage: llme [options...] [prompts...]

OpenAI-compatible chat CLI.

positional arguments:
  prompts               An initial list of prompts

options:
  -h, --help            show this help message and exit
  -u, --base-url URL    API base URL [base_url]
  -m, --model NAME      Model name or identifier [model]
  --list-models         List available models then exit
  --api-key SECRET      The API key [api_key]
  -b, --batch           Run non-interactively. Implicit if stdin is not a tty
                        [batch]
  -p, --plain           No colors or tty fanciness. Implicit if stdout is not
                        a tty [plain]
  --bulk                Disable stream-mode. Not that useful but it helps
                        debugging APIs [bulk]
  -o, --chat-output FILE
                        Export the full raw conversation in json
  -i, --chat-input FILE
                        Continue a previous (exported) conversation
  --export-metrics FILE
                        Export metrics, usage, etc. in json
  -s, --system SYSTEM_PROMPT
                        System prompt [system_prompt]
  --temperature TEMPERATURE
                        Temperature of predictions [temperature]
  --tool-mode {markdown,native}
                        How tools and functions are given to the LLM
                        [tool_mode]
  -c, --config FILE     Custom configuration files
  --list-tools          List available tools then exit
  --dump-config         Print the effective config and quit
  --plugin PATH         Add additional tool (python file or directory)
                        [plugins]
  -v, --verbose         Increase verbosity level (can be used multiple times)
  --log-file FILE       Write logs to a file [log_file]
  -Y, --yolo            UNSAFE: Do not ask for confirmation before running
                        tools. Combine with --batch to reach the singularity.
  --version             Display version information and quit

Boolean flags can be negated with `--no-`. Example `--no-plain` to force
colors in a non TTY
```
<!--/help-->

> ⚠️ Run a fresh `--help` in case I forgot to update this README.

### 🧠 Configuration Precedence

All options with names in brackets can be set in the config file (`base_url` for `--base-url`).
They can also be set by environment variables (`LLME_BASE_URL` for `--base-url`).

1. The explicit option in the command line (the higher precedence)
2. The explicit config files (given by `--config`) in reverse order (last wins)
3. The environment variables (`LLME_SOMETHING`)
4. The user configuration file (`~/.config/llme/config.toml`)
5. The system configuration file provided by the package (the lowest precedence)

## 🗺️ SLASH COMMANDS: TERMINAL SUPERPOWERS

Special commands can be executed during the chat.
Those starts with a `/` and can be used when a prompt is expected (interactively or in the command line).
The command `/help` show the available slash commands.

<!--slash-help-->
```console
$ llme /help /quit
/models       list available models
/tools        list available tools
/metrics      list current metrics
/history      list condensed conversation history
/full-history list hierarchical conversation history (with forks)
/redo         cancel and regenerate the last assistant message
/undo         cancel the last user message (and the response) [PageUp]
/pass         go forward in history (cancel /undo) [PageDown]
/edit         run EDITOR on the chat (save,editor,load)
/save FILE    save chat
/load FILE    load chat
/clear        clear the conversation history
/goto M       jump after message M (e.g /goto 5c)
/config       list configuration options
/set OPT=VAL  change a config option
/quit         exit the program
/help         show this help
```
<!--/slash-help-->

> ⚠️ Run a fresh `/help` in case I forgot to update this README.

## 🔌 LIBRARY & PLUGIN SYSTEM: EXTEND YOUR POWER

### 🧬 Library Usage

Important: the API is far from stable.

LLME is usable as a library, so you can use its features.
The main advantage for now to import `llme` is to add new custom tools usable by LLMs.

### 🎨 Custom Tools with Annotations

You can transform a python function into a tool with the annotation `@llme.tool`.
Look at [weather_plugin.py](examples/weather_plugin.py) for an example.

#### 🔧 Usage Examples

Run the weather plugin as a standalone program (it disables all LLM tools except the weather one).
```bash
./examples/weather_plugin.py 'Will it rains tomorrow at Paris?'
```

Use llme with the `--plugin` option to add one (or more) plugin and bring in all their tools.
```bash
llme --plugin examples/weather_plugin.py 'Will it rains tomorrow at Paris?'
```

Or whole directories!
```bash
llme --plugin examples 'Will it rains tomorrow at Paris?'
```

## 🧪 BATCH MODE: AUTOMATION POWER

llme can be used in batch or in interactive mode.

The batch mode, with `--batch`, is the default when stdin is not a tty.

If there are no prompts on the command line, then the stdin is read and used as a single big prompt and the program terminates.

Otherwise, each prompt from the command line is used one after the other and the program terminates.
If stdin is not a tty, it is read and used as attached data (text or image) send with the first prompt of the command line.

Tools can be used by the assistant in batch mode, but if a confirmation is required, the program will exit with an error (unless `--yolo` is used).

## 🧑‍💻 INTERACTIVE MODE: CHAT POWER

The interactive mode, with `--no-batch`, is the default when stdin is a tty.

When both stdin and stdout are tty, the rich terminal interface with [`prompt_toolkit`](https://github.com/prompt-toolkit/python-prompt-toolkit) is used and provide completion, history, keybindings, etc.
Otherwise, it falls back to a simple `input()` interface that process each line as a prompt.

As with the batch mode, the prompts of the command line are used first, one after the other, then the user can provide prompts interactively.

Tools can be used by the assistant in interactive mode, and the user might be asked for confirmation.
Also, most errors are not fatal in interactive mode.

## 🔧 DEVELOPMENT: BECOME A POWER USER

I do not like Python, nor LLMs, but I needed something simple to test things quickly and play around.
My goal is to keep this simple and minimal: it should fit into a single file and still be manageable.

PR are welcome!

### 🎯 TODO: FUTURE VISION

* 🧠 OpenAI API features
  * [x] API token (untested)
  * [x] list models
  * [x] stream mode
  * [x] bulk mode (non stream mode)
  * [x] thinking mode
  * [x] multimodal
  * [x] attached files
  * [x] attached images
  * [ ] ?
* 🧰 Tools
  * [x] markdown tools
  * [x] native tools
  * [x] run shell command
  * [x] run Python code
  * [x] user-defined tools
  * [ ] sandboxing
  * [x] whitelist/blacklist
* 🎨 User interface & features
  * [x] readline
  * [x] better prompt & history
  * [x] braille spinner
  * [x] model warmup
  * [x] save/load conversation
  * [x] export metrics/usage/statistics
  * [x] slash commands
  * [x] completion for slash commands
  * [x] undo/retry/edit
  * [x] error recovery
  * [x] better tool reporting
  * [x] Usable in pipelines or without a TTY
  * [ ] post-processing output
  * [ ] attach files in interactive mode
  * [ ] ?
* 🔧 Customization and models
  * [x] config files
  * [x] config with env vars
  * [ ] type check / conversion
  * [x] plugin system
  * [ ] better tool selection
  * [x] temperature
  * [ ] other hyper parameters
  * [x] handle non-conform thinking & tools
  * [ ] detect model features (is that even possible?)
  * [x] bench system & reporting
  * [ ] user-defined additional data
  * [ ] user-defined filters
* 🧼 Code quality
  * [x] docstring and comments
  * [x] small code base
  * [x] small methods
  * [x] better logging
  * [x] tests suites
  * [x] robustness and error handling
  * [ ] better separation of CLI and LLM
  * [ ] better libification
* 🌐 Misc
  * [x] README
  * [x] Vibe README
  * [x] TODO list :p
  * [x] build file
  * [x] PyPI [package](https://pypi.org/project/llme-cli/)
  * [x] plugin example
  * [ ] ?

### 🌐 OpenAI API Integration

The two HTML routes used by llme are:

* `$base_url/models` (<https://platform.openai.com/docs/api-reference/models>) for `--list-models` (and to get a default model when `--model` is empty)
* `$base_url/chat/completions` (<https://platform.openai.com/docs/api-reference/chat>) for the main job. Streaming (<https://platform.openai.com/docs/api-reference/chat-streaming>) is used by default.
It can be disabled with `--bulk`, mainly for debugging weird APIs.

Images are uploaded as content parts, for multimodal models.

Tools are integrated with either `--tool-mode=native` for the native function API (<https://platform.openai.com/docs/guides/function-calling>), or with `--tool-mode=markdown` a custom approach intended for models that does not support it (or performs poorly with it).
Custom tools can be profited, see the `--plugin` option.

### 🚨 Issues & Compatibility

* The various OpenAI compatible servers and models implement different subsets. Compatibility is worked on and there is less random 4xx or 5xx responses. Major local LLM servers and servers were tested. See the [benchmark](benchmark.md)
* Models are really sensitive to prompts and system prompts, but you can create a custom config file for each.
* Models are really sensitive to how the messages are structured, unfortunately that is currently hardcoded in the program. I do not want to hard-code many tweaks and workarounds. :(

## 💖 ACKNOWLEDGMENTS: CREDITS & INSPIRATION

* 🤖 [openwebui](https://github.com/open-webui/open-webui) for an inspiration, but too complex and web oriented.
* 🧠 [gptme](https://github.com/gptme/gptme) for another inspiration, but also too complex and targets too much non-local LLMs.
* 📡 [openai-cli](https://github.com/doryiii/openai-cli) for a simpler approach I built on top of.
* 🧠 [llama.cpp](https://github.com/ggerganov/llama.cpp), [nexa-sdk](https://github.com/NexaAI/nexa-sdk/) and others for your great work.

## 🌈 CONTRIBUTING: JOIN THE VIBRANT COMMUNITY

🚀 **WELCOME TO THE FUTURE OF TERMINAL AI ASSISTANCE!**

> *"The only way to do great work is to love what you do."* - Steve Jobs

> *"LLM-ESQUE VIBRATIONS: llme - The Ultimate CLI Assistant for OpenAI-Compatible Chat Servers"*
