#!/bin/bash

. "$(dirname "$0")/utils.sh"

setup() {
	copy fib.c
}

validate() {
	cd "$WORKDIR"
	if ! gcc fib.c -o fib; then
		result FAIL "cannot compile"
	elif ! res=$(timeout 10 ./fib); then
		result FAIL "cannot execute"
	elif echo "$res" | grep --color 512; then
		result FAIL "unfixed"
	elif ! echo "$res" | grep --color 610; then
		echo "$res"
		result FAIL "cannot fib"
	else
		result PASS
	fi
}

tllme 01 "The fib.c program prints 512 instead of 610. The assignment \`a=b;\` is too late. Fix fit.c, compile it and run it." "$@" &&
validate

tllme 02 "Compile and run fib.c" "Cat fib.c" "Spot the error" "Fix the error" "Compile it and run it again" "$@" &&
validate

tllme 02b "Compile and run fib.c. Cat fib.c. Spot the error. Fix the error. Compile it and run it again" "$@" &&
validate

tllme 03 "Run and analyze fib.c. Explain the bug. Explain how to fix it, then fix it. Run fib.c to show that the bug is fixed." "$@" &&
validate

tllme 04 "Fix fib.c" "$@" &&
validate

tllme 05 "Fix possible issues in ." "$@" &&
validate
