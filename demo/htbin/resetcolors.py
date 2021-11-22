#!/usr/bin/python3
import sys
import cgi

with open("maintemplate.css", "r") as template:
    with open("main.css", "w") as maincss:
        css = template.read()
        maincss.write(css)
        maincss.close()
    template.close()

print("Access-Control-Allow-Origin: *\r\n")