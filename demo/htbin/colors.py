#!/usr/bin/python3
import sys
import cgi

form = cgi.FieldStorage()

bgcolor = form["bgcolor"].value
titlecolor = form["titlecolor"].value
textcolor = form["textcolor"].value

with open("colors.txt", 'w') as data:
    data.write(bgcolor + "\n" + titlecolor + "\n" + textcolor + "\n")
    data.close()

with open("maintemplate.css", "r") as template:
    with open("main.css", "w") as maincss:
        css = template.read()
        css = css.replace("black", bgcolor)
        css = css.replace("#f6f2f7", titlecolor)
        css = css.replace("#f7e9fa", textcolor)
        maincss.write(css)
        maincss.close()
    template.close()

print("Access-Control-Allow-Origin: *\r\n")