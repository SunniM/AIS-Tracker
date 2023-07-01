import websocket, threading, time, rel, json
from datetime import datetime, timezone

class WebSocketHandler():
    def __init__(self, south, west, north, east, queue=None):
        self.queue = queue
        self.south = south
        self.west = west
        self.north = north
        self.east = east
        self.ws = websocket.WebSocketApp("wss://stream.aisstream.io/v0/stream",
                                     on_open=self.on_open,
                                     on_message=self.on_message,
                                     on_error=self.on_error,
                                     on_close=self.on_close,
                                     )
        self.count = 0
        self.start_time = time.time()
        
    def run(self):
        # websocket.enableTrace(True)
        self.start_time = time.time()
        queue_thread = threading.Thread(target=self.check_queue)
        queue_thread.start()

        self.ws.run_forever(dispatcher=rel) # dispatcher = rel
        rel.signal(2, rel.abort)  # Keyboard Interrupt  
        rel.dispatch() 

    def check_queue(self):
        while True:
            if not self.queue.empty():
                subscription_message = self.queue.get()
                self.ws.send(subscription_message)
                print("Resubscribed")


    def on_message(self, ws, message):
        message = json.loads(message)
        message_type = message["MessageType"]
        self.count += 1

        if message_type == "PositionReport":
            # the message parameter contains a key of the message type which contains the message itself
            ais_message = message['Message']['PositionReport']
            
            Latitude = ais_message['Latitude']
            Longitude = ais_message['Longitude']
            
            #should be in a methode, but wasn't able to get it working
            width = 1920
            height = 1080
            
            print(f"West {self.west}")
            print(f"South {self.south}")
            print(f"East {self.east}")
            print(f"North {self.north}")
            #0,0 is north west of the bounding box
            #calculating a ratio for the x and y pixel based on size of the window
            x = int(width * (Longitude - self.west) / (self.east - self.west))
            y = int(height * (self.north - Latitude) / (self.north - self.south))
 
            # end of should be in a methode, but wasn't able to get it working
            
            print(f"[{datetime.now(timezone.utc)}] ShipId: {ais_message['UserID']} Latitude: {Latitude} Longitude: {Longitude} x Pixel: {x} y Pixel: {y}")

        if self.count % 300 == 0:
            print(self.count)
            print(time.time() - self.start_time)
            self.start_time = time.time()

    def on_error(self, ws, error):
        print(error)
        print(self.ws.header)

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection Closed")
        print('status code: ', close_status_code)
        print('message: ', close_msg)
        self.run()


    def on_open(self, ws):
        self.subscribe()
        print("Opened connection")

    def set_bounding_box(self, south, west, north, east):
        self.south = south
        self.west = west
        self.north = north
        self.east = east

    def close_connection(self):
        print("Closing Connection")
        self.ws.close()

    def resubscribe(self, south, west, north, east):
        self.south = south
        self.west = west
        self.north = north
        self.east = east
        self.subscribe()

    def subscribe(self):
        subscription_message = {"APIKey": "d77b1be3c710d2d404386475ef886b33989950e3", "BoundingBoxes": [[[self.south, self.west], [self.north, self.east]]]}
        json_message = json.dumps(subscription_message)
        self.ws.send(json_message)

    def make_subscription_message(south, west, north, east):
        subscription_message = {"APIKey": "d77b1be3c710d2d404386475ef886b33989950e3", "BoundingBoxes": [[[south, west], [north, east]]]}
        return json.dumps(subscription_message)


if __name__ == '__main__':
    conn = WebSocketHandler(-90, -180, 90, 180)
    conn.run()
