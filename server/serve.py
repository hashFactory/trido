#!/usr/bin/python3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer, CGIHTTPRequestHandler
from process import *
import urllib.parse
import ssl

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
        user, filename = trido.parse_api(self.path)
        redirect = ""

        #if 'multipart/form-data' in self.headers['Content-Type']:
        if 'upload' in self.path:
            #post_data = self.rfile.read(content_length)
            #print("Found content length: " + str(content_length))
            #m = email.message_from_bytes(post_data)
            #m = email.parser.BytesParser().parsebytes(post_data, self.headers)
            #g = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'})
            #foundit = False
            # compute offsets for reading file contents from post body
            wasted_header = self.headers['Content-Type'].split(";")[1]
            temp_filename = wasted_header.split('-')[-1]
            location = "assets/" + user + "/"
            waste = len(wasted_header)
            print(location + temp_filename)

            # write out entire post body
            with open(location + temp_filename + ".temp", "wb") as o:
                #line = ""
                """while not foundit:
                    line = self.rfile.readline()
                    if line.startswith(bytes('Content-Type', 'utf-8')):
                        foundit = True"""
                # read in entire file from self.rfile fp
                while o.tell() < content_length:
                    o.write(self.rfile.read(10 ** 6))
                    o.flush()
                print("wrote " + str(o.tell()) + " bytes")

            # reopen in read mode
            with open(location + temp_filename + ".temp", "rb") as o:
                #print("wfuhse")
                """
                c_type, p_dict = cgi.parse_header(self.headers.get('Content-Type'))
                p_dict['boundary'] = bytes(p_dict['boundary'], "utf-8")
                if c_type == 'multipart/form-data':
                    fields = cgi.FieldStorage(self.rfile, p_dict)
                    filenum = 1
                    for file in fields['file']:
                        with open("output_file_" + str(filenum) + ".png", "wb") as f:
                            f.write(file)
                        filenum = filenum + 1
                    print("fields: " + str(len(fields['file'][0])))
                """
                #line = ""
                foundit = False
                #new_filename = temp_filename
                while not foundit:
                    line = o.readline()
                    # get filename
                    if line.startswith(bytes('Content-Disposition', 'utf-8')):
                        upload_filename = str(line.split(b'\"')[1::2][-1], 'utf-8')
                        print("Found \"" + str(upload_filename) + "\" filename")
                    #    new_filename = line.split(";")
                    # find last header
                    if line.startswith(bytes('Content-Type', 'utf-8')):
                        foundit = True
                # skip one more line to get to file contents
                o.readline()
                # write out file contents
                with open(location + upload_filename, 'wb') as f2:
                    length = (content_length - waste) - o.tell()
                    while length > 0:
                        amount = min(length, 10 ** 6)
                        f2.write(o.read(amount))
                        length -= amount

            # delete temp
            os.remove(location + temp_filename + ".temp")
            # handle api request
            redirect = trido.handle_post_request((user, filename), {'bgurl': list([user + "/" + upload_filename])})
            if "uploadfile.py" == filename:
                #self.send_response(200)
                self.send_response(200)
                self.send_header("Content-type", 'text/html')
                self.end_headers()
                self.wfile.write(bytes("<p style=\"position: absolute; left: 0; top: 0; color: white;\">" + user + "/" + upload_filename + "</p>", 'utf-8'))
                return
                #self.respond_with(self.wfile.write, location + temp_filename)

        if self.headers['Content-Type'] == "application/x-www-form-urlencoded":
            post_data = self.rfile.read(content_length)
            #self.log_message("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
            #                 str(self.path), str(self.headers), str(post_data.decode('utf-8')))

            form = urllib.parse.parse_qs(post_data.decode('utf-8'))
            redirect = trido.handle_post_request((user, filename), form)

        self.send_response(303)
        self.send_header("Location", trido.s['server'] + redirect)
        self.end_headers()
        # self.send_response_only()

if __name__ == '__main__':
    address = (trido.s["hostname"], trido.s["port"])

    with ThreadingHTTPServer(address, ProjectRequestHandler) as httpd:
        #httpd.socket = ssl.wrap_socket(httpd.socket, certfile='cert_17.pem', keyfile='key_17.pem', server_side=True)
        #try:
        # init server
        trido.s['output_dir'] = ''
        trido.init_users()

        post_map_dirs = [trido.s['users_dir'] + d + "/postmaps/" for d in os.listdir(trido.s['users_dir'])]
        for d in post_map_dirs:
            trido.post_maps_to_html(d)

        trido.generate_user_homepages()
        #trido.generate_home_page()

        # inform user
        print("Serving on " + trido.s["server"])
        httpd.serve_forever()
