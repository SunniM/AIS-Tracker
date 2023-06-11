import base64
import json
import math
from http.server import HTTPServer, BaseHTTPRequestHandler

host = 'localhost'
port = 8080
earthCir = 40075016.686
degreesPerMeter = 360 / earthCir

# Set the parameters for the static map image
api_key = 'YOUR_API_KEY'  # Replace with your Google Maps API key
image_size = '1920x1080'  # Size of the image in pixels
map_id = 'YOUR_MAP_ID'  # Specific map ID


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        f = open('src/index.html').read()
        self.wfile.write(bytes(f, 'utf-8'))

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

        # Decode and save the image locally
        with open('map_image.jpg', 'wb') as file:
            file.write(base64.b64decode(image_data))

    def handle_default_post(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            latitude = data['latitude']
            longitude = data['longitude']
            zoom = data['zoom']

            # Do something with the data
            [min_lat, min_lng, max_lat, max_lng] = calculate_bounding_box(latitude, longitude, zoom, 1920, 1080)
            topLeft = [max_lat, min_lng]
            topRight = [max_lat, max_lng]
            botLeft = [min_lat, min_lng]
            botRight = [min_lat, max_lng]

            # Printing all data
            print("latitude: ", latitude)
            print("longitude: ", longitude)
            print("zoom: ", zoom)
            print("topLeft: ", topLeft)
            print("botLeft: ", botLeft)
            print("topRight: ", topRight)
            print("botRight: ", botRight)

            self.wfile.write(b'POST request received successfully')
        except:
            self.send_response(404)
            self.end_headers()


# Converts to radians from Deg
def toRadians(degrees):
    return (degrees * math.pi / 180)


# Calculates the bounding box of what is displayed
def calculate_bounding_box(lat, lng, zoom, width, height):
    metersPerPixelEW = earthCir / math.pow(2, zoom + 8)
    metersPerPixelNS = earthCir / math.pow(2, zoom + 8) * math.cos(toRadians(lat))

    shiftMetersEW = width / 2 * metersPerPixelEW
    shiftMetersNS = height / 2 * metersPerPixelNS

    shiftDegreesEW = shiftMetersEW * degreesPerMeter
    shiftDegreesNS = shiftMetersNS * degreesPerMeter

    # min_lat, min_lng, max_lat, max_lng
    return (lat - shiftDegreesNS), (lng - shiftDegreesEW), (lat + shiftDegreesNS), (lng + shiftDegreesEW)


def main():
    server = HTTPServer((host, port), MyServer)
    print("Server started http://%s:%s" % (host, port))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    print("Server stopped.")


if __name__ == '__main__':
    main()
