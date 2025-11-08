#!/usr/bin/env python3
import os
import re
import secrets

with open("CHANGELOG.md", "r", encoding="utf-8") as f:
    content = f.read()

matches = re.findall(r"(## \[v[\d\.]+\].*?)(?=## \[v|\Z)", content, re.DOTALL)
latest = matches[0].strip() if matches else "No changelog entry found."

gh_out = os.environ.get("GITHUB_OUTPUT")
if gh_out:
    delim = f"EOF_{secrets.token_hex(8)}"
    with open(gh_out, "a", encoding="utf-8") as f:
        f.write(f"changelog<<{delim}\n{latest}\n{delim}\n")
else:
    print(latest)
