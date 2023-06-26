import pygame
from io import BytesIO

import events
def render(width, height, image_queue=None):

    image = pygame.image.load("map_image.jpg")
    # pygame.init()
    print('video system intiailzed')
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    running = True
    print('Original Value:', events.NEW_IMAGE_EVENT)
    while running:

        for event in pygame.event.get():
            print(event)
            match event.type:
                case pygame.QUIT:
                    running = False
                case events.NEW_IMAGE_EVENT:
                    print('new_image_recieved')
                    if image_queue:
                        image = pygame.image.frombytes(image_queue.get())
                        

        screen.fill((0, 0, 0))  # Clear the screen

        # Load the current image based on the current_image_index

        # Calculate the position to center the image
        image_rect = image.get_rect()
        x = (width - image_rect.width) // 2
        y = (height - image_rect.height) // 2

        # Blit the image at the calculated position
        screen.blit(image, (x, y))

        pygame.display.flip()  # Update the screen
        clock.tick(60)  # Limit the frame rate

        # Switch to the next image

    pygame.quit()

if __name__ == '__main__':
    render(1920, 1080)
