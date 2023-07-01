import cv2
import numpy as np
import pygame
from queue import Empty
import threading

import events

class Renderer:
    def __init__(self, width, height, image_queue=None):

        self.running = True

        self.video = None

        self.width = width
        self.height = height

        self.image = None
        self.image_queue = image_queue
    
        self.queue_thread = None

    def _check_queue(self):
        while self.running:
            try:
                image = self.image_queue.get_nowait()
                event = pygame.event.Event(events.NEW_IMAGE_EVENT, {"image": image, "name_hint": 'png'})
                pygame.event.post(event)
            except Empty:
                pass


    def _mask_image(self, buffer=None):
        # Read the PNG image with alpha channel included
        if not self.image and not buffer:
            cv_image = cv2.imread('assets/map_image.png', cv2.IMREAD_UNCHANGED)
        else:
            nparr = np.fromstring(buffer, np.uint8)

            cv_image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

        # Create a mask for the blue water pixels
        mask = np.logical_and(cv_image[:, :, 0] > 90, np.logical_and(cv_image[:, :, 1] < 100, cv_image[:, :, 2] < 100))

        # Set the alpha channel to 0 where the mask is True
        cv_image[:, :, 3][mask] = 0

        self.image = pygame.image.frombuffer(cv_image.tobytes(), cv_image.shape[1::-1],"RGBA")

    def render(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        clock = pygame.time.Clock()


        self.video = cv2.VideoCapture("assets/water.mp4")
        # self.image = pygame.image.load("map_image.png").convert_alpha()
        self._mask_image()

        if self.image_queue:
            self.queue_thread = threading.Thread(target=self._check_queue)
            self.queue_thread.start()


        more_frames, frame = self.video.read()
        fps = self.video.get(cv2.CAP_PROP_FPS)
        self.running = more_frames
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == events.NEW_IMAGE_EVENT:
                    print('New image received')
                    if self.image_queue:
                        self._mask_image(event.image)


            screen.fill((0, 0, 0))  # Clear the screen

            more_frames, frame = self.video.read()
            if more_frames:
                video_surf = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "BGR")
            else:
                # Reset the video to the beginning
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                more_frames, frame = self.video.read()
                video_surf = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "BGR")
            
            screen.blit(video_surf, (0, 0))

            # Calculate the position to center the image
            image_rect = self.image.get_rect()
            x = (self.width - image_rect.width) // 2
            y = (self.height - image_rect.height) // 2

            # Blit the image at the calculated position
            screen.blit(self.image, (x, y))

            pygame.display.flip()  # Update the screen
            clock.tick(fps)  # Limit the frame rate
        if self.image_queue:
            self.queue_thread.join()
        pygame.quit()


if __name__ == '__main__':
    render = Renderer(1280, 720)
    render.render()

