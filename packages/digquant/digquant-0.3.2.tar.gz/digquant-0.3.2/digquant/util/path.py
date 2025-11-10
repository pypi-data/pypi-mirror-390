import pathlib as p

from ..type import Path


def mkdir(*parts: Path, parent: bool = False) -> p.Path:
    path = p.Path(*parts)
    (path.parent if parent else path).mkdir(parents=True, exist_ok=True)
    return path
