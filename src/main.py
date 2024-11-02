import multiprocessing as mp
import os

import Map
from Renderer import Renderer
import Server
from WebSocketHandler import WebSocketHandler, make_subscription_message

server_address = ('localhost', 8080)

def main():
    # pipe used by server and controller
    server_pipe, controller_pipe = mp.Pipe()
    event_queue = mp.Queue()
    resub_queue = mp.Queue()

    # Starting local webserver
    server_process = mp.Process(target=Server.run_server, args=(server_pipe,event_queue))
    server_process.start()

    # Initialize websocket
    ws_handler = WebSocketHandler(resub_queue, event_queue)
    ws_process = None

    # Initialize renderer
    renderer = Renderer(1920, 1080, event_queue, fullscreen=False)
    window_process = mp.Process(target=renderer.render)



    while True:
        # checks for incoming messages from server
        if controller_pipe.poll():
            data = controller_pipe.recv()
            print('data received')
            if not window_process.is_alive():
                window_process = mp.Process(target=renderer.render)
                window_process.start()
                
            if isinstance(data, Map.Map):
                print("Map Recieved")
                # checks for existing websocket connection
                data.print_map_data()
                south, west, north, east = data.calculate_bounding_box()

                if ws_process:
                    subscription_message = make_subscription_message(south, west, north, east)
                    resub_queue.put(subscription_message)      
                else:
                    # starts websocket connection
                    ws_process = mp.Process(target=ws_handler.run, args=(south, west, north, east))
                    ws_process.start()

            elif isinstance(data, bytes):
                print('Bytes received')
                event_queue.put(data)
            
            elif isinstance(data, str):
                pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        for child in mp.active_children():
            child.kill()
        print('interrupted')
