#!/bin/bash

KEEPWORKDIR=true
. "$(dirname "$0")/utils.sh"

setup() {
	# each test continue the previous one
	LLME_INPUT_CHAT=$ORIGDIR/$LOGDIR/chat.json
	test -f "$LLME_INPUT_CHAT" && export LLME_INPUT_CHAT
}

if tllme 01world "Write a Python program, hello.py, that prints 'Hello World'" "$@"; then
	cd "$WORKDIR"
	if [ ! -f hello.py ]; then
		result "FAIL" nofile
	elif ! python3 hello.py; then
		result "FAIL" norun
	elif [ ! "$(python3 hello.py)" = "Hello World" ]; then
		result "FAIL" nohello
	else
		result "PASS"
	fi
fi

if tllme 02name "Modify hello.py so that it print 'Hello NAME', where NAME is the name of the user, that is given as an argument of the program." "$@"; then
	cd "$WORKDIR"
	if [ ! -f hello.py ]; then
		result "FAIL" nofile
	elif ! python3 hello.py Monde; then
		result "FAIL" norun
	elif [ ! "$(python3 hello.py Monde)" = "Hello Monde" ]; then
		result "FAIL" nohello
	else
		result "PASS"
	fi
fi	

if tllme 03git "git init the current directory, and commit hello.py" "$@"; then
	cd "$WORKDIR"
	if [ ! -d .git ]; then
		result FAIL nogit
	elif [ ! "`git log --oneline | wc -l`" -eq 1 ]; then
		result FAIL not1commit
	else
		result PASS
	fi
fi

if tllme 04gitignore "keep the directory clean and create a gitignore. do not forget to commit" "$@"; then
	cd "$WORKDIR"
	if [ ! -f .gitignore ]; then
		result FAIL nogitignore
	elif [ ! "`git log --oneline | wc -l`" -eq 2 ]; then
		result FAIL not2commits
	elif [ -n "$(git status --porcelain)" ]; then
		result FAIL noclean
	else
		result PASS
	fi
fi
