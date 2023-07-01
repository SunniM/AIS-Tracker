import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import traceback

import Map

earthCir = 40075016.686
degreesPerMeter = 360 / earthCir

# Set the parameters for the static map image
api_key = 'YOUR_API_KEY'  # Replace with your Google Maps API key
image_size = '1920x1080'  # Size of the image in pixels
map_id = 'YOUR_MAP_ID'  # Specific map ID



server_address = ('localhost', 8080)



class RequestHandler(BaseHTTPRequestHandler):


    def __init__(self, pipe, image_queue, *args, **kwargs):
        self.ws_handler = None
        self.pipe = pipe
        self.image_queue = image_queue
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
        if self.path == '/save-image':
            self.save_image()
        else:
            self.handle_default_post()

    def save_image(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        if 'image' in data:
            # Save the image locally
            self.save_image_locally(data['image'])

        # Send the response
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Image saved successfully')

    def save_image_locally(self, image_data):
        # Extract the base64-encoded image data
        _, image_data = image_data.split(',')
        file_written = False
        # Decode and save the image locally
        while not file_written:
            try:
                with open('map_image.png', 'wb') as file:
                    file.write(base64.b64decode(image_data))
                file_written = True
            except:
                pass
        self.pipe.send(base64.b64decode(image_data))
        print('bytes sent')

    def handle_default_post(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
           
            # Do something with the data
            map = Map.Map(data['latitude'], data['longitude'], data['zoom'])

            if self.pipe:
                self.pipe.send(map)

            # Printing all data
            # map.print_map_data(1920, 1080)
            

            self.wfile.write(b'POST request received successfully')
        except:
            self.send_response(404)
            self.end_headers()
            traceback.print_exc()

# Starts server and handles communicates with controller
def run_server(conn=None, image_queue=None):
    server = HTTPServer(server_address, lambda *args, **kwargs: RequestHandler(conn, image_queue, *args, **kwargs))
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
    close_server(server)

# Closes server
def close_server(server):
    server.server_close()
    print("Server Closed")



if __name__ == '__main__':
    run_server()