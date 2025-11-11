"""Executes all the tests via the ``pytest`` module."""

try:
    import pytest
except ImportError as err:
    msg = "pytest paquage required (uv pip install morphomath[test])"
    raise ImportError(msg) from err

from morphomath.utils import get_project_root


def run_tests(
    *,
    debug: bool = False,
    skip_coding_style: bool = False,
    skip_slow: bool = False,
) -> int:
    """Perform all unit tests."""
    root = get_project_root()
    debug_options = ["--full-trace"] if debug else []

    # code quality check
    if not skip_coding_style:
        print("Checking if the coding style respects the PEP...")
        path = str(root / "testing" / "coding_style.py")
        if (
            code := pytest.main([
                *debug_options,
                "--verbose", "--exitfirst", "--capture=no", "--tb=no", "-rN", path,  # no repport
            ])
        ):
            return int(code)

    # classical tests
    print("Runing all the little unit tests...")
    paths = sorted(
        map(
            str,
            (
                set(root.rglob("*.py"))
                - {root / "testing" / "install.py", root / "testing" / "coding_style.py"}
            ),
        ),
    )
    if (code := pytest.main([*debug_options, "-m", "not slow", "--doctest-modules", *paths])):
        return int(code)

    # slow tests
    if not skip_slow:
        print("Runing the slow unit tests...")
        if (code := pytest.main([*debug_options, "-m", "slow", "--verbose", *paths])):
            return int(code)
    return 0
