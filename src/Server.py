import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
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
    TEXTUAL_CONTENT_TYPES = {   
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript'
    }

    VISUAL_CONTENT_TYPES ={
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.ico': 'image/x-icon'
    }

    def __init__(self, pipe, event_queue, *args, **kwargs):
        self.ws_handler = None
        self.pipe = pipe
        self.event_queue = event_queue
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
    
    def get_content_type(self, filename):
        _, file_extension = os.path.splitext(filename)
        if file_extension in ['.html']:
            return "text/html"
        elif file_extension in ['.css']:
            return "text/css"
        elif file_extension in ['.js']:
            return "text/javascript"
        elif file_extension in ['.jpg', '.jpeg']:
            return "image/jpeg"
        elif file_extension == '.png':
            return "image/png"
        elif file_extension == '.ico':
            return "image/x-icon"
        else:
            return "application/octet-stream"  # Fallback content type for other file types

    def do_GET(self):
        try:
            # Get the file path from the URL
            file_path = 'public'
            file_path += "/index.html" if self.path == "/" else self.path
            print(file_path)
            # Check if the file exists
            if os.path.exists(file_path):
                # Determine the file extension
                _, file_extension = os.path.splitext(file_path)
                
                self.send_response(200)
                # Check if the file extension is supported
                if file_extension in self.VISUAL_CONTENT_TYPES:
                    # Set the content type header based on the file extension
                    self.send_header('Content-type', self.VISUAL_CONTENT_TYPES[file_extension])
                    self.end_headers()

                    # Open and send the file
                    with open(file_path, 'rb') as file:
                        self.wfile.write(file.read())
                elif file_extension in self.TEXTUAL_CONTENT_TYPES:
                    self.send_header('Content-type', self.TEXTUAL_CONTENT_TYPES[file_extension])
                    self.end_headers()

                    # Open and send the file
                    with open(file_path, 'r') as file:
                        file_contents = file.read()
                        self.wfile.write(bytes(file_contents, 'utf-8'))
                else:
                    # If the file extension is not supported, return a 415 Unsupported Media Type response
                    self.send_error(415, 'Unsupported Media Type')
            else:
                # If the file doesn't exist, return a 404 Not Found response
                self.send_error(404, 'File Not Found')
        except Exception as e:
            # Handle any other exceptions that may occur during processing
            self.send_error(500, str(e))    
    
    # # Handles get requests
    # def do_GET(self):

    #     filename = "/index.html" if self.path == "/" else self.path
    #     try:
    #         with open(f"public{filename}") as f:
    #             self.send_response(200)
    #             self.send_header("Content-type", self.get_content_type(filename))
    #             self.end_headers()
    #             self.wfile.write(f.read())
    #     except:
    #         self.send_response(404)
    #         self.end_headers()
    #         traceback.print_exc()            

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
                with open('assets/map_image.png', 'wb') as file:
                    file.write(base64.b64decode(image_data))
                file_written = True
            except:
                pass
        message = {
            "message_type" : "image",
            "message" : {
                "image_data" : image_data
            }
        }
        message  = json.dumps(message)
        if self.event_queue:
            self.event_queue.put(message)
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
            map = Map.Map(data)

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
def run_server(conn=None, event_queue=None):
    server = HTTPServer(server_address, lambda *args, **kwargs: RequestHandler(conn, event_queue, *args, **kwargs))
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