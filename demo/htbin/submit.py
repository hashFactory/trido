#!/usr/bin/python3
import sys
import cgitb
cgitb.enable()

content = sys.stdin.read()
#content = "testing testing"
with open('template.html', 'r') as t:
    with open('components.html', 'w') as components:
        template = t.read()
        template = template.replace("|REPLACEME|", content)
        components.write(template)
        components.close()
    t.close()

print("Access-Control-Allow-Origin: *\r\n")
print("Content-type: text/html\r\n")
print("<html>HELLO!</html>")