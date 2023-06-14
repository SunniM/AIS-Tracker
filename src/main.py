
import Server, WebSocketHandler, Map
import multiprocessing as mp

server_address = ('localhost', 8080)

def main():
    server_pipe, mediator_pipe = mp.Pipe() 
    ws_process, ws_handler = None, None

    server_process = mp.Process(target=Server.run_server, args=(server_pipe,))
    server_process.start()

    while True:
        if mediator_pipe.poll():
            data = mediator_pipe.recv()
            match type(data):

                case Map.Map:      
                    print("Map Recieved")
                    if ws_handler or ws_process:
                        ws_handler.close_connection()
                        ws_handler.join()
                    south, west, north, east = data.calculate_bounding_box(1980,1080)
                    print(south, west, north, east)
                    ws_handler = WebSocketHandler.WebSocketHandler(south, west, north, east)
                    ws_handler.start()

if __name__ == '__main__':
    main()