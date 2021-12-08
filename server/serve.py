#!/usr/bin/python3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer, CGIHTTPRequestHandler
from process import *
import urllib.parse

# create server instance
trido = Trido(site_map='site.map')

class ProjectRequestHandler(CGIHTTPRequestHandler):

    # responds by replying with file content
    def respond_with(self, out, filename, contenttype=""):
        self.send_response(200)
        if contenttype != "":
            self.send_header("Content-type", contenttype)
        self.end_headers()
        with open(filename, 'rb') as h:
            out(h.read())
        self.log_message("Responded to " + self.path + " with " + filename)

    def address_string(self) -> str:
        return trido.s["hostname"]

    # handle get requests
    def do_GET(self):
        out = self.wfile.write
        request = parse.urlparse(self.path)

        if self.path == '/' or self.path.endswith('.py'):
            self.respond_with(out, 'content/home.html', 'text/html')
        #if request.pa
        elif "/user/" in self.path:
            self.respond_with(out, 'content/' + request.path.split("/")[-1] + '.html')
        else:
            SimpleHTTPRequestHandler.do_GET(self)

    # handle post
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])

        if self.headers['Content-Type'] == "application/x-www-form-urlencoded":
            post_data = self.rfile.read(content_length)
            #self.log_message("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
            #                 str(self.path), str(self.headers), str(post_data.decode('utf-8')))

            form = urllib.parse.parse_qs(post_data.decode('utf-8'))
            user, filename = trido.parse_api(self.path)
            redirect = trido.handle_post_request((user, filename), form)

            self.send_response(303)
            self.send_header("Location", trido.s['server'] + redirect)
            self.end_headers()
            # self.send_response_only()

if __name__ == '__main__':
    address = (trido.s["hostname"], trido.s["port"])

    with ThreadingHTTPServer(address, ProjectRequestHandler) as httpd:
        #try:
        # init server
        trido.s['output_dir'] = ''
        trido.init_users()

        post_map_dirs = [trido.s['users_dir'] + d + "/postmaps/" for d in os.listdir(trido.s['users_dir'])]
        for d in post_map_dirs:
            trido.post_maps_to_html(d)

        trido.generate_user_homepages()
        trido.generate_home_page()

        # inform user
        print("Serving on " + trido.s["server"])
        httpd.serve_forever()
