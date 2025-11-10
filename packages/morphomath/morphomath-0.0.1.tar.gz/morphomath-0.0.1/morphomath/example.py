#!/usr/bin/env python3

"""Create the example image."""

import random

import numpy as np

def create_test_image() -> np.ndarray:
    """Create a test image for morphological operations.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from morphomath.example import create_test_image
    >>> plt.imshow(create_test_image(), cmap="gray")
    >>> plt.show()
    >>>
    """
    img = np.zeros((180, 180), dtype=np.uint8)

    # little dot cloud
    for i in range(0, 6, 2):
        for j in range(0, 180, 2):
            img[i, j] = 255

    # medium dot cloud
    for i in range(6, 24, 6):
        for j in range(0, 180, 6):
            img[i:i+3, j:j+3] = 255

    # big dot cloud
    for i in range(24, 60, 18):
        for j in range(0, 180, 18):
            img[i:i+9, j:j+9] = 255

    # small lines
    for i in range(60, 66, 2):
        img[range(60, 66, 2), :] = 255
        img[60:120, i-60] = 255

    # medium lines
    for i in range(66, 84, 6):
        img[i:i+3, :] = 255
        img[60:120, i-60:i-60+3] = 255

    # big lines
    for i in range(84, 120, 18):
        img[i:i+9, :] = 255
        img[60:120, i-60:i-60+9] = 255

    # random blocs
    random.seed(0)
    for _ in range(100):
        height = random.randint(1, 9)
        width = random.randint(1, 9)
        i = random.randint(120, 180-height)
        j = random.randint(0, 180-width)
        img[i:i+height, j:j+width] = 255

    # create symetry
    img = np.vstack(
        [np.hstack([img, 1-img[:, ::-1]]), np.hstack([img[::-1, :].T, 1-img.T])]
    )

    return img
