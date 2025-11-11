"""Provide tools for simple manipulation of a structuring element."""

import numbers
import typing

import numpy as np


class Kernel:
    """A morphological structuring element with a dual representation.

    Attributes
    ----------
    anchor : tuple[int, ...]
        The algebrical coordinate of the anchor voxel.
    ndim : int
        The number of dimensions.
    shape : tuple[int, ...]
        The shape of the structurant element.
    struct_elem : np.ndarray[np.uint8, ...]
        The binary structurant element as a readonly numpy array.
    points : frozenset[tuple[int, ...]]
        All the nonzero kernel point coordinates (readonly).
    points_array : np.ndarray[np.int64, np.int64]
        The 2d numpy array of the individuals, sorted in lexicographic order.
        By convention, the shape is (nbr_points, ndim).
        It is a readonly array.

    """

    def __init__(
        self,
        kernel: np.ndarray | list | tuple | set | frozenset,
        anchor: typing.Iterable[numbers.Integral] | None = None,
    ) -> None:
        """Initialise the kernel with an image patch or a set of points.

        Parameters
        ----------
        kernel : arraylike or points set
            If an ordered arraylike is provided,
            it is considered as the binary "convolution" kernel.
            Overwise, it is assumed to be the set of the nonzero kernel point coordinates.
        anchor : list[int], optional
            If provided, it is the coordinate of the anchor point of the "convolutive" kernel.

        """
        # declaration
        self._anchor: tuple[int, ...] = None
        self._points: frozenset[tuple[int, ...]] = None
        self._struct_elem: np.ndarray[np.uint8, ...] = None

        match kernel:
            case Kernel():
                self._anchor = kernel._anchor  # noqa: SLF001
                self._points = kernel._points  # noqa: SLF001
                self._struct_elem = kernel._struct_elem  # noqa: SLF001
            case set() | frozenset():  # case cloud point
                self._points = self.from_points(kernel)._points  # noqa: SLF001
                assert anchor is None, (
                    "The anchor point can be deduced from the points,"
                    "so you musn't to specify it again."
                )
            case np.ndarray() | list() | tuple():  # case structurant element
                self._struct_elem = self.from_struct_elem(kernel)._struct_elem  # noqa: SLF001
                if anchor is not None:
                    self._anchor = tuple(map(int, anchor))
                    assert len(self._anchor) == self._struct_elem.ndim
            case _:
                msg = f"not valid kernel type {kernel}"
                raise ValueError(msg)

    def _init(self) -> None:
        """Set the attributes to None."""
        self._anchor = self._points = self._struct_elem = None

    @property
    def anchor(self) -> tuple[int, ...]:
        """Return the algebrical coordinate of the anchor voxel.

        Examples
        --------
        >>> from morphomath.kernel import Kernel
        >>> Kernel({(-1, 0), (-1, 1), (0, 1)}).anchor
        (1, 0)
        >>> Kernel([[1, 1, 1], [1, 1, 1], [1, 1, 1]]).anchor
        (1, 1)
        >>>

        """
        if self._anchor is None:
            if self._points is not None:
                self._anchor = tuple(-min(d) for d in zip(*self._points, strict=True))
            else:
                self._anchor = tuple((s-1)//2 for s in self._struct_elem.shape)
        return self._anchor

    def copy(self) -> typing.Self:
        """Return an independent copy of self."""
        cls = self.__class__
        copy = cls.__new__(cls)
        copy._init()  # noqa: SLF001
        copy._anchor = self._anchor  # noqa: SLF001
        copy._points = self._points  # noqa: SLF001
        copy._struct_elem = self._struct_elem  # noqa: SLF001
        return copy

    @classmethod
    def from_points(cls, points: typing.Iterable) -> typing.Self:
        """Create a kernel from the nonzero kernel point coordinates.

        Parameters
        ----------
        points : set
            All the points of the structurant element, relative to the anchor.
            It can not be empty, at least one point must to be provided.

        Returns
        -------
        kernel : Kernel
            A new instance of a kernel from this points.

        Examples
        --------
        >>> from morphomath.kernel import Kernel
        >>> Kernel({(-1, 0), (-1, 1), (0, 1)})
        Kernel({(-1, 0), (-1, 1), (0, 1)})
        >>>

        """
        assert hasattr(points, "__iter__"), points.__class__.__name__
        _points = set()
        for point in points:
            _points.add(tuple(map(int, point)) if hasattr(point, "__iter__") else (int(point),))
        assert len(_points) != 0, "you must to provide at least one point"
        dims = {len(p) for p in _points}
        assert len(dims) == 1, f"not all points are the same dimension {dims}"

        kernel = cls.__new__(cls)
        kernel._init()  # noqa: SLF001
        kernel._points = frozenset(_points)  # noqa: SLF001
        return kernel

    @classmethod
    def from_struct_elem(cls, struct_elem: np.ndarray | list | tuple) -> typing.Self:
        """Create a kernel from the structurant element.

        Parameters
        ----------
        struct_elem : arraylike
            The binary structurant element.

        Returns
        -------
        kernel : Kernel
            A new instance of a kernel from this structurant element.

        Examples
        --------
        >>> from morphomath.kernel import Kernel
        >>> Kernel([[1, 1], [0, 1]])
        Kernel([[1, 1], [0, 1]])
        >>>

        """
        struct_elem = np.asarray(struct_elem, dtype=np.bool).view(np.uint8)
        assert struct_elem.any(), "the structurant element must be not empty"

        kernel = cls.__new__(cls)
        kernel._init()  # noqa: SLF001
        kernel._struct_elem = struct_elem  # noqa: SLF001
        return kernel

    def match_sub_kernel(self, sub_kernel: typing.Self) -> tuple[int, ...]:
        """Find all possible translations of `sub_kernel` such that it is included in self.

        In other words, search all shift `s` such as
        `sub_kernel.shift(s).struct_elem in self.struct_elem[:shape1, :shape2, ...]`.
        Considering the anchors of `sub_kernel` and `self` are 0.

        Parameters
        ----------
        sub_kernel : Kernel
            The sub-element we are trying to fit into self.

        Yields
        ------
        shift : tuple[int, ...]
            Considering the anchors of `self` and `sub_kernel` are coincident,
            it corresponds to the translation to be applyed to `sub_kernel`,
            in order to make `sub_kernel` fitting inside `self` at this position.

        Examples
        --------
        >>> from morphomath.kernel import Kernel
        >>> ref = Kernel([[1, 1, 1], [1, 0, 1], [1, 1, 1]], anchor=(0, 0))
        >>> list(ref.match_sub_kernel(Kernel([[1, 1]], anchor=(0, 0))))
        [(0, 0), (0, 1), (2, 0), (2, 1)]
        >>>

        """
        def _is_in(
            self_pts: list[tuple[int, ...]],
            other_pts: list[tuple[int, ...]],
            shift: tuple[int, ...],
        ) -> bool:
            """Return True if shifted other_pts is a subset of self_pts."""
            if not other_pts:
                return True
            other_pts_0_shifted = tuple(o + s for o, s in zip(other_pts[0], shift, strict=True))
            for j in range(len(self_pts)-len(other_pts)+1):
                if other_pts_0_shifted == self_pts[j]:
                    return _is_in(self_pts[j+1:], other_pts[1:], shift)
            return False

        self_points, other_points = sorted(self.points), sorted(Kernel(sub_kernel).points)
        for i in range(len(self_points)-len(other_points)+1):
            shift = tuple(  # vectorization of self_points[i] - other_points[0]
                s - o for s, o in zip(self_points[i], other_points[0], strict=True)
            )
            if _is_in(self_points[i+1:], other_points[1:], shift):
                yield shift

    @property
    def ndim(self) -> int:
        """Return the number of dimensions."""
        if self._struct_elem is not None:
            return self._struct_elem.ndim
        return len(next(iter(self._points)))

    @property
    def points(self) -> frozenset[tuple[int, ...]]:
        """Return all the nonzero kernel point coordinates.

        Examples
        --------
        >>> from morphomath.kernel import Kernel
        >>> sorted(Kernel([[1, 1], [0, 1]]).points)
        [(0, 0), (0, 1), (1, 1)]
        >>>

        """
        if self._points is None:
            self._points = frozenset(zip(
                *(
                    (d-a).tolist()
                    for a, d in zip(self.anchor, self._struct_elem.nonzero(), strict=True)
                ),
                strict=True,
            ))
        return self._points

    @property
    def points_array(self) -> np.ndarray[np.int64, np.int64]:
        """Return the sorted points.

        Examples
        --------
        >>> from morphomath.kernel import Kernel
        >>> Kernel([[0, 1, 0], [0, 1, 0], [1, 1, 1]]).points_array
        array([[-1,  0],
               [ 0,  0],
               [ 1, -1],
               [ 1,  0],
               [ 1,  1]])
        >>>

        """
        return np.asarray(sorted(self.points))

    @property
    def shape(self) -> tuple[int, ...]:
        """Return the shape of the structurant element."""
        if self._struct_elem is not None:
            return self._struct_elem.shape
        return tuple(max(d) - min(d) + 1 for d in zip(*self._points, strict=True))

    def shift(
        self, shift: typing.Iterable[numbers.Integral], *, reverse: bool = False,
    ) -> typing.Self:
        """Translate the anchor point of the shift value inplace."""
        assert isinstance(reverse, bool), reverse.__class__.__name__
        shift = tuple(map(int, shift))
        assert len(shift) == self.ndim, f"shift ({shift}) must contains {self.ndim} coordinates"
        if reverse:
            shift = tuple(-s for s in shift)
        if self._points is not None:
            self._points = frozenset(
                tuple(pi-s for pi, s in zip(p, shift, strict=True)) for p in self._points
            )
            self._anchor = None
        else:
            self._anchor = tuple(a+s for a, s in zip(self.anchor, shift, strict=True))
        return self

    def shifted(
        self, shift: typing.Iterable[numbers.Integral], *, reverse: bool = False,
    ) -> typing.Self:
        """Outplace alias of ``self.copy().shift(shift, reverse=reverse)``."""
        return self.copy().shift(shift, reverse=reverse)

    @property
    def struct_elem(self) -> np.ndarray[np.uint8, ...]:
        """Return the binary structurant element as a readonly numpy array.

        Examples
        --------
        >>> from morphomath.kernel import Kernel
        >>> Kernel({(-1, 0), (-1, 1), (0, 1)}).struct_elem
        array([[1, 1],
               [0, 1]], dtype=uint8)
        >>>

        """
        if self._struct_elem is None:
            shape = [max(d) - min(d) + 1 for d in zip(*self._points, strict=True)]
            self._struct_elem = np.zeros(shape, np.uint8)
            mini = [min(d) for d in zip(*self._points, strict=True)]
            points = [[c-m for c, m in zip(p, mini, strict=True)] for p in self._points]
            self._struct_elem[*zip(*points, strict=True)] = 1
            self._struct_elem.flags.writeable = False
        return self._struct_elem

    def __and__(self, other: typing.Self) -> typing.Self:
        """Return the intersection of the points (self & other)."""
        assert isinstance(other, Kernel), other.__class__.__name__
        return Kernel.from_points(self.points & other.points)

    def __array__(self) -> np.ndarray[np.uint8, ...]:
        """Alias to self.struct_elem."""
        return self.struct_elem

    def __contains__(self, other: typing.Self) -> bool:
        """Test if other is in self.

        Examples
        --------
        >>> from morphomath.kernel import Kernel
        >>> Kernel([[1, 0], [0, 1]]) in Kernel([[0, 0, 1], [0, 1, 1], [1, 0, 1]])
        True
        >>> Kernel([[1, 0], [1, 1]]) in Kernel([[0, 0, 1], [0, 1, 1], [1, 0, 1]])
        False
        >>>

        """
        try:
            next(iter(self.match_sub_kernel(other)))
        except StopIteration:
            return False
        return True

    def __eq__(self, other: typing.Self) -> bool:
        """Return True if the structurant elements and the anchors are the same."""
        other = Kernel(other)
        if self.anchor != other.anchor:
            return False
        return self.points == other.points

    def __hash__(self) -> int:
        """Make the kernel hashable.

        The value depends of the anchor point.
        """
        return hash(self.points)

    def __len__(self) -> int:
        """Return the numbers of non zero voxels in the structurant element."""
        return len(self.points)

    def __or__(self, other: typing.Self) -> typing.Self:
        """Return the union of the points (self | other)."""
        assert isinstance(other, Kernel), other.__class__.__name__
        return Kernel.from_points(self.points | other.points)

    def __repr__(self) -> str:
        """Create an executable repetable representation of self."""
        points_kernel = "{" + ", ".join(map(str, sorted(self.points))) + "}"
        struct_elem_kernel = str(self.struct_elem.tolist())
        if tuple((s-1)//2 for s in self.struct_elem.shape) != self.anchor:
            struct_elem_kernel += f", anchor={self.anchor}"
        kernel = min([points_kernel, struct_elem_kernel], key=len)
        return f"{self.__class__.__name__}({kernel})"

    def __str__(self) -> str:
        """Return a unicode human readable nice representation of the kernel.

        Examples
        --------
        >>> from morphomath.kernel import Kernel
        >>>
        >>> # 1d
        >>> print(Kernel([1, 0, 1, 1]))
        ● 🕂 ● ●
        >>> print(Kernel([1, 0, 1, 1], anchor=(2,)))
        ● · 🕀 ●
        >>> print(Kernel([1, 0, 1, 1], anchor=(-2,)))
        🕂 · ● · ● ●
        >>> print(Kernel([1, 0, 1, 1], anchor=(5,)))
        ● · ● ● · 🕂
        >>>
        >>> # 2d
        >>> print(Kernel([[0, 1, 0], [0, 1, 0], [1, 1, 1]]))
        · ● ·
        · 🕀 ·
        ● ● ●
        >>> print(Kernel([[0, 1, 0], [0, 1, 0], [1, 1, 1]], anchor=(-2, 4)))
        · · · · 🕂
        · · · · ·
        · ● · · ·
        · ● · · ·
        ● ● ● · ·
        >>>
        >>> # nd
        >>> print(Kernel([[[1, 1], [0, 1], [0, 0]], [[0, 0], [1, 0], [1, 1]]]))
        [[ 0 -1  0]
         [ 0 -1  1]
         [ 0  0  1]
         [ 1  0  0]
         [ 1  1  0]
         [ 1  1  1]]
        >>>

        """
        def select(pts: frozenset[tuple[int, ...]], dim: int) -> set[int]:
            return {p[dim] for p in pts}

        symbols = {
            (False, False): "\u00b7",  # empty
            (False, True): chr(0x1f542),  # empty target
            (True, False): "\u25cf",  # filled
            (True, True): chr(0x1f540),  # filled target
        }
        match self.ndim:
            case 1:
                kernel = [
                    symbols[((i,) in self.points, i == 0)]
                    for i in range(
                        min(0, *select(self.points, 0)),
                        max(0, *select(self.points, 0)) + 1,
                        1,
                    )
                ]
                return " ".join(kernel)
            case 2:
                kernel = [
                    [
                        symbols[((i, j) in self.points, (i, j) == (0, 0))]
                        for j in range(
                            min(0, *select(self.points, 1)),
                            max(0, *select(self.points, 1)) + 1,
                            1,
                        )
                    ]
                    for i in range(
                        min(0, *select(self.points, 0)),
                        max(0, *select(self.points, 0)) + 1,
                        1,
                    )
                ]
                return "\n".join(" ".join(line) for line in kernel)
        return str(self.points_array)
