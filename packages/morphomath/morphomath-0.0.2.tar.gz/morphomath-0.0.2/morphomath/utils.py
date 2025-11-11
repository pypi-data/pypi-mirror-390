"""Pythonic tools."""

import os
import pathlib

import numpy as np


def get_compilation_rules() -> dict:
    """Return the extra compilation rules."""
    if os.environ.get("READTHEDOCS") == "True":  # if we are on readthedoc server
        extra_compile_args = [
            "-fopenmp",  # for threads
            "-fopenmp-simd",  # for single instruction multiple data
            "-lc",  # include standard c library
            "-lm",  # for math functions
            "-march=x86-64",  # uses local processor instructions for optimization
            "-mtune=generic",  # can be conflictual with march
            "-O1",  # faster to compile
            "-Wall", "-Wextra",  # activate warnings
            "-std=gnu11",  # use iso c norm (gnu23 not yet supported on readthedoc)
            "-pipe",  # use pipline rather than tempory files
        ]
    else:
        extra_compile_args = [
            "-fopenmp",  # for threads
            "-fopenmp-simd",  # for single instruction multiple data
            "-lc",  # include standard c library
            "-lm",  # for math functions
            "-march=native",  # uses local processor instructions for optimization
            "-mtune=native",  # can be conflictual with march
            "-O2",  # hight optimization, -O3 include -ffast-math
            "-ffast-math",  # not activated in -O2
            "-std=gnu18",  # use iso c norm
            "-flto=auto",  # enable link time optimization
            "-pipe",  # use pipline rather than tempory files
            # for debug only
            # "-fopt-info",
            # "-fopt-info-loop",
            # "-fopt-info-loop-missed",
            # "-fopt-info-vec",
            # "-fopt-info-vec-missed",
        ]
    # setuptools used sysconfig CC and CFLAGS by default,
    # it used environement var if it is defined.
    # to avoid undefined symbol: GOMP_loop_nonmonotonic_dynamic_start,
    # we have to add -fopenmp -fopenmp-simd before "extra_compile_args".
    os.environ["CC"] = "gcc"  # overwite default compiler
    os.environ["CFLAGS"] = " ".join(extra_compile_args)
    return {
        "define_macros": [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],  # for warning
        "extra_compile_args": extra_compile_args,
        # solvable localy with:
        # import ctypes
        # ctypes.CDLL('libgomp.so.1')
        # or in the shell with:
        # export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libgomp.so.1
        "extra_link_args": [
            "-fopenmp", "-shared", "-lmvec",  # avoid ImportError: ... .so undefined symbol: ...
        ],
        "include_dirs": [
            np.get_include(),  # requires for  #include <numpy/arrayobject.h>
            str(get_project_root().parent),  # requires for #include "morphomath/..."
        ],
    }


def get_project_root() -> pathlib.Path:
    """Return the absolute project root folder.

    Examples
    --------
    >>> from morphomath.utils import get_project_root
    >>> root = get_project_root()
    >>> root.is_dir()
    True
    >>> root.name
    'morphomath'
    >>> sorted(p.name for p in root.iterdir())  # doctest: +ELLIPSIS
    ['__init__.py', ...]
    >>>

    """
    return pathlib.Path(__file__).resolve().parent


def shift(tensor: np.ndarray, shift: tuple[int, ...]) -> np.ndarray:
    """Like np.roll with border duplication rather wrap-around."""
    assert isinstance(tensor, np.ndarray), tensor.__class__.__name__
    assert isinstance(shift, tuple | list), shift.__class__.__name__
    assert all(isinstance(s, int) for s in shift), shift
    assert len(shift) <= tensor.ndim, (shift, tensor.shape)

    has_copy: bool = False
    for i, dec in enumerate((0,)*(tensor.ndim-len(shift)) + shift):
        if dec > 0:
            bef, aft = (slice(None),)*i, (slice(None),)*(tensor.ndim-1-i)
            border = tensor[*bef, 0, *aft]
            if not has_copy:
                tensor, has_copy = tensor.copy(), True
            tensor[*bef, slice(dec, None), *aft] = tensor[*bef, slice(0, -dec), *aft].copy()
            tensor[*bef, slice(1, dec), *aft] = border[*bef, None, *aft]
        elif dec < 0:
            bef, aft = (slice(None),)*i, (slice(None),)*(tensor.ndim-1-i)
            border = tensor[*bef, -1, *aft]
            if not has_copy:
                tensor, has_copy = tensor.copy(), True
            tensor[*bef, slice(0, dec), *aft] = tensor[*bef, slice(-dec, None), *aft].copy()
            tensor[*bef, slice(dec, -1), *aft] = border[*bef, None, *aft]
    return tensor


def unravel_index(idx: int, shape: tuple[int, ...]) -> tuple[int, ...]:
    """Do like as np.unravel_index, inverse of itertools.product(*map(range, shape)).

    Examples
    --------
    >>> import itertools
    >>> from morphomath.utils import unravel_index
    >>> shape = (1, 2, 3, 4, 5, 6)
    >>> items = list(itertools.product(*map(range, shape)))
    >>> items[500]
    (0, 1, 1, 0, 3, 2)
    >>> unravel_index(500, shape)
    (0, 1, 1, 0, 3, 2)
    >>>

    """
    assert isinstance(idx, int), idx.__class__.__name__
    assert idx >= 0, idx
    assert isinstance(shape, tuple), shape.__class__.__name__
    assert all(isinstance(s, int) and s >= 0 for s in shape), shape
    if len(shape) == 1:
        assert idx < shape[0], f"the index {idx} is not possible for the shape {shape}"
        return (idx,)
    prod = shape[1]
    for coord in shape[2:]:
        prod *= coord
    return idx//prod, *unravel_index(idx%prod, shape[1:])
