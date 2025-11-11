"""Fast morphological operations."""

import typing

import numpy as np

from .kernel import Kernel
from .morpho import Morpho

__author__ = "Robin RICHARD (robinechuca)"
__version__ = "0.0.2"  # pep 440
__all__ = ["Dilatation", "Erosion", "Kernel", "Morpho", "dilate", "erode"]


class Erosion(Morpho):
    """Morphological erosion, based on :py:class:`morphomath.morpho.Morpho`."""

    def __init__(self, kernel: Kernel | np.ndarray | list | tuple | set | frozenset) -> None:
        """Alias to :py:class:`morphomath.morpho.Morpho` with ``min`` operator."""
        super().__init__(kernel, "min")

    @classmethod
    def from_decomposition(
        cls,
        kernels: list[Kernel | np.ndarray | list | tuple | set | frozenset],
        merge: dict[tuple[int, ...], set[tuple[int, tuple[int, ...]]]],
    ) -> typing.Self:
        """Alias to :py:meth:`morphomath.morpho.Morpho.from_decomposition`."""
        return super().from_decomposition(kernels, merge, "min")


class Dilatation(Morpho):
    """Morphological dilatation, based on :py:class:`morphomath.morpho.Morpho`."""

    def __init__(self, kernel: Kernel | np.ndarray | list | tuple | set | frozenset) -> None:
        """Alias to :py:class:`morphomath.morpho.Morpho` with ``max`` operator."""
        super().__init__(kernel, "max")

    @classmethod
    def from_decomposition(
        cls,
        kernels: list[Kernel | np.ndarray | list | tuple | set | frozenset],
        merge: dict[tuple[int, ...], set[tuple[int, tuple[int, ...]]]],
    ) -> typing.Self:
        """Alias to :py:meth:`morphomath.morpho.Morpho.from_decomposition`."""
        return super().from_decomposition(kernels, merge, "max")


def dilate(
    src: np.ndarray,
    kernel: Kernel | np.ndarray | list | tuple | set | frozenset,
) -> np.ndarray:
    """Erode an image by using a specific structuring element.

    For 2d kernel, it is equivalent to:

    .. code:: shell

        import cv2
        import morphomath

        def dilate(src, kernel):
            ker = morphomath.Kernel(kernel)
            return cv2.dilate(
                img,
                kernel=ker.struct_elem,
                anchor=ker.anchor[::-1],
                borderType=cv2.BORDER_REPLICATE,
            )

    Parameters
    ----------
    src : np.ndarray
        The input image, transmitted to :py:method:`morphomath.morpho.Morpho.__call__`.
    kernel : arraylike or pointslike
        The structuring element used for dilatation,
        transmitted to :py:class:`morphomath.kernel.Kernel`.

    Returns
    -------
    np.ndarray
        The dilated copy of the src tensor.

    """
    return Dilatation(kernel).decomposed()(src)


def erode(
    src: np.ndarray,
    kernel: Kernel | np.ndarray | list | tuple | set | frozenset,
) -> np.ndarray:
    """Erode an image by using a specific structuring element.

    For 2d kernel, it is equivalent to:

    .. code:: shell

        import cv2
        import morphomath

        def erode(src, kernel):
            ker = morphomath.Kernel(kernel)
            return cv2.erode(
                img,
                kernel=ker.struct_elem,
                anchor=ker.anchor[::-1],
                borderType=cv2.BORDER_REPLICATE,
            )

    Parameters
    ----------
    src : np.ndarray
        The input image, transmitted to :py:method:`morphomath.morpho.Morpho.__call__`.
    kernel : arraylike or pointslike
        The structuring element used for erosion,
        transmitted to :py:class:`morphomath.kernel.Kernel`.

    Returns
    -------
    np.ndarray
        The eroded copy of the src tensor.

    """
    return Erosion(kernel).decomposed()(src)
