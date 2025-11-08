#!/bin/bash

. "$(dirname "$0")/utils.sh"

setup() {
	copy image.jpg
}

tllme "0" "What is in this image?" "$@" < "$TESTDIR/data/image.jpg" &&
	smoke 'building\|window\|winter\|snow'
tllme "1" image.jpg "What is in this image?" "$@" &&
	smoke 'building\|window\|winter\|snow'
tllme "2" "What is in this image?" image.jpg "$@" &&
	smoke 'building\|window\|winter\|snow'
tllme "3" "What is in this image? image.jpg" "$@" &&
	smoke 'building\|window\|winter\|snow'

tllme "4" "What is in this image?" image.jpg "Is this image similar to the previous one?" image.jpg "$@" &&
	smoke 'similar\|duplicate\|related\|same'
