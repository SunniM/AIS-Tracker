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
    render()
