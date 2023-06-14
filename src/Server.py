from http.server import HTTPServer, BaseHTTPRequestHandler
import json, traceback

import Map


server_address = ('localhost', 8080)



class RequestHandler(BaseHTTPRequestHandler):

    def __init__(self, pipe, *args, **kwargs):
        self.ws_handler = None
        self.pipe = pipe
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
    
    def do_GET(self):

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        f = open('src/index.html').read()
        self.wfile.write(bytes(f, 'utf-8'))

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

            self.pipe.send(map)

            
            #Printing all data
            # print("\nlatitude: ", map.latitude)
            # print("longitude: ", map.longitude)
            # print("zoom: ", map.zoom)
            # print("topLeft: ", (max_lat,min_lng))
            # print("botLeft: ", (max_lat,max_lng))
            # print("topRight: ", (min_lat,min_lng))
            # print("botRight: ", (min_lat,max_lng)) 
            # print("\n")            

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'POST request received successfully')      
        except:
            self.send_response(404)
            self.end_headers()
            traceback.print_exc()

def run_server(conn):
    server = HTTPServer(server_address, lambda *args, **kwargs: RequestHandler(conn, *args, **kwargs))
    print("Server started http://%s:%s" % server_address)

    # Serve requests until the parent process sends the termination signal
    while True:
        server.handle_request()
        if conn.poll():
            message = conn.recv()
            if message == 'terminate':
                break
    server.server_close()


def main():
    server = HTTPServer(server_address, RequestHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    print("Server stopped.")  

if __name__ == '__main__':
    main()