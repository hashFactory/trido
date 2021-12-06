#!/usr/bin/python3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer, CGIHTTPRequestHandler
from process import *
import urllib.parse

# create server instance
trido = Trido(site_map='site.map')

class ProjectRequestHandler(CGIHTTPRequestHandler):
    # handle get requests
    def do_GET(self):
        out = self.wfile.write
        if self.path == '/' or self.path.endswith('.py'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open('home.html', 'rb') as h:
                out(h.read())
        else:
            SimpleHTTPRequestHandler.do_GET(self)

    # handle post
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])

        if self.headers['Content-Type'] == "application/x-www-form-urlencoded":
            post_data = self.rfile.read(content_length)
            self.log_message("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                             str(self.path), str(self.headers), str(post_data.decode('utf-8')))

            form = urllib.parse.parse_qs(post_data.decode('utf-8'))
            filename = os.path.split(self.path)[1]
            trido.handle_post(filename, form)

            self.send_response(303)
            self.send_header("Location", trido.s['server'])
            self.end_headers()
            # self.send_response_only()

if __name__ == '__main__':
    address = (trido.s["hostname"], trido.s["port"])

    with ThreadingHTTPServer(address, ProjectRequestHandler) as httpd:
        try:
            # init server
            trido.s['output_dir'] = ''
            trido.post_maps_to_html()
            trido.generate_home_page()

            # inform user
            print("")
            httpd.serve_forever()
        except:
            print("The server crashed!")
