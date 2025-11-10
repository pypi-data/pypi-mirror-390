import pathlib as p
import typing as t


T = t.TypeVar("T")

Gen = t.Generator[T, None, None]

Path = t.Union[str, p.Path]
Strings = t.List[str]
