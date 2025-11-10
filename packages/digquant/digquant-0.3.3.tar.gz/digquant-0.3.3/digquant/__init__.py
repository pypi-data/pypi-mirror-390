__all__ = ["print_requirements"]


import sys as _sys


def print_requirements(simplify: bool = True) -> None:
    from .util.dependency import DependencyTreeResolver

    dtr = DependencyTreeResolver()
    print(f"# {_sys.version} @ {_sys.platform}")
    print(dtr.requirements(simplify))
