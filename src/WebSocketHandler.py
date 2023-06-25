import asyncio
import json
import multiprocessing as mp
import time
import websockets
from datetime import datetime, timezone

#! TODO:
#   add ipc and 
#  
class WebSocketHandler:

    def __init__(self, queue, south, west, north, east):
        self.address = "wss://stream.aisstream.io/v0/stream"
        self.api_key = "d77b1be3c710d2d404386475ef886b33989950e3"
        self.ws = None
        self.south = south
        self.west = west
        self.north = north
        self.east = east
        self.queue = queue
        self.count = 0

    async def run(self):
        try:
            self.ws = await websockets.connect(self.address)
            print('Connected')
            subscription_message = self.make_subscription_message(-90, -180, 90, 180)
            await self.ws.send(subscription_message)

            asyncio.create_task(self.check_queue())

            async for message in self.ws:
                try:
                    await self.process(message)
                except:
                    print('Could not process message: ', message)
                            
        except websockets.WebSocketException as e:
            print(f"WebSocket error occurred: {str(e)}")

        finally:
            if self.ws:
                await self.ws.close()
                print('WebSocket connection closed.')

    async def check_queue(self):
        while True:
            if not self.queue.empty():
                subscription_message = self.queue.get()
                await self.ws.send(subscription_message)
                print("Resubscribed")
            await asyncio.sleep(1)  # Adjust the sleep duration as needed
            
    def make_subscription_message(self, south, west, north, east):
        subscription_message = {"APIKey": self.api_key, "BoundingBoxes": [[[south, west], [north, east]]]}
        json_message = json.dumps(subscription_message)
        return json_message
        


    async def subscribe(self, south, west, north, east):
        subscription_message = {"APIKey": self.api_key, "BoundingBoxes": [[[south, west], [north, east]]]}
        json_message = json.dumps(subscription_message)
        await self.ws.send(json_message)

    async def process(self, message):
        self.count += 1
        message = json.loads(message)
        message_type = message["MessageType"]

        if message_type == "PositionReport":
            ais_message = message['Message']['PositionReport']
            print(f"[{datetime.now(timezone.utc)}] ShipId: {ais_message['UserID']} Latitude: {ais_message['Latitude']} Longitude: {ais_message['Longitude']}")
        # if self.count % 300 == 0:
        #     print(self.count)

    async def close_connection(self):
        await self.ws.close()


def run_websocket_handler(ws_handler):
    asyncio.run(ws_handler.run())

async def main():
    async with True:
        print("Here")
        
if __name__ == '__main__':
    queue = mp.Queue()
    ws_handler = WebSocketHandler(queue)

    ws_process = mp.Process(target=run_websocket_handler, args=(ws_handler,))
    ws_process.start()

    time.sleep(5)  # Wait for the WebSocket connection to be established

    subscription_message = ws_handler.make_subscription_message(-40, -40, 40, 40)
    queue.put(subscription_message)
    print("message sent")

    time.sleep(5)  # Wait for the WebSocket connection to be established

    subscription_message = ws_handler.make_subscription_message(-40, -40, 40, 40)
    queue.put(subscription_message)
    print("message sent")


    