#!/usr/bin/python

from lxml import html
import json

# Put POSTBIN URL here
# POSTBIN_URL =
postbin = html.parse(POSTBIN_URL)

posts = postbin.getroot().find_class("post")

for p in posts:
    content = p.text_content()
    start = content.index("{")
    json_content = json.loads(content[start:])
    name = json_content[u'after']
    with open(name + ".json", "w") as f:
        json.dump(json_content, f, indent=1)
