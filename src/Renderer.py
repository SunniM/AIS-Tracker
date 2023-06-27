import pygame
import threading
import asyncio
from io import BytesIO
import events

class Renderer:
    def __init__(self, width, height, image_queue=None):
        self.width = width
        self.height = height
        self.image_queue = image_queue
        self.queue_thread = None

    def check_queue(self):
        while True:
            image = self.image_queue.get()
            event = pygame.event.Event(events.NEW_IMAGE_EVENT, {"image": BytesIO(image), "name_hint": 'jpg'})
            pygame.event.post(event)

    async def check_queue_async(self):
        while True:
            image = await self.image_queue.get()
            print('image received')
            event = pygame.event.Event(events.NEW_IMAGE_EVENT, {"image": BytesIO(image), "name_hint": 'jpg'})
            pygame.event.post(event)

    def render(self):
        pygame.init()

        if self.image_queue:
            self.queue_thread = threading.Thread(target=self.check_queue)
            self.queue_thread.start()

        image = pygame.image.load("map_image.jpg")

        print('Video system initialized')
        screen = pygame.display.set_mode((self.width, self.height))
        clock = pygame.time.Clock()

        running = True
        print('Original Value:', events.NEW_IMAGE_EVENT)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == events.NEW_IMAGE_EVENT:
                    print('New image received')
                    if self.image_queue:
                        image = pygame.image.load(event.image)

            screen.fill((0, 0, 0))  # Clear the screen

            # Calculate the position to center the image
            image_rect = image.get_rect()
            x = (self.width - image_rect.width) // 2
            y = (self.height - image_rect.height) // 2

            # Blit the image at the calculated position
            screen.blit(image, (x, y))

            pygame.display.flip()  # Update the screen
            clock.tick(60)  # Limit the frame rate

if __name__ == '__main__':
    render = Renderer(1920, 1080)
    render.render()
