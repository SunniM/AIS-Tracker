
import Map
import traceback
import multiprocessing as mp
from tkinter import Tk, Label
from PIL import Image, ImageTk
import pygame

import Server, WebSocketHandler, render, events


import Server, Map
from WebSocketHandler import WebSocketHandler


import Server, Map
from WebSocketHandler import WebSocketHandler


server_address = ('localhost', 8080)

def main():
    # pipe used by server and controller
    server_pipe, controller_pipe = mp.Pipe()
    image_queue = mp.Queue()

    ws_handler = None
    ws_process = None
    ws_queue = mp.Queue()
    window_process = mp.Process(target=render.render, args=(1920, 1080, image_queue))
    window_process.start()

    # Starting local webserver
    server_process = mp.Process(target=Server.run_server, args=(server_pipe,image_queue))
    server_process.start()

    while True:
        # checks for incoming messages from server
        if controller_pipe.poll():
            data = controller_pipe.recv()
            print('data received')


            # parses message
            match type(data):

                # received a map object
                case Map.Map:
                    print("Map Recieved")

                    # gets bounding box
                    south, west, north, east = data.calculate_bounding_box(1920,1080)
                    
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
                    ws_handler = WebSocketHandler(south, west, north, east, ws_queue)
                    ws_process = mp.Process(target=ws_handler.run)
                    while not ws_process.is_alive():
                        ws_process.start()
                  
                    if not window_process.is_alive():
                        window_process.start()
                        window_process.join()
                case bytes:
                    print('bytes received')
                    image_queue.put(data)
                    event = pygame.event.Event(events.NEW_IMAGE_EVENT)
                    if not window_process.is_alive():
                        window_process.start()
                        window_process.join()
                    else:
                        pygame.event.post(event)



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        for child in mp.active_children():
            child.kill()
        print('interrupted')