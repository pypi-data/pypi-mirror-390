#!/bin/bash

# Common setup and useful functions for test scripts

export SUITE=$(basename "$0" .sh)
export TESTDIR=$(dirname "$0")
export ORIGDIR=`pwd`
export UTILDATE=${UTILDATE:-`date +%s`} # so all runs from a same initial script share a same utildate
export UTILID=${UTILID:-$UTILDATE-$$-$RANDOM} # so all runs from a same initial script share a same utilid

# The llme tool to check
LLME="llme"
if ! command -v "$LLME" >/dev/null; then
	echo "llme not found: $LLME" >&2
	exit 1
fi

# run before each test. override if needed
setup() {
	true
}

# run after each test. override if needed
teardown() {
	true
}

# copy files from data to the workdir
copy() {
	for f in "$@"; do
		cp -r "$TESTDIR/data/$f" "$WORKDIR/"
	done
}

# escape $1 as a json string ("" included)
jsonescape() {
	jq -Rn --arg str "$1" '$str'
}


# Register a test result
result() {
	config="$ORIGDIR/$LOGDIR/config.json"
	if [ -f "$config" ]; then
		url=`jq -r .base_url "$config"`
		model=`jq -r .model "$config"`
	else
		url=
		model=
	fi
	chat="$ORIGDIR/$LOGDIR/chat.json"
	if [ -f "$chat" ]; then
		msgs=`jq '.|length' "$chat"`
		words=`wc -w < "$chat"`
	else
		msgs=
		words=
	fi

	cat > "$ORIGDIR/$LOGDIR/result.json" <<-EOF
	{
		"result":$(jsonescape "$1"),
		"comment":$(jsonescape "$2"),
		"msgs":${msgs:-null},
		"words":${words:-null},
		"task":"$task",
		"suite":"$SUITE",
		"utildate":$UTILDATE,
		"date":`date +%s`,
		"path":"$LOGDIR",
		"git-version":"`git -C "$ORIGDIR/$TESTDIR" describe --tags --dirty`",
		"llme-version":"`"$LLME" --version`"
	}
	EOF
	case $1 in
		ERROR*|FAIL*|TIMEOUT*)
			color=91;;
		PASS*)
			color=92;;
		RUNNING*)
			color=94;;
		*)
			color=93;;
	esac
	printf "\e[${color}m$1\e[0m "
	echo "$2 $LOGDIR/ model=$model msgs=$msgs words=$words"
}

# Check that the llm result matches the pattern $1 on the last line.
answer() {
	if jq -r '.[-1].content' "$LOGDIR/chat.json" | sed '/^$/d' | tail -n1 | grep -x "$1"; then
		result "PASS"
	elif grep --color=always -i "$1" "$LOGDIR/out.txt" > >(head); then
		result "ALMOST"
	else
		result "FAIL"
	fi
}

# Check that the llm result talk about a pattern
smoke() {
	for re in "$@"; do
		if ! grep --color=always -i "$re" "$LOGDIR/out.txt" > >(head); then
			result "FAIL"
			return 1
		fi
	done
	result "PASS"
}

# Run a command in its workdir with a fresh python environment if available.
runllme() {
	# verbose mode
	if [ -z "$V" ]; then
		out=/dev/null
	else
		out=/dev/stdout
	fi

	(
	set -e
	cd "$WORKDIR"
	if [ -f venv ]; then
		. venv/bin/activate
	fi
	setsid timeout -v -f -sINT 180 "$@"
	) 2> >(tee -a "$LOGDIR/err.txt" > "$out") > >(tee -a "$LOGDIR/out.txt" > "$out")
}

# Create LOGDIR and WORKDIR.
# And initialize other env variables
prepare() {
	task=$1
	shift

	if [ -n "$F" ] && echo "$task" | grep -qv "$F"; then
		return 1
	fi

	cd "$ORIGDIR"

	# Tests results are stored in logs/$id/ where id is a unique identifier
	id=$SUITE-$task-$(date +%s)
	export LOGDIR="logs/$UTILID/$id"
	mkdir -p "$LOGDIR"
	env | grep "^LLME_" > "$LOGDIR/env.txt"

	export LLME_CHAT_OUTPUT=$ORIGDIR/$LOGDIR/chat.json
	export LLME_EXPORT_METRICS=$ORIGDIR/$LOGDIR/metrics.json
	export LLME_LOG_FILE=$ORIGDIR/$LOGDIR/log.txt
	export LLME_BATCH=true
	export LLME_YOLO=true

	# create a tmp workdir
	if [ -z "$WORKDIR" ] || [ -z "$KEEPWORKDIR" ]; then
		WORKDIR=`mktemp --tmpdir -d llme-XXXXX`
	fi
	ln -s "$WORKDIR" "$LOGDIR/workdir"
}

# Shortcut for result PASS
pass() {
	result PASS
}

# Shortcut for result ERROR/TIMEOUT.
# $1 the error code
checkerr() {
	err=$1
	if [ "$err" -eq 124 ]; then
		result "TIMEOUT"
		return 124
	elif [ "$err" -ne 0 ]; then
		grep --color -i error "$LOGDIR/out.txt"
		result "ERROR" "$(tail -n 1 "$LOGDIR/err.txt")"
		return $err
	fi
}

# Run a basic test with a command
# Usage: t taskname [cmd args]...
t() {
	prepare "$@" || return
	shift
	setup
	echo
	result "RUNNING"
	runllme "$@"
	err=$?
	teardown
	checkerr "$err"
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


# Run a test with the llme tool
# Usage: tllme taskname [llme args...] (use "$@" for args)
#
# define '$V' for verbose
# define '$F' to filter tests
# define '$KEEPWORKDIR' to reuse the workdir in subsequent tests
tllme() {
	prepare "$@" || return
	shift

	setup

	if ! "$LLME" "$@" --dump-config > "$LOGDIR/config.json"; then
		result "ERROR" "can't get config"
		return 1
	fi

	(cd "$WORKDIR" && python3 -m venv venv)

	echo
	result "RUNNING"

	runllme "$LLME" "$@"
	err=$?

	teardown

	if [ "$err" -eq 124 ]; then
		result "TIMEOUT"
		return 124
	elif [ "$err" -ne 0 ]; then
		grep --color -i error "$LOGDIR/out.txt"
		result "ERROR" "$(tail -n 1 "$LOGDIR/err.txt")"
		return $err
	fi

	return 0
}
