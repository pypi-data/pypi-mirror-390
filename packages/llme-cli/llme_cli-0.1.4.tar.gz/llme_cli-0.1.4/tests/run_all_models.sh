#!/bin/bash

# Usage: run_all_models.sh <testsuite.sh> [llme args...]
# Run testsuite on all available models in the base_url (the specified model is ignored)

. "$(dirname "$0")/utils.sh"

testsuite=$1
shift

url=`$LLME "$@" --dump-config | jq -r '.base_url'`
echo "url: $url"

models=`curl -s "$url/models" | jq '.. | .id? | select(. != null)' -r`
models=`echo $models`

echo "models: $models"
for model in $models; do
    echo "Model: $model - Test suite: $testsuite"
    "$testsuite" "$@" -m "$model"
done
