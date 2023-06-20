import noise
import numpy as np
import pygame

# Set up parameters for Perlin noise generation and animation
width = 400  # Width of the height map
height = 400  # Height of the height map
depth = 50  # Number of frames in the animation

scale = 10.0  # Adjust the scale to control the frequency of the waves
octaves = 6
persistence = 0.5
lacunarity = 2.0
scroll_speed = 1  # Speed of the scrolling effect

# Precompute color lookup table
color_lookup = np.zeros((256, 3), dtype=np.uint8)
for i in range(256):
    r = min(255, int(50  + i * 0.5))
    g = min(255, int(75 + i * 0.5))
    b = min(255, int(200 + i * 0.5))
    color_lookup[i] = (r, g, b)

# Initialize Pygame with hardware acceleration
pygame.init()
window_size = (width, height)
screen = pygame.display.set_mode(window_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
clock = pygame.time.Clock()

# Generate the initial height map
height_map = np.zeros((height, width))

# Game loop
running = True
frame_index = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Generate the height map for the current frame
    for y in range(height):
        for x in range(width):
            shifted_x = x + frame_index * scroll_speed
            value = noise.pnoise3(shifted_x / scale,
                                  y / scale,
                                  frame_index / scale,
                                  octaves=octaves,
                                  persistence=persistence,
                                  lacunarity=lacunarity,
                                  repeatx=width,
                                  repeaty=height,
                                  repeatz=depth,
                                  base=0)
            height_map[y, x] = value

    # Normalize height map to [0, 1] range
    height_map = (height_map - np.min(height_map)) / (np.max(height_map) - np.min(height_map))

    # Apply color lookup to the height map
    height_map_scaled = (height_map * 255).astype(np.uint8)
    frame_color = color_lookup[height_map_scaled]

    # Render the current frame
    frame_surface = pygame.surfarray.make_surface(frame_color)
    screen.blit(pygame.transform.scale(frame_surface, window_size), (0, 0))
    pygame.display.flip()

    frame_index = (frame_index + 1) % depth
    clock.tick(30)  # Limit frame rate to 30 FPS

pygame.quit()
