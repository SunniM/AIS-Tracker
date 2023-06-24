
import Map
import traceback
import multiprocessing as mp

import pygame

import Server, WebSocketHandler, render


import Server, Map
from WebSocketHandler import WebSocketHandler


server_address = ('localhost', 8080)
new_image_event = pygame.USEREVENT + 1


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
                    else:
                        pygame.event.post(new_image_event)

                    # Render window


def show_window(width=1920, height=1080):
    
    pygame.init()

    screen = pygame.display.set_mode((width, height))
    image = pygame.image.load("map_image.jpg")

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case new_image_event:
                    image = pygame.image.load("map_image.jpg")

        screen.fill((0, 0, 0))  # Clear the screen

        # Load the current image based on the current_image_index

        # Use the loaded image within the loop
        screen.blit(image, (0, 0))

        pygame.display.flip()  # Update the screen
        clock.tick(60)  # Limit the frame rate

        # Switch to the next image

    pygame.quit()

    # # Create the main window
    # window = Tk()

    # # Set the window title
    # window.title("Image Background Example")

    # # Set the window size
    # window.geometry("1920x1080")

    # # Load the image
    # image = Image.open("map_image.jpg")
    # background_image = ImageTk.PhotoImage(image)

    # # Create a label with the image as the background
    # background_label = Label(window, image=background_image)
    # background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # # Add other widgets or perform other operations on the window

    # # Start the main event loop
    # window.mainloop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        for child in mp.active_children():
            child.kill()
        print('interrupted')