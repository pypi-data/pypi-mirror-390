#!/usr/bin/env python3

"""Get structurant elements."""

import numpy as np


def kernel_disk(radius: float) -> np.ndarray:
    """Create a disk with this radius.

    Examples
    --------
    >>> from morphomath.elements import kernel_disk
    >>> kernel_disk(3.5)
    array([[0, 0, 1, 1, 1, 0, 0],
           [0, 1, 1, 1, 1, 1, 0],
           [1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1],
           [0, 1, 1, 1, 1, 1, 0],
           [0, 0, 1, 1, 1, 0, 0]], dtype=uint8)
    >>>
    """
    assert isinstance(radius, float), radius.__class__.__name__
    assert radius > 0, radius

    int_radius = max(1, round(radius - 0.5))
    dist = np.arange(-int_radius, int_radius+1, 1, dtype=np.float32)
    dist_i, dist_j = np.meshgrid(dist, dist, indexing="ij")
    dist = dist_i*dist_i + dist_j*dist_j

    kernel = (dist_i*dist_i + dist_j*dist_j <= radius*radius).view(np.uint8)
    return kernel
