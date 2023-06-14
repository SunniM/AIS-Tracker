
import Server, WebSocketHandler, Map
import multiprocessing as mp

server_address = ('localhost', 8080)


def main():
    # pipe used by server and controller
    server_pipe, controller_pipe = mp.Pipe()

    ws_handler = None

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
                    # checks for exisring websocket connection
                    if ws_handler:
                        # closes existing connection
                        ws_handler.close_connection()
                        ws_handler.join()
                    # gets bounding box
                    south, west, north, east = data.calculate_bounding_box(1980,1080)
                    # starts websocket connection
                    ws_handler = WebSocketHandler.WebSocketHandler(south, west, north, east)
                    ws_handler.start()

if __name__ == '__main__':
    main()