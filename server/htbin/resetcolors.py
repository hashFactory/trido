#!/usr/bin/python3
import sys
import cgi

import json
import process as sp

with open("primitives/defaultcolors.map", 'r') as defaultcolors:
    with open("primitives/colors.map", 'w') as data:
        json.dump(json.load(defaultcolors), data)

sp.read_site_map('site.map')
sp.settings['output_dir'] = ''
sp.post_map_to_html(postmaps_dir="content/postmaps/")
sp.generate_home_page()

print("Access-Control-Allow-Origin: *")
print("Content-Type: text/html\r\n")
print(open('home.html').read())