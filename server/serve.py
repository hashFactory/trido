#!/usr/bin/python3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer, CGIHTTPRequestHandler
from process import *
import urllib.parse

port = 8890
address = ('192.168.1.17', port)

trido = Trido(site_map='site.map')
trido.read_site_map('site.map')
trido.s['output_dir'] = ''
trido.post_maps_to_html()
trido.generate_home_page()

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
            
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(open('home.html', 'rb').read())

if __name__ == '__main__':
    with ThreadingHTTPServer(address, ProjectRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except:
            print("Failed")