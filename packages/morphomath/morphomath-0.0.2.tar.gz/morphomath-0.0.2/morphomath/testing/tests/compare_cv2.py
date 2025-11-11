"""Compare the morphomath behavour with the cv2 behavour."""

import cv2
import numpy as np

import morphomath


def compare_2d(kernel: list) -> None:
    """For a given kernel, compare the erosion with cv2 and morphomath."""
    path = morphomath.utils.get_project_root() / "media" / "image.png"
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    kernel = morphomath.Kernel(kernel)
    out_cv2 = cv2.erode(
        img,
        kernel=kernel.struct_elem,
        anchor=kernel.anchor[::-1],
        borderType=cv2.BORDER_REPLICATE,
    )
    out_morphomath = morphomath.erode(img, kernel)
    # import matplotlib.pyplot as plt
    # plt.imshow(out_cv2 != out_morphomath, cmap="gray")
    # plt.show()
    np.testing.assert_array_equal(out_morphomath, out_cv2)


def test_1() -> None:
    """Compare cv2 and morphomath."""
    compare_2d([[1]])


def test_11() -> None:
    """Compare cv2 and morphomath."""
    compare_2d([[1, 1]])


def test_111() -> None:
    """Compare cv2 and morphomath."""
    compare_2d([[1, 1, 1]])


def test_1_1() -> None:
    """Compare cv2 and morphomath."""
    compare_2d([[1], [1]])


def test_1_1_1() -> None:
    """Compare cv2 and morphomath."""
    compare_2d([[1], [1], [1]])


def test_010_010_111() -> None:
    """Compare cv2 and morphomath."""
    compare_2d([[0, 1, 0], [0, 1, 0], [1, 1, 1]])


def test_0110_1111_1111_0110() -> None:
    """Compare cv2 and morphomath."""
    compare_2d([[0, 1, 1, 0], [1, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 0]])

