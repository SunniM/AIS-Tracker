from http.server import HTTPServer, BaseHTTPRequestHandler
import json, traceback

import Map

server_address = ('localhost', 8080)

class RequestHandler(BaseHTTPRequestHandler):

    def __init__(self, pipe, *args, **kwargs):
        self.ws_handler = None
        self.pipe = pipe
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
    
    # Handles get requests
    def do_GET(self):

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        f = open('src/index.html').read()
        self.wfile.write(bytes(f, 'utf-8'))

    # Handles post requests
    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
           
            # Do something with the data
            map = Map.Map(data['latitude'], data['longitude'], data['zoom'])

            if self.pipe:
                self.pipe.send(map)

            map.print_map_data(1920, 1080)
          

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'POST request received successfully')      
        except:
            self.send_response(404)
            self.end_headers()
            traceback.print_exc()

# Starts server and handles communicates with controller
def run_server(conn):
    server = HTTPServer(server_address, lambda *args, **kwargs: RequestHandler(conn, *args, **kwargs))
    print("Server started http://%s:%s" % server_address)

    # Serve requests until the parent process sends the termination signal
    try:
        while True:
            server.handle_request()
            if conn:
                if conn.poll():
                    message = conn.recv()
                    if message == 'terminate':
                        break
        close_server(server)
    except KeyboardInterrupt:
        pass
    close_server()

# Closes server
def close_server(server):
    server.server_close()
    print("Server Closed")

if __name__ == '__main__':

    run_server(None)