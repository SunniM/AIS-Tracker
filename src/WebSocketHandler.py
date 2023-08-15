import websocket
import threading
import rel
import json
from datetime import datetime, timezone


def make_subscription_message(south, west, north, east):
    subscription_message = {"APIKey": "d77b1be3c710d2d404386475ef886b33989950e3", "BoundingBoxes": [
        [[south, west], [north, east]]]}
    return json.dumps(subscription_message)

class WebSocketHandler():
    def __init__(self, input_queue=None, output_queue=None, map=None):
        self.output_queue = output_queue
        self.input_queue = input_queue
        self.map = map

        self.ws = websocket.WebSocketApp("wss://stream.aisstream.io/v0/stream",
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         )

    def run(self, south, west, north, east):
        # websocket.enableTrace(True)
        self.set_bounding_box(south, west, north, east)

        self.running  = True

        if self.input_queue:
            queue_thread = threading.Thread(target=self.check_queue)
            queue_thread.start()

        self.ws.run_forever(dispatcher=rel)  # dispatcher = rel
        rel.signal(2, rel.abort)  # Keyboard Interrupt
        rel.dispatch()
        queue_thread.join()

    def check_queue(self):
        while self.running:
            subscription_message = self.input_queue.get()
            self.from_subscription_message(subscription_message)
            self.ws.send(subscription_message)
            render_message = {
                "message_type": "clear_list",
                "message": ""
            }
            render_message = json.dumps(render_message)
            self.output_queue.put(render_message)

    def on_open(self, ws):
        self.subscribe()
        print("Opened connection")

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection Closed")
        print('status code: ', close_status_code)
        print('message: ', close_msg)
        self.running = False
        # self.run()

    def close_connection(self):
        print("Closing Connection")
        self.ws.close()

    def on_error(self, ws, error):
        print(error)
        print(self.ws.header)

    def on_message(self, ws, message):
        message = json.loads(message)
        message_type = message["MessageType"]

        if message_type == "PositionReport":
            # the message parameter contains a key of the message type which contains the message itself
            ais_message = message['Message']['PositionReport']

            Latitude = ais_message['Latitude']
            Longitude = ais_message['Longitude']

            # should be in a method, but wasn't able to get it working
            width = 1920
            height = 1080

            # 0,0 is north west of the bounding box
            # calculating a ratio for the x and y pixel based on size of the window

            x = int(width * abs((Longitude - self.west) / (self.east - self.west)))
            y = int(height * abs((Latitude - self.north) / (self.north - self.south)))

            # end of should be in a methode, but wasn't able to get it working
            ship_message = {
                "message_type": "ship_data",
                "message": {
                    "ship_id": ais_message['UserID'],
                    "x": x,
                    "y": y}
            }
            ship_message = json.dumps(ship_message)
            if self.output_queue:
                self.output_queue.put(ship_message)
            else:
                print(ship_message)

            # print(f"[{datetime.now(timezone.utc)}] ShipId: {ais_message['UserID']} Latitude: {Latitude} Longitude: {Longitude} x Pixel: {x} y Pixel: {y}")

    def subscribe(self):
        subscription_message = make_subscription_message(
            self.south, self.west, self.north, self.east)
        self.ws.send(subscription_message)

    def from_subscription_message(self, subscription_message):
        subscription_message = json.loads(subscription_message)
        values = subscription_message["BoundingBoxes"]
        self.set_bounding_box(values[0][0][0], values[0][0][1], values[0][1][0], values[0][1][1])

    def set_bounding_box(self, south, west, north, east):
        self.south = south
        self.west = west
        self.north = north
        self.east = east

if __name__ == '__main__':
    conn = WebSocketHandler()
    conn.run(-90, -180, 90, 180)