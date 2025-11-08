#!/bin/bash

. "$(dirname "$0")/utils.sh"

setup() {
	copy README.md
}

tllme "01" "What is the capital of France?" "$@" &&
	smoke paris
tllme "02" "What is the capital of France?" "What about Canada?" "And Vatican?" "And Mordor?" "And my axe?" "$@" &&
	smoke 'tolkien\|middle\|sauron'
tllme "03" "What the content on the current directory?" "$@" &&
	smoke 'ls\|ll\|README'
tllme "04" "What is the current operating system?" "$@" &&
	smoke 'uname\|linux'
tllme "05" "What is the factorial of 153?" "$@" &&
	smoke 'factorial\|153\|200634390509568239477828874698911718566246149616161171934231099284840946025238092339613294062603588435530393145048663047173051913507711632216305667129554900620296603188543122491838966881134795135997316305640071571629943041039657861120000000000000000000000000000000000000'
tllme "06" <<<"What is the capital of France?" "$@" &&
	smoke paris

tllme "10" "Summarize the file README.md in one sentence" "$@" &&
	smoke llm
tllme "11" "Summarize the file in one sentence" "$@" < "$TESTDIR/data/README.md" &&
	smoke llm
tllme "12" README.md "Summarize the file in one sentence" "$@" &&
	smoke llm
tllme "13" "Summarize the file in one sentence" "$@" README.md &&
	smoke llm

tllme "31" bonjour "exécute la commande uptime" "calcule la factorielle de 10" "résume en 10 (dix) mots le fichier" README.md "$@" &&
	smoke llm

tllme "32" "Tell me a joke about LLMs" "$@" &&
	smoke 'llm\|ai\|gpt'
lastchat=$ORIGDIR/$LOGDIR/chat.json
tllme "33" -i "$lastchat" "What is the joke about?" "$@" &&
	smoke 'llm\|ai\|gpt'
