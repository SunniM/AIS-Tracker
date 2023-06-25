import threading, json, websockets, time, ssl, asyncio, threading, traceback
import multiprocessing as mp

from websockets.sync import client

from datetime import datetime, timezone

import Server, Map
from WebSocketHandler import WebSocketHandler


server_address = ('localhost', 8080)


def main():
    # pipe used by server and controller
    server_pipe, controller_pipe = mp.Pipe()

    ws_handler = None
    ws_process = None
    ws_queue = mp.Queue()

    # Starting local webserver
    server_process = mp.Process(target=Server.run_server, args=(server_pipe,))
    server_process.start()

    while True:
        # checks for incoming messages from server
        if controller_pipe.poll():
            data = controller_pipe.recv()

            #parses message
            match type(data):

                # received a map object
                case Map.Map:      
                    print("Map Recieved")

                    # gets bounding box
                    south, west, north, east = data.calculate_bounding_box(1980,1080)
                    
                    # checks for exisring websocket connection
                    if ws_handler and ws_process.is_alive():

                        # resend existing connection
                        try:
                            message = WebSocketHandler.make_subscription_message(south, west, north, east)
                            ws_queue.put(message)
                            print('Resubsribe Sent to Websocket')
                        except:
                            traceback.print_exc()
                            print("resubscribe failed")

                    # starts websocket connection
                    ws_handler = WebSocketHandler(ws_queue, south, west, north, east)
                    ws_process = mp.Process(target=ws_handler.run)
                    while not ws_process.is_alive():
                        ws_process.start()
                  

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        for child in mp.active_children():
            child.kill()
        print('interrupted')