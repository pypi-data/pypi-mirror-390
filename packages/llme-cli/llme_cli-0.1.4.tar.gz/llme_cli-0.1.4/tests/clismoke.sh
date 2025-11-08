#!/bin/bash

. "$(dirname "$0")/utils.sh"

# validate each message content in the chat with PCRE
validate_chat() {
	i=0
	for re in "$@"; do
		if ! content=$(jq -c ".[$i]" "$LOGDIR/chat.json"); then
			result FAIL "bad jq"
			return 1
		fi
		if ! echo "$content" | grep -qP "$re"; then
			echo "$content"
			result FAIL "at $i no $re"
			return 1
		fi
		((i++))
	done
	if ! content=$(jq "length" "$LOGDIR/chat.json"); then
		result ALMOST "bad jq"
		return 1
	fi
	if [ "$content" -ne "$i" ]; then
		result ALMOST "expected length $i, got $content"
		return 1
	fi
	result PASS
}

# test a command that should error
et() {
	prepare "$@" || return
	shift
	setup
	echo
	result "RUNNING"
	runllme "$@"
	err=$?
	teardown
	if [ "$err" -eq 124 ]; then
		result "TIMEOUT"
		return 124
	elif [ "$err" -eq 0 ]; then
		result "FAIL" "unexpected success"
		return 1
	fi
	# we good
	return 0
}

# Vadidate if specific regex are found in the err.txt file
validate_err() {
	for re in "$@"; do
		if ! grep -q -P "$re" "$LOGDIR/err.txt"; then
			result FAIL "$re not found"
			return 1
		fi
	done
	if grep -q "Traceback (most recent call last):" "$LOGDIR/err.txt"; then
		result ALMOST "exception raised"
		return 1
	fi
	pass
}

# Run "$@", the result code decide PASS or FAIL
validate_with() {
	if res="$("$@" 2>&1)"; then
		result PASS
	else
		result FAIL "$res"
		return 1
	fi
}

setup() {
	copy README.md chat.json
}

t prompt01 llme hello world "$@" &&
	validate_chat system hello assistant world assistant

# Empty prompts are ignored. not POLA
t prompt02 llme '' "$@" &&
	validate_chat system

t prompt03 llme README.md hello "$@" &&
	validate_chat system '"hello".*README' assistant tool assistant

t prompt04 llme hello README.md "$@" &&
	validate_chat system '"hello".*README' assistant tool assistant

et prompt05 llme /etc/shadow hello "$@" &&
	validate_err "Permission denied"

t prompt06 llme <<<hello world "$@" &&
	validate_chat system '"world".*filename' assistant tool assistant

t prompt07 llme <<<hello "$@" &&
	validate_chat system hello assistant

#  -u, --base-url BASE_URL API base URL [base_url]
et url1 llme -u bad hello "$@" &&
	validate_err "Invalid URL"

et url2 llme -u '' hello "$@" &&
	validate_err "base-url required"

et url3 llme -u http://bad.example.com hello "$@" &&
	validate_err "Failed to resolve"

et url4 llme -u http:// hello "$@" &&
	validate_err "Invalid URL"

et url5 llme -u http://localhost:1 hello "$@" &&
	validate_err "Connection refused"

et url6 llme -u http://google.com hello "$@" &&
	validate_err "404"
et ss-url1 llme '/set base_url=bad' hello "$@" &&
	validate_err "Invalid URL"

#  -m, --model MODEL     Model name [model]
et model1 llme -m bad hello "$@" &&
	validate_err "ERROR" # unfortunately, servers can react differently to this error

t model2 llme -m '' hello "$@" &&
	validate_chat system hello assistant # Should chose a default model

#  --list-models         List available models then exit
t list-models1 llme --list-models &&
	smoke "Models of"
# /models       list available models
t s-models llme /models hello "$@" &&
	smoke "Models of" &&
	validate_chat system hello assistant


#  --api-key API_KEY     The API key [api_key]
t key1 llme --api-key SECRET_KEY hello "$@" &&
	validate_chat system hello assistant

t key2 llme --api-key '' hello "$@" &&
	validate_chat system hello assistant

#  -b, --batch           Run non-interactively. Implicit if stdin is not a tty [batch]
# batch+no prompts = stdin is big prompt
t batch1 llme -b "$@" <<<$'hello\nworld\n' &&
	validate_chat system 'hello.*world' assistant
# no batch+no prompts = stdin lines are prompts
t batch2 llme --no-batch "$@" <<<$'hello\nworld\n' &&
	validate_chat system hello assistant world assistant
# batch+prompts = stdin is data
t batch3 llme -b goodbye "$@" <<<$'hello\nworld\n' &&
	validate_chat system "goodbye.*file" assistant tool assistant
# no batch+prompts = stdin are more prompts
t batch4 llme --no-batch goodbye "$@" <<<$'hello\nworld\n' &&
	validate_chat system goodbye assistant hello assistant world assistant

#  -p, --plain           No colors or tty fanciness. Implicit if stdout is not a tty [plain]
t plain1 llme -p hello "$@" &&
	validate_chat system hello assistant
t plain2 llme --no-plain hello "$@" &&
	smoke $'\e\\[0m'

#  --bulk                Disable stream-mode. Not that useful but it helps debugging APIs [bulk]
t bulk1 llme --bulk hello "$@" &&
	validate_chat system hello assistant

#  -o, --chat-output CHAT_OUTPUT Export the full raw conversation in json
t output1 llme -o tmp.json hello "$@" &&
	validate_with jq . "$WORKDIR/tmp.json"

t output2 llme -o tmp.json -o '' hello "$@" &&
	validate_with [ ! -f "$WORKDIR/tmp.json" ]

et output3 llme -o /bad/file hello "$@" &&
	validate_err "No such file"

# /save FILE    save chat
t s-save1 llme hello '/save tmp.json' world '/save tmp2.json' "$@" &&
	validate_with jq . "$WORKDIR/tmp.json" &&
	validate_with jq . "$WORKDIR/tmp2.json"
t s-save2 llme '/save tmp3.json' hello "$@" &&
	validate_with jq . "$WORKDIR/tmp3.json"
et s-save3 llme '/save' hello "$@" &&
	validate_err "Missing filename"
et s-save4 llme '/save /bad/file' hello "$@" &&
	validate_err "No such file"

#  -i, --chat-input CHAT_INPUT Continue a previous (exported) conversation
t input1 llme -i chat.json world "$@" &&
	validate_chat system hello assistant world assistant

t input2 llme -i chat.json -i '' world "$@" &&
	validate_chat system world assistant

et input3 llme -i /bad/file hello "$@" &&
	validate_err "No such file"
# /load FILE    load chat
t s-load1 llme hello2 '/load chat.json' world '/load chat.json' "$@" &&
	validate_chat 'You are assistant.' hello "I'm assistant."
t s-load2 llme '/load chat.json' world "$@" &&
	validate_chat 'You are assistant.' hello "I'm assistant." world assistant
et s-load3 llme '/load' world "$@" &&
	validate_err "Missing filename"
et s-load4 llme '/load /bad/file' hello "$@" &&
	validate_err "No such file"

#  --export-metrics EXPORT_METRICS Export metrics, usage, etc. in json
t export-metrics1 llme --export-metrics tmp.json hello "$@" &&
	validate_with jq . "$WORKDIR/tmp.json"
et export-metrics2 llme --export-metrics /bad/file hello "$@" &&
	validate_err "No such file"
t export-metrics3 llme --export-metrics tmp.json --export-metrics '' hello "$@" &&
	validate_with [ ! -f "$WORKDIR/tmp.json" ] &&
	validate_chat system hello assistant
# /metrics      list current metrics
t s-metrics llme /metrics hello /metrics "$@" &&
	smoke "message_n: 1" &&
	validate_chat system hello assistant

#  -s, --system SYSTEM_PROMPT System prompt [system_prompt]
t system1 llme -s hello world "$@" &&
	validate_chat hello world assistant

t system2 llme -s '' hello "$@" &&
	validate_chat hello assistant

#  --temperature TEMPERATURE Temperature of predictions [temperature]
t temp1 llme --temperature 0 hello "$@" &&
	validate_chat system hello assistant

et temp2 llme --temperature '' hello "$@" &&
	validate_err 'invalid float value'

et temp3 llme --temperature bad hello "$@" &&
	validate_err 'invalid float value'

#  --tool-mode {markdown,native} How tools and functions are given to the LLM [tool_mode]
t tool-mode1 llme --tool-mode markdown hello "$@" &&
	validate_chat '```' hello assistant
t tool-mode2 llme --tool-mode native hello "$@" &&
	validate_chat system hello assistant # How to test this?
et tool-mode3 llme --tool-mode bad hello "$@" &&
	validate_err 'invalid choice'
et tool-mode4 llme --tool-mode '' hello "$@" &&
	validate_err 'invalid choice'

#  -c, --config CONFIG   Custom configuration files
t config1 llme -c "$ORIGDIR/$TESTDIR/data/config.toml" hello "$@" &&
	validate_chat 'You are assistant.' hello ''
et config2 llme -c bad hello "$@" &&
	validate_err "No such file"
et config3 llme -c '' hello "$@" &&
	validate_err "No such file"
et config4 llme -c chat.json hello "$@" &&
	validate_err "Invalid config file"

#  --list-tools          List available tools then exit
t list-tools1 llme --list-tools hello "$@" &&
	smoke "run_command"
# /tools        list available tools
t s-tools1 llme /tools hello "$@" &&
	smoke "run_command" &&
	validate_chat system hello assistant

#  --dump-config         Print the effective config and quit
t dump-config1 llme --dump-config hello "$@" &&
	smoke '"dump_config": true'
# /config       list configuration options
t s-config1 llme '/config' hello "$@" &&
	smoke 'base_url' &&
	validate_chat system hello assistant

#  --plugin PLUGINS      Add additional tool (python file or directory) [plugins]
t plugin1 llme --plugin "$ORIGDIR/$TESTDIR/../examples/weather_plugin.py" hello "$@" &&
	validate_chat system hello assistant
t plugin1b llme --list-tools --plugin "$ORIGDIR/$TESTDIR/../examples/weather_plugin.py" hello "$@" &&
	smoke 'weather(city: str)'
t plugin2 llme --plugin "$ORIGDIR/$TESTDIR/../examples" hello "$@" &&
	validate_chat system hello assistant
t plugin2b llme --list-tools --plugin "$ORIGDIR/$TESTDIR/../examples" hello "$@" &&
	smoke 'weather(city: str)'
et plugin3 llme --plugin bad hello "$@" &&
	validate_err "No such file"

#  -v, --verbose         Increase verbosity level (can be used multiple times)
t verbose1 llme -v hello "$@" &&
	validate_err "level set to INFO"
t verbose2 llme -vv hello "$@" &&
	validate_err "level set to DEBUG"
t verbose3 llme -vvv hello "$@" &&
	validate_err "level set to DEBUG"
t ss-verbose1 llme '/set verbose=1' hello "$@"

#  --log-file LOG_FILE   Write logs to a file [log_file]
t log-file1 llme --log-file tmp.log hello "$@" &&
	validate_with grep -q 'llme - DEBUG' "$WORKDIR/tmp.log"
et log-file2 llme --log-file /bad/file hello "$@" &&
	validate_err "No such file"

#  -Y, --yolo            UNSAFE: Do not ask for confirmation before running tools. Combine with --batch to reach the singularity.
t yolo1 llme --yolo hello "$@" &&
	validate_chat system hello assistant

#  --version             Display version information and quit
t version1 llme --version hello "$@" &&
	smoke 'v[0-9]'

# --help
t help1 llme --help "$@" &&
	smoke "usage: llme"

# --dummy
t dummy1 llme --dummy hello "$@" &&
	validate_chat system hello "I'm assistant."
t dummy2 llme --dummy --list-models "$@" &&
	smoke dummy
t dummy3 llme -u bad --dummy hello "$@" &&
	validate_chat system hello "I'm assistant."

# args
t args0 llme "$@" < /dev/null &&
	pass
# prefix
t args1 llme --verbo hello "$@" &&
	validate_err "level set to INFO"
et args2 llme --bad hello "$@" &&
	validate_err "unrecognized argument"
t args3 llme --no-version hello "$@" &&
	validate_chat system hello assistant
et s-set1 llme '/set bad=bad' hello "$@" &&
	validate_err "Unknown setting"
et s-set2 llme '/set bad' hello "$@" &&
	validate_err "Syntax error"
et s-set3 llme '/set' hello "$@" &&
	validate_err "Missing setting"
# prefix
t slash1 llme /he hello "$@" &&
	smoke "list available models"
et slash2 llme /bad hello "$@" &&
	validate_err "Unknown slash command"
et slash3 llme / hello "$@" &&
	validate_err "Is a directory" # / is the root directory

# /quit         exit the program
t s-quit llme /quit hello "$@" &&
	validate_chat system

# /help         show this help
t s-help llme /help hello "$@" &&
	smoke "list available models"

# /redo        cancel and regenerate the last assistant message
t s-redo1 llme hello /redo world /redo "$@" &&
	validate_chat system hello assistant world assistant # hum how to test that
t s-redo2 llme hello /redo /redo "$@" &&
	validate_chat system hello assistant
et s-redo3 llme /redo hello "$@" &&
	validate_err "No assistant message to redo"

# /undo         cancel the last user message (and the response)
t s-undo1 llme hello /undo world /undo "$@" &&
	validate_chat system world assistant

et s-undo2 llme /undo hello "$@" &&
	validate_err "No user message to undo"

# /pass         go forward in history (cancel /undo) [PageDown]
t s-pass1 llme hello /undo /pass world "$@" &&
	validate_chat system hello assistant world assistant
et s-pass2 llme /pass hello "$@" &&
	validate_err "Already at latest message"

# /goto M       jump after message M (e.g /goto 5c)
t s-goto00 llme hello world "/goto 0" goodbye "$@" &&
	validate_chat goodbye assistant
t s-goto01 llme hello world "/goto 1" goodbye "$@" &&
	validate_chat system goodbye assistant
t s-goto02 llme hello world "/goto 2" goodbye "$@" &&
	validate_chat system hello assistant goodbye assistant
t s-goto03 llme hello world "/goto 3" goodbye "$@" &&
	validate_chat system hello assistant goodbye assistant
t s-goto04 llme hello world "/goto 4" goodbye "$@" &&
	validate_chat system hello assistant world assistant goodbye assistant
t s-goto10 llme hello /undo world "/goto 2a" "$@" &&
	validate_chat system hello assistant
et s-goto12 llme hello /undo world "/goto" "$@" &&
	validate_err "Missing message label"
et s-goto13 llme hello /undo world "/goto bad" "$@" &&
	validate_err "Invalid message label"
et s-goto14 llme hello world "/goto 42" goodbye "$@" &&
	validate_err "Message 42 not found"

# /history      list condensed conversation history
t s-history1 llme hello /history "$@" &&
	smoke "1 user: hello" &&
	validate_chat system hello assistant

t s-history2 llme hello /undo world /history "$@" &&
	smoke "1 user: world" &&
	validate_chat system world assistant

# /full-history list hierarchical conversation history (with forks)
t s-full-history1 llme hello /full-history "$@" &&
	smoke "1a user: hello" &&
	validate_chat system hello assistant

t s-full-history2 llme hello /undo world /full-history "$@" &&
	smoke "1a user: hello" "1b user: world" &&
	validate_chat system world assistant

# /edit         run EDITOR on the chat (save,editor,load)
export EDITOR="sed -i 's/hello/world/'"
t s-edit1 llme hello /edit hello "$@" &&
	validate_chat system world assistant hello assistant
export EDITOR="sed -i 's/hello/world/'"
t s-edit2 llme --system=hello /edit hello2 "$@" &&
	validate_chat world hello2 assistant
export EDITOR="false"
et s-edit3 llme /edit hello "$@" &&
	validate_err "returned non-zero exit"
export EDITOR="/bad/name"
et s-edit4 llme hello /edit "$@" &&
	validate_err "No such file"
export EDITOR="echo 'badquote"
et s-edit5 llme hello /edit "$@" &&
	validate_err "Invalid editor command"
