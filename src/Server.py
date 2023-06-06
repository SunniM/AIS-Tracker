import multiprocessing as mp
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import math
import asyncio
import websockets
from datetime import datetime, timezone

host = 'localhost'
port = 8080
earthCir = 40075016.686
degreesPerMeter = 360 / earthCir

class MyServer(BaseHTTPRequestHandler):
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
            latitude = data['latitude']
            longitude = data['longitude']
            zoom = data['zoom']
           
            # Do something with the data
            
            #Uses function to create bounds
            [min_lat, min_lng, max_lat, max_lng] = calculate_bounding_box(latitude,longitude,zoom,1920,1080)
            topLeft = [max_lat,min_lng]
            topRight = [max_lat,max_lng]
            botLeft = [min_lat,min_lng]
            botRight = [min_lat,max_lng]
            
            #Printing all data
            print("latitude: ", latitude)
            print("longitude: ", longitude)
            print("zoom: ", zoom)
            print("topLeft: ", topLeft)
            print("botLeft: ", botLeft)
            print("topRight: ", topRight)
            print("botRight: ", botRight)

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'POST request received successfully')      
        except:
            self.send_response(404)
            self.end_headers()

#Converts to radians from Deg
def toRadians(degrees):
    return (degrees * math.pi/180)


#Calculates the bounding box of what is displayed
def calculate_bounding_box(lat, lng, zoom, width, height):
    metersPerPixelEW = earthCir / math.pow(2, zoom + 8)
    metersPerPixelNS = earthCir / math.pow(2, zoom + 8) * math.cos(toRadians(lat))
    
    shiftMetersEW = width/2 * metersPerPixelEW
    shiftMetersNS = height/2 * metersPerPixelNS
    
    shiftDegreesEW = shiftMetersEW * degreesPerMeter
    shiftDegreesNS = shiftMetersNS * degreesPerMeter
    
    # min_lat, min_lng, max_lat, max_lng
    return (lat-shiftDegreesNS), (lng-shiftDegreesEW), (lat+shiftDegreesNS), (lng+shiftDegreesEW)

#Gets the Raw AIS data from AISStream.io 
async def connect_ais_stream():

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {"APIKey": "d77b1be3c710d2d404386475ef886b33989950e3", "BoundingBoxes": [[[-180, -90], [180, 90]]]}

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        async for message_json in websocket:
            message = json.loads(message_json)
            message_type = message["MessageType"]

            if message_type == "PositionReport":
                # the message parameter contains a key of the message type which contains the message itself
                ais_message = message['Message']['PositionReport']
                print(f"[{datetime.now(timezone.utc)}] ShipId: {ais_message['UserID']} Latitude: {ais_message['Latitude']} Longitude: {ais_message['Longitude']}")

   
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