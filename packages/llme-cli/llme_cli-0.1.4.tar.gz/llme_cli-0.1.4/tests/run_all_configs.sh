#!/bin/bash

# Usage: run_all_configs.sh <testsuite.sh> [llme args...]
# Run all models in parallel for all config files

. "$(dirname "$0")/utils.sh"

testsuite=$1
shift

configs=()
for config in *.toml; do
	[ "$config" = "pyproject.toml" ] && continue
	configs+=("`pwd`/$config")
done
echo "configs: ${configs[@]}"
parallel "$TESTDIR/run_all_models.sh" "$testsuite" "$@" -c -- "${configs[@]}"
