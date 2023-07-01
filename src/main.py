import multiprocessing as mp

import Map
from Renderer import Renderer
import Server
from WebSocketHandler import WebSocketHandler

server_address = ('localhost', 8080)

def main():
    # pipe used by server and controller
    server_pipe, controller_pipe = mp.Pipe()
    image_queue = mp.Queue()

    ws_handler = None
    ws_process = None
    ws_queue = mp.Queue()

    renderer = Renderer(1920, 1080, image_queue)
    window_process = mp.Process(target=renderer.render)
    window_process.start()

    # Starting local webserver
    server_process = mp.Process(target=Server.run_server, args=(server_pipe,image_queue))
    server_process.start()

    while True:
        # checks for incoming messages from server
        if controller_pipe.poll():
            data = controller_pipe.recv()
            print('data received')
            if not window_process.is_alive():
                window_process.join()
                window_process = mp.Process(target=renderer.render)
                window_process.start()
                
            if isinstance(data, Map.Map):
                print("Map Recieved")
                # checks for exisring websocket connection
                south, west, north, east = data.calculate_bounding_box(1920, 1080)
                if ws_process:
                    subscription_message = WebSocketHandler.make_subscription_message(south, west, north, east)
                    ws_queue.put(subscription_message)      
                else:
                    # starts websocket connection
                    ws_handler = WebSocketHandler(south, west, north, east, ws_queue)
                    ws_process = mp.Process(target=ws_handler.run)
                    ws_process.start()

            elif isinstance(data, bytes):
                print('Bytes received')
                image_queue.put(data)
            
            elif isinstance(data, str):
                pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        for child in mp.active_children():
            child.kill()
        print('interrupted')
