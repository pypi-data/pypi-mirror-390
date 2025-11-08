#!/bin/bash

mkdir -p logs.bak
for f in $(grep "$1" logs/*/config.json -l); do
	d=$(dirname "$f")
	if [ ! -d "$d" ]; then
		continue
	fi
	echo $d `jq -c '[.base_url,.model]' $d/config.json`
	mv "$d" logs.bak
done
