#!/bin/bash

. "$(dirname "$0")/utils.sh"

setup() {
	copy README.md pyproject.toml
}

validate_file() {
if diff -u "$TESTDIR/data/$1.expected" "$WORKDIR/$1"; then
	result PASS
else
	result FAIL
fi
}

validate() {
	validate_file README.md
}

tllme 00free "Look at the README.md file and change 'CLI' in the title to 'command line'. Do not change anything else." "$@" &&
validate

tllme 01cat "Look at the README.md file and change 'CLI' in the title to 'command line'. Do not change anything else. Use cat to update the file." "$@" &&
validate

tllme 02sed "Look at the README.md file and change 'CLI' in the title to 'command line'. Do not change anything else. Use sed to update the file." "$@" &&
validate

tllme 03patch "Look at the README.md file and change 'CLI' in the title to 'command line'. Do not change anything else. Use patch to update the file." "$@" &&
validate

tllme 04ed "Look at the README.md file and change 'CLI' in the title to 'command line'. Do not change anything else. Use ed to update the file." "$@" &&
validate

tllme 05python "Look at the README.md file and change 'CLI' in the title to 'command line'. Do not change anything else. Use python to update the file." "$@" &&
validate

validate() {
	validate_file pyproject.toml
}

tllme 10free "swap the order of 'dependencies' and 'classifiers' settings in the file pyproject.toml. Do not do any other changes." "$@" && 
validate

tllme 11cat "swap the order of 'dependencies' and 'classifiers' settings in the file pyproject.toml. Do not do any other changes. Use cat to update the file." "$@" && 
validate

tllme 12sed "Swap the order of 'dependencies' and 'classifiers' settings in the file pyproject.toml. Do not do any other changes. Use sed to update the file." "$@" && 
validate

tllme 13patch "Swap the order of 'dependencies' and 'classifiers' settings in the file pyproject.toml. Do not do any other changes. Use patch to update the file." "$@" && 
validate

tllme 14ed "Swap the order of 'dependencies' and 'classifiers' settings in the file pyproject.toml. Do not do any other changes. Use ed to update the file." "$@" && 
validate

tllme 15python "Swap the order of 'dependencies' and 'classifiers' settings in the file pyproject.toml. Do not do any other changes. Use python to update the file." "$@" && 
validate
