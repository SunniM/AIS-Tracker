import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# pip3 install git+https://github.com/pvigier/perlin-numpy
from perlin_numpy import generate_perlin_noise_3d

np.random.seed(0)
noise = generate_perlin_noise_3d(
    (32, 256, 256), (1, 4, 4), tileable=(True, False, False)
)

fig = plt.figure()
images = [
    [plt.imshow(
        layer, cmap='gray', interpolation='lanczos', animated=True
    )]
    for layer in noise
]
animation_3d = animation.ArtistAnimation(fig, images, blit=True)
plt.show()