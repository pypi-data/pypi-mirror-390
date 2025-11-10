#!/usr/bin/env python3

"""Perform verifications on the decomposition."""


from morphomath.kernel import Kernel
from morphomath.decomposition import initialisation, all_steps_decomposition, one_step_decomposition
from morphomath.decomposition import TYPE_VEC, TYPE_TOROID_POINT


def check_all_steps_decomposition(kernel: Kernel):
    """Verify in the decompositions are corrects."""
    lattice = initialisation(kernel)
    ref_kernels = {
        i: Kernel.from_points([r + s*q for q, r, s in zip(*tp, kernel.shape)] for tp in tps)
        for i, tps in enumerate(lattice)
    }
    for sub_kernels, merge_table in all_steps_decomposition(lattice):
        reconstructed_kernels = recompose(sub_kernels, merge_table, kernel.shape)
        assert ref_kernels == reconstructed_kernels


def recompose(
    sub_kernels: list[set[TYPE_TOROID_POINT]],
    merge_table: dict[int, set[tuple[int, TYPE_VEC]]],
    shape: TYPE_VEC,
) -> dict[int, Kernel]:
    """Merge the toroid points to rebuild kernels."""
    reconstructed_kernels: dict[int, Kernel] = {}
    for i, fusion in merge_table.items():
        points: set[TYPE_VEC] = set()
        for ker_idx, mod in fusion:
            points |= {
                tuple(r + s*(q+m) for q, r, m, s in zip(*tp, mod, shape))
                for tp in sub_kernels[ker_idx]
            }
        reconstructed_kernels[i] = Kernel.from_points(points)
    return reconstructed_kernels


def test_decomposition_1d_1():
    """Test the decomposition."""
    check_all_steps_decomposition(Kernel([1]))


def test_decomposition_1d_11():
    """Test the decomposition."""
    check_all_steps_decomposition(Kernel([1, 1]))


def test_decomposition_1d_111():
    """Test the decomposition."""
    check_all_steps_decomposition(Kernel([1, 1, 1]))


def test_decomposition_1d_1111():
    """Test the decomposition."""
    check_all_steps_decomposition(Kernel([1, 1, 1, 1]))


def test_decomposition_2d_1():
    """Test the decomposition."""
    check_all_steps_decomposition(Kernel([[1]]))


def test_decomposition_2d_11_11():
    """Test the decomposition."""
    check_all_steps_decomposition(Kernel([[1, 1], [1, 1]]))


def test_decomposition_2d_010_010_111():
    """Test the decomposition."""
    check_all_steps_decomposition(Kernel([[0, 1, 0], [0, 1, 0], [1, 1, 1]]))

