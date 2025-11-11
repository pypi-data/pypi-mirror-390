"""Perfom the structuring elements patch decomposition using common subexpression elimination."""

import itertools

from morphomath.kernel import Kernel
from morphomath.utils import unravel_index

TYPE_VEC = tuple[int, ...]
TYPE_TOROID_POINT = tuple[TYPE_VEC, TYPE_VEC]


def initialisation(kernel: Kernel) -> list[set[TYPE_TOROID_POINT]]:
    """Return the lattice of structurant elements grid.

    This is the first step of block decomposition.

    Parameters
    ----------
    kernel : Kernel
        The structurant element to be strided on a grid.

    Returns
    -------
    lattice : list[set[TYPE_TOROID_POINT]]
        The ordered set of the folded kernel for each "atom" in the elementary lattice.
        In order to relate lattice congruence invariance of the kernel,
        The kernels are "rotated" to stay inside the main lattice.
        The first argument corresponds to the absolute lattice index to unfold the kernels.
        The second to the points coordinates inside the lattice.

    Examples
    --------
    >>> import pprint
    >>> from morphomath.kernel import Kernel
    >>> from morphomath.decomposition import initialisation
    >>> kernel = Kernel([[0, 1, 0], [0, 1, 0], [1, 1, 1]])
    >>> lattice = initialisation(kernel)
    >>> pprint.pprint(lattice, width=96)
    [{((-1, 0), (2, 0)), ((0, 0), (1, 1)), ((0, -1), (1, 2)), ((0, 0), (0, 0)), ((0, 0), (1, 0))},
     {((0, 0), (0, 1)), ((0, 0), (1, 1)), ((-1, 0), (2, 1)), ((0, 0), (1, 0)), ((0, 0), (1, 2))},
     {((0, 0), (0, 2)), ((-1, 0), (2, 2)), ((0, 0), (1, 1)), ((0, 1), (1, 0)), ((0, 0), (1, 2))},
     {((0, 0), (2, 1)), ((0, -1), (2, 2)), ((0, 0), (2, 0)), ((0, 0), (0, 0)), ((0, 0), (1, 0))},
     {((0, 0), (2, 1)), ((0, 0), (0, 1)), ((0, 0), (1, 1)), ((0, 0), (2, 0)), ((0, 0), (2, 2))},
     {((0, 0), (0, 2)), ((0, 0), (2, 1)), ((0, 0), (2, 2)), ((0, 1), (2, 0)), ((0, 0), (1, 2))},
     {((1, 0), (0, 1)), ((0, 0), (2, 0)), ((1, -1), (0, 2)), ((1, 0), (0, 0)), ((0, 0), (1, 0))},
     {((0, 0), (2, 1)), ((1, 0), (0, 1)), ((0, 0), (1, 1)), ((1, 0), (0, 0)), ((1, 0), (0, 2))},
     {((1, 0), (0, 1)), ((0, 0), (2, 2)), ((1, 1), (0, 0)), ((1, 0), (0, 2)), ((0, 0), (1, 2))}]
    >>> for tps in lattice:
    ...     print(Kernel.from_points([r + s*q for q, r, s in zip(*tp, kernel.shape)] for tp in tps))
    ...     print()
    ...
    · ● ·
    · 🕀 ·
    ● ● ●
    <BLANKLINE>
    · ● ·
    🕂 ● ·
    ● ● ●
    <BLANKLINE>
    · · ● ·
    🕂 · ● ·
    · ● ● ●
    <BLANKLINE>
    · 🕀 ·
    · ● ·
    ● ● ●
    <BLANKLINE>
    🕂 ● ·
    · ● ·
    ● ● ●
    <BLANKLINE>
    🕂 · ● ·
    · · ● ·
    · ● ● ●
    <BLANKLINE>
    · 🕂 ·
    · ● ·
    · ● ·
    ● ● ●
    <BLANKLINE>
    🕂 · ·
    · ● ·
    · ● ·
    ● ● ●
    <BLANKLINE>
    🕂 · · ·
    · · ● ·
    · · ● ·
    · ● ● ●
    <BLANKLINE>
    >>>

    """
    assert isinstance(kernel, Kernel), kernel.__class__.__name__
    return [
        {
            tuple(
                zip(*(divmod(p, s) for p, s in zip(point, kernel.shape, strict=True)), strict=True),
            )
            for point in kernel.shifted(shift, reverse=True).points
        }
        for shift in itertools.product(*map(range, kernel.shape))
    ]


def toroid_points_inter(
    tps1: set[TYPE_TOROID_POINT], tps2: set[TYPE_TOROID_POINT],
) -> set[TYPE_TOROID_POINT]:
    """Find all the common shifted subset of points.

    Parameters
    ----------
    tps1, tps2 : set[TYPE_TOROID_POINT]
        The 2 sets of toroid points, as a pair of "lattice shift" and "relative coords".

    Yields
    ------
    inter : set[TYPE_TOROID_POINT]
        A subset of ``tps1`` such that there exists a lattice shift ``s`` such that
        ``inter + s`` is also a subset of ``tps2``.

    Notes
    -----
    It is assumed there is unicity of the relative coord in the sets.

    Examples
    --------
    >>> from morphomath.decomposition import toroid_points_inter
    >>> tps1 = {((0,), (0,)), ((0,), (1,)), ((1,), (2,))}
    >>> list(toroid_points_inter(tps1, {((0,), (0,)), ((10,), (1,)), ((11,), (2,))}))
    [{((0,), (0,))}, {((0,), (1,)), ((1,), (2,))}]
    >>>

    """
    rel_to_lat_2 = {rel: lat for lat, rel in tps2}  # ok because unicity assumption
    while tps1:
        lat1, rel = next(iter(tps1))
        if (lat2 := rel_to_lat_2.get(rel)) is None:
            tps1 = tps1 - {(lat1, rel)}  # not inplace
            continue
        shift = tuple(l1 - l2 for l1, l2 in zip(lat1, lat2, strict=True))
        subset = tps1 & {
            (tuple(li + si for li, si in zip(tp[0], shift, strict=True)), tp[1]) for tp in tps2
        }
        yield subset
        tps1 = tps1 - subset


def is_toroid_point_subset(
    mainset: set[TYPE_TOROID_POINT], subset: set[TYPE_TOROID_POINT], *, return_shift: bool = False,
) -> bool:
    """Return True if it exists a shift ``s`` such as ``subset + s`` is a subset of ``mainset``.

    Parameters
    ----------
    mainset : set[TYPE_TOROID_POINT]
        A big set of points.
    subset : set[TYPE_TOROID_POINT]
        A lattice shifted subset of ``mainset``.
    return_shift : boolean, default=False
        If True, return the shift value (or None) rather than a boolean.
        If False (default case) retun a boolean

    Returns
    -------
    boolean or TYPE_TOROID_PIONT
        True if ``subset`` is indeed a shifted subsample of ``mainset``.
        False overwise.

    Notes
    -----
    It is assumed there is unicity of the relative coord in the sets.

    Examples
    --------
    >>> from morphomath.decomposition import is_toroid_point_subset
    >>> mainset = {((0,), (0,)), ((0,), (1,)), ((1,), (2,))}
    >>> is_toroid_point_subset(mainset, {((10,), (1,)), ((11,), (2,))})
    True
    >>> is_toroid_point_subset(mainset, {((10,), (1,)), ((10,), (2,))})
    False
    >>>

    """
    rel_to_lat = {rel: lat for lat, rel in mainset}
    shifts = set()
    for sub_lat, rel in subset:
        if (main_lat := rel_to_lat.get(rel)) is None:
            return None if return_shift else False
        shift = tuple(l1 - l2 for l1, l2 in zip(main_lat, sub_lat, strict=True))
        shifts.add(shift)
        if len(shifts) > 1:
            return None if return_shift else False
    try:
        return shifts.pop() if return_shift else True
    except KeyError:  # if subset is an empty set
        return None


def sum_vect(vect1: TYPE_VEC, vect2: TYPE_VEC) -> TYPE_VEC:
    """Vectorial elementwise sum."""
    return tuple(v1 + v2 for v1, v2 in zip(vect1, vect2, strict=True))


def one_step_decomposition(
    lattice: list[set[TYPE_TOROID_POINT]],
) -> tuple[list[set[TYPE_TOROID_POINT]], dict[int, set[tuple[int, TYPE_VEC]]]]:
    """Perform a decomposition step.

    Parameters
    ----------
    lattice : list[set[TYPE_TOROID_POINT]]
        An ordered set of sub-kernels to be decomposed one more time.

    Yields
    ------
    next_lattice : list[Kernel]
        An other latice with a sub decomposition.
        We allway have ``len(next_lattice) = len(lattice) + 1``.
    merge_table : dict[int, set[tuple[int, TYPE_VEC]]]
        To each kernel indice in lattice,
        associate the list of the kernel indices (and the anchor) to be merged in the new lattice.

    Examples
    --------
    >>> import pprint
    >>> from morphomath.kernel import Kernel
    >>> from morphomath.decomposition import initialisation, one_step_decomposition
    >>> lattice = initialisation(Kernel([1, 1, 1], anchor=(0,)))
    >>> pprint.pprint(next(iter(one_step_decomposition(lattice))))
    ([{((0,), (2,)), ((0,), (1,))},
      {((0,), (0,))},
      {((1,), (0,))},
      {((1,), (1,)), ((0,), (2,)), ((1,), (0,))}],
     {0: {(1, (0,)), (0, (0,))}, 1: {(2, (0,)), (0, (0,))}, 2: {(3, (0,))}})

    """
    zero_shift = (0,) * len(next(iter(lattice[0]))[1])

    # search all sub kernels
    intersections: list[set[TYPE_TOROID_POINT]] = [
        subset
        for i, k1 in enumerate(lattice[:-1])
        for k2 in lattice[i+1:]
        for subset in toroid_points_inter(k1, k2)
        if len(subset) >= 2  # noqa: PLR2004
    ]

    # perform substitutions
    for subset in intersections:
        new_lattice = [subset]
        merge_table: dict[int, set[tuple[int, TYPE_VEC]]] = {}
        for i, toroid_points in enumerate(lattice):
            # case no substitution
            if (shift := is_toroid_point_subset(toroid_points, subset, return_shift=True)) is None:
                merge_table[i] = {(len(new_lattice), zero_shift)}
                new_lattice.append(toroid_points)
                continue
            # case substitution
            sub_toroid_points = (
                toroid_points
                - {
                    (tuple(li + si for li, si in zip(l_, shift, strict=True)), r)
                    for (l_, r) in subset
                }
            )  # not inplace!
            if not sub_toroid_points:
                merge_table[i] = {(0, shift)}
                continue
            merge_table[i] = {(0, shift), (len(new_lattice), zero_shift)}
            new_lattice.append(sub_toroid_points)
        yield new_lattice, merge_table


def all_steps_decomposition(
    lattice: list[set[TYPE_TOROID_POINT]],
    _merge: dict[int, set[tuple[int, TYPE_VEC]]] | None = None,
) -> tuple[list[set[TYPE_TOROID_POINT]], dict[int, set[tuple[int, TYPE_VEC]]]]:
    """Recursive version of :py:func:`one_step_decomposition`.

    Parameters
    ----------
    lattice : list[set[TYPE_TOROID_POINT]]
        A list of kernels to be totaly decomposed.

    Yields
    ------
    final_lattice : list[set[TYPE_TOROID_POINT]]
        The fully decomposed kernels.
    merge_steps : dict[int, set[tuple[int, TYPE_VEC]]]
        To each final kernel index, associate the index
        of the kernels to be merged from the ``final_lattice`` list.

    Examples
    --------
    >>> import pprint
    >>> from morphomath.kernel import Kernel
    >>> from morphomath.decomposition import initialisation, all_steps_decomposition
    >>> lattice = initialisation(Kernel([[1, 0, 0], [1, 1, 0], [0, 1, 1]]))
    >>> latt, steps = next(iter(all_steps_decomposition(lattice)))
    >>> pprint.pprint([sorted(kernel) for kernel in latt])
    [[((0, 0), (1, 1)), ((0, 0), (2, 2))],
     [((0, 0), (1, 0)), ((0, 0), (2, 1))],
     [((0, -1), (1, 2)), ((0, 0), (2, 0))],
     [((0, 0), (0, 1)), ((0, 0), (1, 2))],
     [((0, -1), (0, 2)), ((0, 0), (1, 0))],
     [((0, 0), (0, 0)), ((0, 0), (1, 1))],
     [((-1, -1), (2, 2))],
     [((-1, 0), (2, 0))],
     [((-1, 0), (2, 1))],
     [((0, 0), (2, 1))],
     [((0, 0), (2, 2))],
     [((0, 1), (2, 0))],
     [((0, -1), (2, 2)), ((1, 0), (0, 0)), ((1, 0), (0, 1))],
     [((0, 0), (2, 0)), ((1, 0), (0, 1)), ((1, 0), (0, 2))],
     [((0, 0), (2, 1)), ((1, 0), (0, 2)), ((1, 1), (0, 0))]]
    >>> pprint.pprint(steps)
    {0: {(5, (0, 0)), (6, (0, 0)), (4, (0, 0))},
     1: {(5, (0, 0)), (3, (0, 0)), (7, (0, 0))},
     2: {(8, (0, 0)), (3, (0, 0)), (4, (0, 1))},
     3: {(2, (0, 0)), (9, (0, 0)), (4, (0, 0))},
     4: {(5, (0, 0)), (1, (0, 0)), (10, (0, 0))},
     5: {(11, (0, 0)), (3, (0, 0)), (0, (0, 0))},
     6: {(2, (0, 0)), (12, (0, 0))},
     7: {(13, (0, 0)), (1, (0, 0))},
     8: {(0, (0, 0)), (14, (0, 0))}}
    >>>

    """
    if _merge is None:
        zero_shift = (0,) * len(next(iter(lattice[0]))[1])
        _merge: dict[int, set[tuple[int, TYPE_VEC]]] = {
            i: {(i, zero_shift)} for i in range(len(lattice))
        }
    has_sub_dec: bool = False
    for sub_kernels, sub_merge in one_step_decomposition(lattice):
        has_sub_dec = True
        new_merge = {
            i: {
                (new_ker_idx, sum_vect(new_mod, old_mod))
                for old_ker_idx, old_mod in old_merges
                for new_ker_idx, new_mod in sub_merge[old_ker_idx]
            }
            for i, old_merges in _merge.items()
        }
        yield from all_steps_decomposition(sub_kernels, new_merge)
    if not has_sub_dec:
        yield lattice, _merge


def full_decomposition(
    kernel: Kernel,
) -> tuple[list[Kernel], dict[TYPE_VEC, set[tuple[int, TYPE_VEC]]]]:
    """Find all the possible decompositions.

    Parameters
    ----------
    kernel : Kernel
        The structurant element to be "convolved" on an infinite grid.

    Returns
    -------
    kernels : list[Kernel]
        The fully decomposed kernels.
    merge : dict[int, set[tuple[int, TYPE_VEC]]]
        To each final kernel index (in the lattice), associate the index
        of the kernels to be merged from the ``kernels`` list.

    """
    lattice = initialisation(kernel)
    final_lattice, merge_steps = next(iter(all_steps_decomposition(lattice)))
    all_kernels_new = [
        Kernel.from_points(
            [r + s*q for q, r, s in zip(*tp, kernel.shape, strict=True)] for tp in tps
        )
        for tps in final_lattice
    ]
    merge_steps_new = {
        unravel_index(idx, kernel.shape): fusion
        for idx, fusion in merge_steps.items()
    }
    return all_kernels_new, merge_steps_new
