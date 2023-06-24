import pygame

def render(width, height):
    image = pygame.image.load("map_image.jpg")
    pygame.init()
    screen = pygame.display.set_mode((width, height))
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

if __name__ == '__main__':
    render()
