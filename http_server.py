from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

if __name__ == '__main__':
    server_address = ('', 80)
    httpd = ThreadingHTTPServer(server_address, MyHandler)
    httpd.serve_forever()