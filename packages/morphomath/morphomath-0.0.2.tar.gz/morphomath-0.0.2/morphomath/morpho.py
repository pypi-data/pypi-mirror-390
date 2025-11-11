"""Full pipeline."""

import functools
import typing

import numpy as np

from .decomposition import full_decomposition
from .kernel import Kernel
from .utils import shift


class Morpho:
    """Perform the kernel subdivision and the morphological operation.

    Attributes
    ----------
    kernel : Kernel
        The kernel used for the decomposition (readonly).
    kernels : list[Kernel]
        The sub kernel used, all decomposition parts.
    ndim : int
        The number of dimensions.
    operator : str
        The collapse function used (readonly).
    stride : tuple[int, ...]
        The step to be applied to each decomposed element.

    """

    def __init__(
        self,
        kernel: Kernel | np.ndarray | list | tuple | set | frozenset,
        operator: str,
    ) -> None:
        """Instanciate the image operator with a specific kernel and collaps function.

        Parameters
        ----------
        kernel : Kernel or arraylike or points
            The structurant element for the morphological operation,
            forwarded to :py:class:`morphomath.kernel.Kernel`.
        operator : str
            The function to collapse the values, it as to be **associative** and **commutative**.
            Currently, the supported functions are ``min``, ``max``, ``+``, and ``*``.

        """
        assert isinstance(operator, str), operator.__class__.__name__
        assert operator in {"min", "max", "+", "*"}, operator
        kernel = Kernel(kernel)
        self._operator = operator
        self._kernels = [kernel]
        zero_vect = (0,)*kernel.ndim
        self._merge = {zero_vect: {(0, zero_vect)}}

    def decomposed(self) -> typing.Self:
        """Search a kernel subdivision, return a new Morpho instance."""
        kernels, merge = full_decomposition(self.kernel)
        return Morpho.from_decomposition(kernels, merge, self._operator)

    @classmethod
    def from_decomposition(
        cls,
        kernels: list[Kernel | np.ndarray | list | tuple | set | frozenset],
        merge: dict[tuple[int, ...], set[tuple[int, tuple[int, ...]]]],
        operator: str,
    ) -> typing.Self:
        """Create an Operator instance from the decomposition.

        Parameters
        ----------
        kernels : list[Kernel]
            An **ordered** iterable of little **kernelike** structurant elements.
        merge : dict
            At each final coordinate, says how to group the small kernels.
        operator : str
            Same as __init__.

        """
        # verification kernels
        assert hasattr(kernels, "__iter__"), kernels.__class__.__name__
        kernels = [Kernel(k) for k in kernels]
        if len(dims := {k.ndim for k in kernels}) != 1:
            msg = f"the structural elements do not all have the same number of dimensions {dims}"
            raise AssertionError(
                msg,
            )
        dims = dims.pop()

        # verification merge
        assert isinstance(merge, dict), merge.__class__.__name__
        # keys
        assert all(
            isinstance(k, tuple) and len(k) == dims and all(isinstance(c, int) for c in k)
            for k in merge
        ), f"merge keys ({list(merge)}) are not all {dims} tuple of int"
        stride = tuple(max(d) + 1 for d in zip(*merge, strict=True))
        assert np.prod(stride) == len(merge), (
            f"the merge table is incomplete, because {len(merge)} compositions are provided, "
            f"but with a stride of {stride}, {np.prod(stride)} are requires, "
            f"provided keys are {sorted(merge)}"
        )
        # values
        assert all(
            isinstance(v, set) and all(isinstance(m, tuple) for m in v)
            for v in merge.values()
        ), f"merge values ({list(merge.values())}) are not a set of tuple"

        # operator
        assert isinstance(operator, str), operator.__class__.__name__
        assert operator in {"min", "max", "+", "*"}, operator

        # recomposition
        grouped = {
            pos: functools.reduce(
                Kernel.__or__,
                (
                    kernels[idx].shifted(-s*m for s, m in zip(stride, mod, strict=True))
                    for idx, mod in fus
                ),
            )
            for pos, fus in merge.items()
        }

        # verification same kernel
        if len(kernel := {k.shifted(k.anchor, reverse=True) for k in grouped.values()}) != 1:
            msg = (
                f"the fusion of the kernels {kernels} with the rule {merge} give several kernels "
                f"{kernel}, witch is not unique"
            )
            raise AssertionError(msg)

        # creation of the new instance
        morpho = cls.__new__(cls)
        morpho._operator = operator  # noqa: SLF001
        morpho._kernels = kernels  # noqa: SLF001
        morpho._merge = merge  # noqa: SLF001
        return morpho

    @functools.cached_property
    def kernel(self) -> Kernel:
        """Return the kernel used for the decomposition."""
        stride = self.stride
        return functools.reduce(
            Kernel.__or__,
            (
                self._kernels[idx].shifted(-s*m for s, m in zip(stride, mod, strict=True))
                for idx, mod in self._merge[(0,)*len(stride)]
            ),
        )

    @property
    def kernels(self) -> list[Kernel]:
        """Return the sub kernel used, all decomposition parts."""
        return self._kernels

    @property
    def ndim(self) -> int:
        """Return the number of dimensions."""
        return self._kernels[0].ndim

    @property
    def operator(self) -> str:
        """Return the collapse function used."""
        return self._operator

    @property
    def stride(self) -> tuple[int, ...]:
        """Return the step to be applied to each decomposed element."""
        return tuple(max(d) + 1 for d in zip(*self._merge, strict=True))

    def __call__(self, image: np.ndarray) -> np.ndarray:
        """Perform the morphological operation on the image.

        Examples
        --------
        >>> import cv2
        >>> import morphomath
        >>> path = morphomath.utils.get_project_root() / "media" / "image.png"
        >>> img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        >>> ero = morphomath.Erosion([[0, 1, 0], [0, 1, 0], [1, 1, 1]]).decomposed()
        >>> ero(img)
        array([[  0,   0,   0, ...,   0, 255,   0],
               [  0,   0,   0, ...,   0,   0,   0],
               [  0,   0,   0, ...,   0, 255,   0],
               ...,
               [  0,   0,   0, ..., 255, 255, 255],
               [  0,   0,   0, ...,   0,   0,   0],
               [  0,   0,   0, ...,   0,   0,   0]], shape=(360, 360), dtype=uint8)
        >>>

        """
        assert isinstance(image, np.ndarray), image.__class__.__name__
        assert image.ndim >= self.ndim, (
            f"the image {image.shape} requieres at least {self.ndim} dimensions"
        )

        # padding
        shape = [sh//st for st, sh in zip(self.stride, image.shape[-self.ndim:], strict=True)]
        before = tuple(
            -min(c) for c in zip(*(p for k in self._kernels for p in k.points), strict=True)
        )
        after = self.stride  # this margin can be smaller, to avoid computational waste
        src = np.pad(image, tuple(zip(before, after, strict=True)), mode="edge")

        # reduction function
        operator = {
            "min": np.minimum, "max": np.maximum, "+": sum, "*": lambda x, y: x*y,
        }[self.operator]

        # operation on all subdivised kernels
        premices = [
            functools.reduce(
                operator,
                [
                    src[
                        ...,
                        *(
                            slice(c+b, c+b+d*s, s)
                            for c, d, s, b in zip(point, shape, self.stride, before, strict=True)
                        ),
                    ]
                    for point in kernel.points
                ],
            )
            for kernel in self._kernels
        ]

        # group subkernels
        dst = np.empty(
            image.shape[:-self.ndim] + tuple(d*s for d, s in zip(shape, self.stride, strict=True)),
            dtype=image.dtype,
        )
        for anchor, fusion in self._merge.items():
            idx_np = (
                ...,
                *(
                    slice(a, a+d*s, s)
                    for a, d, s in zip(anchor, shape, self.stride, strict=True)
                ),
            )
            dst[idx_np] = functools.reduce(
                operator,
                (
                    shift(premices[idx], tuple(-m for m in mod))
                    for idx, mod in fusion
                ),
            )

        return dst

    def __repr__(self) -> str:
        """Give an evaluable version of self."""
        if len(self._kernels) == 1:
            return f"Morpho({self.kernel!r}, {self._operator!r})"
        return f"Morpho.from_decomposition({self._kernels}, {self._merge}, {self._operator!r})"

    def __str__(self) -> str:
        """Return a full human readable description of the operation."""
        operation = {"min": "erosion", "max": "dilatation"}.get(self._operator, self._operator)
        # main info
        title = f"Perform a {self.ndim}d morphological {operation}.\n"
        kernel = f"The main kernel is:\n    {'\n    '.join(str(self.kernel).split('\n'))}\n"
        comp = (
            sum(len(k)-1 for k in self._kernels)
            + sum(len(m)-1 for m in self._merge.values())
        ) / len(self._merge)
        stats = (
            f"With the naive method, there is {len(self.kernel)-1} comparisons per 'pixel'.\n"
            f"With this decomposition, there is {comp:.2f} comparisons per 'pixel' in average.\n"
        )
        # decomposition
        kernels = [str(k).split("\n") for k in self._kernels]  # list of lines
        kernels = [[f"{i:^{len(k[0])}}", *k] for i, k in enumerate(kernels)]  # add header
        size = max(len(k) for k in kernels)
        kernels = [(k+[""]*size)[:size] for k in kernels]
        kernels = [[f"{line:<{len(k[0])}}" for line in k] for k in kernels]  # pad lines same length
        kernels = "\n".join("|".join(full_line) for full_line in zip(*kernels, strict=True))
        kernels = "\n".join(line.rstrip() for line in kernels.split("\n"))  # remove leading spaces
        # merge
        merge = "\n".join(
            f"cluster {i}: {' and '.join(f'ker {j} > {mod}' for j, mod in sorted(self._merge[i]))}"
            for i in sorted(self._merge)
        )
        decomposition = (
            f"A stride {self.stride} morphology is performed with each of these kernels:\n"
            "\n"
            f"{kernels}"
            "\n"
            f"Then, there are merged in {len(self._merge)} clusters:\n"
            f"{merge}"
        )
        return title + "\n" + kernel + "\n" + stats + "\n" + decomposition
