
from http.server import SimpleHTTPRequestHandler, HTTPServer, CGIHTTPRequestHandler

port = 8003
address = ('', port)

class projectServerHandler(CGIHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        if self.path == '/omponents.html' or self.path == '/':
            with open('components2.html') as c:
                c.read()
                with open('contents.html') as con:
                    print('efwef')
        else:
            CGIHTTPRequestHandler(self)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        with open('contents.html', mode='w') as c:
            c.write(post_data)
            c.close()

if __name__ == '__main__':
    #try:
    httpd = HTTPServer(address, projectServerHandler, port)
    httpd.serve_forever()
    #except KeyboardInterrupt:
    #    pass
    #httpd.server_close()