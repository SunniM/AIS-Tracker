import cv2
import numpy as np
import pygame
import noise

# Set up parameters for the fractal noise
width = 400  # Width of the fractal noise
height = 400  # Height of the fractal noise

scale = 0.05  # Controls the scale of the fractal noise
octaves = 6  # Number of octaves in the fractal noise
persistence = 0.5  # Persistence of the fractal noise
lacunarity = 2.0  # Lacunarity of the fractal noise

# Set up parameters for the video
output_file = 'fractal_noise_video.mp4'
fps = 30
duration = 5  # Duration of the video in seconds

# Initialize pygame
pygame.init()
window_size = (width, height)
screen = pygame.Surface(window_size)

# Create a VideoWriter object to save the video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_out = cv2.VideoWriter(output_file, fourcc, fps, window_size)

# Generate the fractal noise frames
num_frames = duration * fps
for frame_index in range(num_frames):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Generate the fractal noise grid
    noise_grid = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            noise_grid[y][x] = noise.snoise2(x * scale, y * scale, octaves=octaves, persistence=persistence,
                                             lacunarity=lacunarity)

    # Normalize the noise grid to the [0, 1] range
    min_value = np.min(noise_grid)
    max_value = np.max(noise_grid)
    noise_grid = (noise_grid - min_value) / (max_value - min_value)

    # Render the fractal noise
    for y in range(height):
        for x in range(width):
            color_value = int(noise_grid[y][x] * 255)
            screen.set_at((x, y), (color_value, color_value, color_value))

    # Convert the pygame surface to a numpy array
    frame_array = pygame.surfarray.array3d(screen)

    # Convert the numpy array from RGB to BGR format for OpenCV
    frame_array_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)

    # Write the frame to the video file
    video_out.write(frame_array_bgr)

# Release the VideoWriter object and close the video file
video_out.release()
