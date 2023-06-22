import websocket, threading, time, rel
import json
from datetime import datetime, timezone

class WebSocketHandler():
    def __init__(self, south, west, north, east):
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
    def run(self):
        # websocket.enableTrace(True)
        self.ws.run_forever(dispatcher = rel)
        # dispatcher = rel
        rel.signal(2, rel.abort)
        rel.dispatch()


    def on_message(self, ws, message):
        message = json.loads(message)
        message_type = message["MessageType"]

        if message_type == "PositionReport":
            # the message parameter contains a key of the message type which contains the message itself
            ais_message = message['Message']['PositionReport']
            time.sleep(1)
            print(f"[{datetime.now(timezone.utc)}] ShipId: {ais_message['UserID']} Latitude: {ais_message['Latitude']} Longitude: {ais_message['Longitude']}")

    def on_error(self, ws, error):
        print(error)
        print(self.ws.header)

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection Closed")
        print('status code: ', close_status_code)
        print('message: ', close_msg)


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

if __name__ == '__main__':
    conn = WebSocketHandler(-90,-180,90,180)
    conn.run()
