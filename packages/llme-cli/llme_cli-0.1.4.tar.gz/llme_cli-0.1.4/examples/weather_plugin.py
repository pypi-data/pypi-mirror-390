#!/usr/bin/env python3

"""This a an example of a LLME plugin that offers a custom-tool.
The module is also usable as a stand-alone CLI tool."""

import requests
import urllib


# The important part :)
import llme


# The @llme.tool decoration teach LLME to use a function as a tool. Ensure that the information the LLM gets are usable
# * the fuction name
# * the documentation
# * the parameter names, type (str and int), and default value
@llme.tool
def weather(city: str):
    """Return the weather and forecast of a given city"""
    print(f"LLM asked for {city}")
    url = f"http://wttr.in/{urllib.parse.quote(city)}?format=j1"
    with llme.Spinner("red"):
        response = requests.get(url=url)
    response.raise_for_status()
    return response.text


if __name__ == "__main__":
    # Keep only the weather tool (API might improve)
    llme.all_tools = {"weather": llme.all_tools["weather"]}
    # This just run the LLME entry point
    llme.main()
