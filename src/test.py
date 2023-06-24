import WebSocketHandler
import multiprocessing as mp
import time

def main():
    ws_handler = WebSocketHandler.WebSocketHandler(-40,-40,-30,-30)
    print("main id: ", id(ws_handler))
    ws_process = mp.Process(target=ws_handler.run)
    ws_process.start()
    
    time.sleep(5)
    ws_handler.close_connection()
    ws_process.join()
     
    ws_handler = WebSocketHandler.WebSocketHandler(-90,-180,90,180)
    ws_process = mp.Process(target=ws_handler.run)
    ws_process.start()

if __name__ == '__main__':
    main()