import multiprocessing as mp
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

host = 'localhost'
port = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        f = open('src/map.html').read()
        self.wfile.write(bytes(f, 'utf-8'))

    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            latitude = data['latitude']
            longitude = data['longitude']
            zoom = data['zoom']

            # Do something with the data
            # ...
            print("latitude: ", latitude)
            print("longitude: ", longitude)
            print("zoom: ", zoom)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'POST request received successfully')      
        except:
            self.send_response(404)
            self.end_headers()

   
def main():
    server = HTTPServer((host,port), MyServer)
    print("Server started http://%s:%s" % (host, port))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    print("Server stopped.")  

if __name__ == '__main__':
    main()