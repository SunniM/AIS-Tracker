import base64
import cv2
import json
import numpy as np
import pygame
from queue import Empty, Queue
import threading

import events


class Renderer:
    def __init__(self, width, height, message_queue=None, fullscreen=False):

        self.ship_list = {}

        self.running = True
        self.video = None
        self.width = width
        self.height = height
        self.image = None
        self.message_queue = message_queue
        self.queue_thread = None
        self.fullscreen = pygame.FULLSCREEN if fullscreen else 0

    def _check_queue(self):
        while self.running:
            try:
                message = self.message_queue.get_nowait()
                message = json.loads(message)

                message_type = message["message_type"]
                message = message["message"]

                if message_type == "image":
                    event = pygame.event.Event(events.NEW_IMAGE_EVENT, {"image": message['image_data'], "name_hint": 'png'})
                    pygame.event.post(event)
                elif message_type == "ship_data":
                    with self.ship_list_lock:
                        ship_item = {message["ship_id"]: (message["x"], message["y"])}
                        print(ship_item)
                        self.ship_list.update(ship_item)
                elif message_type == "clear_list":
                    with self.ship_list_lock:
                        self.ship_list = {}

            except Empty:
                pass

    def _mask_image(self, buffer=None):

        if not self.image and not buffer:
            cv_image = cv2.imread('assets/map_image.png', cv2.IMREAD_UNCHANGED)
        else:
            nparr = np.fromstring(base64.b64decode(buffer), np.uint8)
            cv_image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

        mask = np.logical_and(cv_image[:, :, 0] > 90, np.logical_and(
            cv_image[:, :, 1] < 100, cv_image[:, :, 2] < 100))
        cv_image[:, :, 3][mask] = 0

        cv2.imwrite("assets/map_mask.png", cv_image)

        self.image = pygame.image.frombuffer(
            cv_image.tobytes(), cv_image.shape[1::-1], "BGRA")
        print("image masked")

    def render(self):
        pygame.init()

        # Lock for accessing the ship list
        self.ship_list_lock = threading.Lock()

        screen = pygame.display.set_mode(
            (self.width, self.height), flags=self.fullscreen)
        clock = pygame.time.Clock()

        boat_img = pygame.image.load("assets/dot.png")
        self.video = cv2.VideoCapture("assets/water.mp4")
        self._mask_image()

        if self.message_queue:
            self.queue_thread = threading.Thread(target=self._check_queue)
            self.queue_thread.start()

        more_frames, frame = self.video.read()
        fps = self.video.get(cv2.CAP_PROP_FPS)
        self.running = more_frames
        keys = pygame.key.get_pressed()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or keys[pygame.K_ESCAPE] == True:
                    self.running = False
                elif event.type == events.NEW_IMAGE_EVENT:
                    print('New image received')
                    if self.message_queue:
                        self._mask_image(event.image)

            screen.fill((0, 0, 0))

            more_frames, frame = self.video.read()
            if not more_frames:
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                more_frames, frame = self.video.read()
            video_surf = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "BGR")

            
            screen.blit(video_surf, (0, 0))

            with self.ship_list_lock:
                ship_list_copy = self.ship_list.copy()  # Make a local copy of the ship list

           
            # Calculate the position to center the image
            image_rect = self.image.get_rect()
            x = (self.width - image_rect.width) // 2
            y = (self.height - image_rect.height) // 2

            # Blit the image at the calculated position
            screen.blit(self.image, (x, y))

            for x, y in ship_list_copy.values():
                screen.blit(boat_img, [x, y])


            # box_width = 10
            # for x, y in ship_list_copy.values():
            #     rect = pygame.Rect(x-(box_width//2), y-(box_width//2), 10, 10)
            #     pygame.draw.rect(screen, (255, 0, 0), rect)
        
            
            keys = pygame.key.get_pressed()
            pygame.display.flip()
            clock.tick(fps)

        if self.message_queue:
            self.queue_thread.join()
        pygame.quit()


if __name__ == '__main__':
    render = Renderer(1920, 1080)
    render.render()
