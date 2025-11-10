import io
import typing as t
import warnings

if t.TYPE_CHECKING:
    import typing_extensions as te


KINDS = ["default", "bz2", "gzip", "lzma", "zstd"]


class Compression:
    def __init__(self, kind: str = "default") -> None:
        assert kind in KINDS

        self._kind = kind

    @classmethod
    def fromDefault(cls) -> "te.Self":
        return cls("zstd")

    def open(self, *args, **kwargs) -> io.BufferedIOBase:
        return getattr(self, f"_open_{self._kind}")(*args, **kwargs)

    def _open_default(self, *args, **kwargs) -> io.BufferedIOBase:
        return open(*args, **kwargs)

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
        try:
            import zstandard
        except ModuleNotFoundError:
            warnings.warn(
                "Module `zstandard` not available. Install with: `pip install digquant[zstd]`"
            )
            return self._open_default(*args, **kwargs)
        else:
            return zstandard.open(*args, **kwargs)
