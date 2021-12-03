#!/usr/bin/python3
import cgi

# import ssg script
import process as sp
sp.read_site_map("site.map")
sp.settings['output_dir'] = ''

# populate form fields
form = cgi.FieldStorage()

title = form["title"].value
userid = form["userid"].value
content = form["content"].value

# create and save new post
np = sp.Post(userid, title, content)
np.to_post_map()
np.to_html()

# regenerate html pages
sp.post_map_to_html(postmaps_dir="content/postmaps/")
sp.generate_home_page()

# give whole page response
print("Access-Control-Allow-Origin: *")
print("Content-Type: text/html\r\n")
print(open('home.html').read())