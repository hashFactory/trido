#!/usr/bin/python3
import sys
import cgi
import cgitb
cgitb.enable()
import json
import process as sp

form = cgi.FieldStorage()
colors = {}

colors["|BGCOLOR|"] = form["bgcolor"].value
colors["|TITLECOLOR|"] = form["titlecolor"].value
colors["|TEXTCOLOR|"] = form["textcolor"].value
colors["|BOXCOLOR|"] = form["boxcolor"].value

with open("primitives/colors.map", 'w') as data:
    json.dump(dict(colors), data)
    data.close()

sp.read_site_map('site.map')
sp.settings['output_dir'] = ''
sp.post_map_to_html(postmaps_dir="content/postmaps/")
sp.generate_home_page()

print("Access-Control-Allow-Origin: *")
print("Content-Type: text/html\r\n")
print(open('home.html').read())