#!/usr/bin/env python3

"""Fast morphological operations."""

from .kernel import Kernel
from .morpho import Morpho


__author__ = "Robin RICHARD (robinechuca)"
__version__ = "0.0.1"  # pep 440
__all__ = ["Kernel", "Morpho", "Erosion", "Dilatation"]


class Erosion(Morpho):
    """Morphological erosion, based on :py:class:`morphomath.morpho.Morpho`."""

    def __init__(self, kernel):
        super().__init__(kernel, "min")

    @classmethod
    def from_decomposition(cls, kernels, merge):
        return super().from_decomposition(kernels, merge, "min")


class Dilatation(Morpho):
    """Morphological dilatation, based on :py:class:`morphomath.morpho.Morpho`."""

    def __init__(self, kernel):
        super().__init__(kernel, "max")

    @classmethod
    def from_decomposition(cls, kernels, merge):
        return super().from_decomposition(kernels, merge, "max")
