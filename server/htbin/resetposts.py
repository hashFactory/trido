#!/usr/bin/python3
import cgi
import shutil, os

# import ssg script
import process as sp

# reset output dir
sp.read_site_map("site.map")
sp.settings['output_dir'] = ''

# delete posts and replace with originals
shutil.rmtree('content/postmaps/')
shutil.rmtree('content/posts/')
os.mkdir('content/posts/')
shutil.copytree('content/defaultposts/', 'content/postmaps')

# regenerate html pages
sp.post_map_to_html(postmaps_dir="content/postmaps/")
sp.generate_home_page()

# return empty response
print("Access-Control-Allow-Origin: *")
print("Content-Type: text/html\r\n")
print(open('home.html').read())