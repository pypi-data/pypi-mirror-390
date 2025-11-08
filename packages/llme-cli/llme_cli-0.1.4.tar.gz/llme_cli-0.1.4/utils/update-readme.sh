#!/bin/bash

set -e
{
sed -n '1,/^<!--help-->$/p' README.md
echo '```console'
echo '$ llme --help'
llme --help
echo '```'
sed -n '/^<!--\/help-->$/,/^<!--slash-help-->$/p' README.md
echo '```console'
echo '$ llme /help /quit'
llme /help /quit
echo '```'
sed -n '/^<!--\/slash-help-->$/,$p' README.md
} > README.new.md
mv README.new.md README.md
git add README.md

llme --temperature 1.5 'cat ./README.md. Improve it: make it more eye-candy, punchy and awesome. Rephrase sentences to make them more complex and techno-babble. Decorate with influencing emojis. Target LLM enthusiasts and vibe-coders. Move, add of remove sections. Be creative and unhinged. Write the new version of the file with: cat > README.vibe.md'
