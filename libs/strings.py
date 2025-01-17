"""
libs.strings

By default, uses `en-gb.json` file inside the `strings` top-level folder.

If language changes, set `libs.strings.default_locale` and run `libs.strings.refresh()`.
"""
import json

default_locale = 'en-gb'
cached_strings = {}


def refresh():
    global cached_strings
    with open(f'strings/{default_locale}.json') as f:
        cached_strings = json.loads(f)


def gettext(name):
    return cached_strings.get(name, '')

refresh()

