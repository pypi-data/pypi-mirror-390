#!/usr/bin/env python3

"""Write the source code of a specific decomposition."""


from morphomath.kernel import Kernel
from morphomath.utils import get_project_root


class Printer:
    """Draw the full C code of a given morphological decomposition."""

    def __init__(self, kernel: Kernel, kernels: list[Kernel], merge: dict):
        """Initialise the printer for a given decomposition.

        Parameters
        ----------
        kernel : Kernel
            The original full kernel.
        kernels : list[Kernel]
            The decompositions.
        merge : dict
            The way to combine the decomposition.
        """
        assert isinstance(kernel, Kernel), kernel.__class__.__name__
        assert isinstance(kernels, list), kernels.__class__.__name__
        assert all(isinstance(k, Kernel) for k in kernels), kernels
        assert isinstance(merge, dict), merge.__class__.__name__

        self._kernel = kernel
        self._kernels = kernels
        self._merge = merge

        self._ndim = self._kernel.ndim

    def draw_description(self) -> str:
        """Return a multiline description of this specific decomposition.

        Examples
        --------
        >>> from morphomath.decomposition import full_decomposition
        >>> from morphomath.kernel import Kernel
        >>> from morphomath.printer import Printer
        >>> kernel = Kernel([[0, 1, 0], [0, 1, 0], [1, 1, 1]])
        >>> kernels, merge = full_decomposition(kernel)
        >>> printer = Printer(kernel, kernels, merge)
        >>> print(printer.draw_description())
        Perform a 2d morphological erosion with a specific kernel.
        <BLANKLINE>
        The main kernel is:
            · ● ·
            · 🕀 ·
            ● ● ●
        <BLANKLINE>
        With the naive convolution, there is 4 comparisons per pixel.
        With this decomposition, there is 3.44 comparisons per pixel in average.
        <BLANKLINE>
        A stide (3, 3) morphology is performed with each of these kernels:
        <BLANKLINE>
         0 |  1  | 2 |3| 4 | 5 |  6  |   7   | 8 |  9  |  10   | 11  | 12  |  13
        🕂 ·|🕂 · ●|· ●|●|🕂 ·|· 🕂|🕂 · ·|· · ● ·|· 🕀|🕂 ● ·|🕂 · · ·|· 🕂 ·|🕂 · ·|🕂 · · ·
        · ·|· · ●|🕂 ●|🕀|● ●|● ·|· · ●|🕂 · · ·|· ●|· ● ·|· · · ·|· ● ·|· ● ·|· · ● ·
        ● ●|     |   | |   |   |     |· ● · ●|● ·|· · ●|· ● ● ●|· · ·|· · ·|· · ● ·
           |     |   | |   |   |     |       |   |     |       |● · ●|● · ●|· ● ● ●
        Then, there are merged in 9 clusters:
        cluster 0: ker 3 > (0, 0) and ker 4 > (0, 0) and ker 5 > (0, 0)
        cluster 1: ker 2 > (0, 0) and ker 4 > (0, 0) and ker 6 > (0, 0)
        cluster 2: ker 1 > (0, 0) and ker 7 > (0, 0)
        cluster 3: ker 0 > (0, 0) and ker 8 > (0, 0)
        cluster 4: ker 0 > (0, 0) and ker 9 > (0, 0)
        cluster 5: ker 1 > (0, 0) and ker 10 > (0, 0)
        cluster 6: ker 3 > (1, 0) and ker 11 > (0, 0)
        cluster 7: ker 2 > (1, 0) and ker 12 > (0, 0)
        cluster 8: ker 13 > (0, 0)
        >>>
        """
        # main info
        title = f"Perform a {self._ndim}d morphological erosion with a specific kernel.\n"
        kernel = f"The main kernel is:\n    {'\n    '.join(str(self._kernel).split('\n'))}\n"
        comp = (
            sum(len(k)-1 for k in self._kernels)
            + sum(len(m)-1 for m in self._merge.values())
        ) / self._kernel.struct_elem.size
        stats = (
            f"With the naive convolution, there is {len(self._kernel)-1} comparisons per pixel.\n"
            f"With this decomposition, there is {comp:.2f} comparisons per pixel in average.\n"
        )
        # decomposition
        kernels = [str(k).split("\n") for k in self._kernels]  # list of lines
        kernels = [[f"{i:^{len(k[0])}}", *k] for i, k in enumerate(kernels)]  # add header
        size = max(len(k) for k in kernels)
        kernels = [(k+[""]*size)[:size] for k in kernels]
        kernels = [[f"{l:<{len(k[0])}}" for l in k] for k in kernels]  # pad lines same length
        kernels = "\n".join("|".join(full_line) for full_line in zip(*kernels))
        kernels = "\n".join(l.rstrip() for l in kernels.split("\n"))  # remove leading spaces
        # merge
        merge = "\n".join(
            f"cluster {i}: {' and '.join(f'ker {j} > {mod}' for j, mod in sorted(self._merge[i]))}"
            for i in sorted(self._merge)
        )
        decomposition = (
            f"A stide {self._kernel.shape} morphology is performed with each of these kernels:\n"
            "\n"
            f"{kernels}"
            "\n"
            f"Then, there are merged in {len(self._merge)} clusters:\n"
            f"{merge}"
        )
        return title + "\n" + kernel + "\n" + stats + "\n" + decomposition

    def draw_func_elementary_loop(self) -> str:
        """Return the source code of iterative call to first level decomposition.

        Examples
        --------
        >>> from morphomath.decomposition import full_decomposition
        >>> from morphomath.kernel import Kernel
        >>> from morphomath.printer import Printer
        >>> kernel = Kernel([[0, 1, 0], [0, 1, 0], [1, 1, 1]])
        >>> kernels, merge = full_decomposition(kernel)
        >>> printer = Printer(kernel, kernels, merge)
        >>> print(printer.draw_func_elementary_loop())  # doctest: +ELLIPSIS
        """
        decomp_range = [
            (min(d), max(d)) for d in zip(*(p for k in self._kernels for p in k.points))
        ]
        code = (
            "int elementary_loop(NPY** dst, PyArrayObject* src, long int threads) {\n"
            f"  *dst = malloc(sizeof(NPY) * PyArray_SIZE(src) * {len(self._kernels)});\n"
            "  if (*dst == NULL) {\n"
            "    return EXIT_FAILURE;\n"
            "  }\n"
            "  return EXIT_SUCCESS;\n"
            "}"
        )
        return code

    def draw_func_elementary_patch(self) -> str:
        """Return the source code of the first atomic decomposition level.

        Examples
        --------
        >>> from morphomath.decomposition import full_decomposition
        >>> from morphomath.kernel import Kernel
        >>> from morphomath.printer import Printer
        >>> kernel = Kernel([[0, 1, 0], [0, 1, 0], [1, 1, 1]])
        >>> kernels, merge = full_decomposition(kernel)
        >>> printer = Printer(kernel, kernels, merge)
        >>> print(printer.draw_func_elementary_patch())  # doctest: +ELLIPSIS
        void elementary_patch(NPT dst[14], PyArrayObject* src, npy_intp a0, npy_intp a1) {
          dst[3] = OP(*(NPT *)PyArray_GETPTR2(src, a0, a1), *(NPT *)PyArray_GETPTR2(src, a0+8, a1));
          dst[8] = OP(*(NPT *)PyArray_GETPTR2(src, a0, a1), *(NPT *)PyArray_GETPTR2(src, a0+4, a1));
          ...
          dst[7] = OP(dst[7], *(NPT *)PyArray_GETPTR2(src, a0+8, a1+8));
          dst[8] = OP(dst[8], *(NPT *)PyArray_GETPTR2(src, a0+8, a1+8));
          dst[9] = OP(dst[9], *(NPT *)PyArray_GETPTR2(src, a0+8, a1+8));
          dst[10] = OP(dst[10], *(NPT *)PyArray_GETPTR2(src, a0+8, a1+8));
          dst[13] = OP(dst[13], *(NPT *)PyArray_GETPTR2(src, a0+8, a1+8));
        }
        >>>
        """
        # data organization to minimize the cache access
        ops: list[tuple[tuple[int, ...], int]] = []
        for i, kernel in enumerate(self._kernels):
            ops.extend([(p, i) for p in kernel.points])
        ops.sort()

        # header
        args = [
            f"NPT dst[{len(self._kernels)}]",
            "PyArrayObject* src",
            *(f'npy_intp a{i}' for i in range(self._ndim))
        ]
        code = f"void elementary_patch({', '.join(args)}) {{\n"

        # content
        is_init: list[bool] = [False for _ in range(len(self._kernels))]
        while ops:
            idx_0, i_0 = ops.pop(0)
            if is_init[i_0]:
                code += f"  dst[{i_0}] = OP(dst[{i_0}], {_getptr('src', idx_0)});\n"
                continue
            is_init[i_0] = True
            try:
                next_point_idx = next(iter(i for i, (_, i_1) in enumerate(ops) if i_1 == i_0))
            except StopIteration:
                code += f"  dst[{i_0}] = {_getptr('src', idx_0)};\n"
            else:
                idx_1, _ = ops.pop(next_point_idx)
                code += f"  dst[{i_0}] = OP({_getptr('src', idx_0)}, {_getptr('src', idx_1)});\n"

        # end
        code += "}"
        return code

    def __str__(self) -> str:
        """Return the completed C module template of this function."""
        # load template
        with open(get_project_root() / "template.c", "r", encoding="utf-8") as file:
            code = file.read()

        # fill template
        code = (
            code
            .replace("{numpy_type}", "npy_float")
            .replace("{operator}", "MIN")
            .replace("{description}", self.draw_description())
            .replace("{func_elementary_decomposition}", self.draw_func_elementary_patch())
            .replace("{func_elementary_loop}", self.draw_func_elementary_loop())
        )

        return code



def draw_patches(stride: tuple[int, ...], field: tuple[tuple[int, int], ...]) -> str:
    """Draw the C function that compute all valid morphological patchs.

    Parameters
    ----------
    stride : tuple[int, ...]
        The size of the blocs.
    field : tuple[tuple[int, int], ...]
        The min and max point of all the kernels for each componant.

    Returns
    -------
    code : str
        The source code of the function that vectorize morpho_patch.

    Examples
    --------
    >>> from morphomath.printer import draw_patches
    >>> print(draw_patches((3, 2), ((-1, 2), (0, 6))))
    void morpho_valid(npy_float* dst, PyArrayObject* src, long int threads ) {
      #pragma omp parallel for schedule(static) collapse(2) num_threads(threads)
      for ( npy_intp a0 = 0; a0 <= (PyArray_DIM(src, 0)-2)/3; ++a0 ) {
        for ( npy_intp a1 = 0; a1 <= (PyArray_DIM(src, 1)-6)/2; ++a1 ) {
          morpho_patch(npy_float dst[3], src, 3*a0+1, 2*a1+0);
        }
      }
    }
    >>>
    """
    assert isinstance(stride, tuple), stride.__class__.__name__
    assert isinstance(field, tuple), field.__class__.__name__
    assert len(stride) == len(field), (stride, field)
    assert all(isinstance(s, int) for s in stride), stride
    assert all(isinstance(f, tuple) for f in field), field
    assert all(len(f) == 2 for f in field), field
    assert all(isinstance(b, int) for f in field for b in f), field
    assert all(min_ < max_ for min_, max_ in field), field

    # header
    code = (
        "void morpho_valid("
        "npy_float* dst, "
        "PyArrayObject* src, "
        "long int threads "
        ") {\n"
    )

    # loops
    #pragma omp parallel for schedule(static) collapse(2) num_threads(threads)
    code += f"  #pragma omp parallel for schedule(static) collapse({len(stride)}) num_threads(threads)\n"
    for i, (stride_, (min_, max_)) in enumerate(zip(stride, field)):
        code += (
            f"{'  '*(i+1)}"
            f"for ( npy_intp a{i} = {min(0, -min_)}; "
            f"a{i} <= (PyArray_DIM(src, {i})-{max_})/{stride_}; ++a{i} ) {{\n"
        )
    args = [
        "npy_float dst[3]",  # TODO: bon acces
        "src",
        *(f"{s}*a{i}+{-min_}" for i, (s, (min_, _)) in enumerate(zip(stride, field)))
    ]
    code += f"{'  '*(len(stride)+1)}morpho_patch({', '.join(args)});\n"
    for i in range(len(stride), 0, -1):
        code += f"{'  '*i}}}\n"

    # end
    code += "}"
    return code


def _getptr(symb: str, idx: tuple[int, ...]) -> str:
    """C numpy array assignation."""
    pos = [f"a{i}+{s}".replace("+-", "-").replace("+0", "") for i, s in enumerate(idx)]
    if len(idx) <= 4:  # optional use macro to make the code more readable
        return f"*(NPT *)PyArray_GETPTR{len(idx)}({symb}, {', '.join(pos)})"
    ptr = " + ".join(
        f"({p})*PyArray_STRIDES({symb})[{i}]" for i, p in enumerate(pos)
    )
    return f"*(NPT *)(PyArray_BYTES({symb}) + {ptr})"
