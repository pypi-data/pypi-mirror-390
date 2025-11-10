import io
import typing as t

if t.TYPE_CHECKING:
    import typing_extensions as te


KINDS = ["bz2", "gzip", "lzma", "zstd"]


class Compression:
    def __init__(self, kind: str) -> None:
        assert kind in KINDS

        self._kind = kind

    @classmethod
    def fromDefault(cls) -> "te.Self":
        return cls("zstd")

    def open(self, *args, **kwargs) -> io.BufferedIOBase:
        return getattr(self, f"_open_{self._kind}")(*args, **kwargs)

    def _open_bz2(self, *args, **kwargs) -> io.BufferedIOBase:
        import bz2

        return bz2.open(*args, **kwargs)

    def _open_gzip(self, *args, **kwargs) -> io.BufferedIOBase:
        import gzip

        return gzip.open(*args, **kwargs)

    def _open_lzma(self, *args, **kwargs) -> io.BufferedIOBase:
        import lzma

        return lzma.open(*args, **kwargs)

    def _open_zstd(self, *args, **kwargs) -> io.BufferedIOBase:
        import zstandard

        return zstandard.open(*args, **kwargs)
