import contextlib as ctx
import functools as f
import io
import sys
import typing as t

from importlib import metadata

from packaging.utils import canonicalize_name

if t.TYPE_CHECKING:
    from pipdeptree._models import PackageDAG


Import2Dist = t.Dict[str, metadata.Distribution]
Package2Dist = t.Dict[str, metadata.Distribution]


class DependencyTreeResolver:
    def __init__(self) -> None:
        pass

    @f.cached_property
    def import2dist(self) -> Import2Dist:
        ans = {}
        for dist in metadata.distributions():
            text = dist.read_text("top_level.txt") or self._get_package_name(dist)
            lines = filter(bool, map(str.strip, text.splitlines()))
            for line in lines:
                ans[canonicalize_name(line)] = dist
        return ans

    def package2dist(self) -> Package2Dist:
        names = {
            canonicalize_name(key.split(".", maxsplit=1)[0])
            for key in sys.modules.keys()
            if not key.startswith("_")
        }
        return {
            canonicalize_name(self._get_package_name(dist)): dist
            for name, dist in self.import2dist.items()
            if name in names
        }

    def requirements(self, simplify: bool = True) -> str:
        if simplify:
            tree = self._get_package_dag(*self.package2dist().keys())
            ignores = {value.key for values in tree.values() for value in values}

        else:
            ignores = set()
        return "\n".join(
            sorted(
                f"{package}=={dist.version}"
                for package, dist in self.package2dist().items()
                if package not in ignores
            )
        )

    def _get_package_name(self, dist: metadata.Distribution) -> str:
        return dist.metadata["Name"]

    def _get_package_dag(self, *packages: str) -> "PackageDAG":
        from pipdeptree._discovery import get_installed_distributions
        from pipdeptree._models import PackageDAG

        with io.StringIO() as target, ctx.redirect_stderr(target):
            pkgs = get_installed_distributions(interpreter=sys.executable)
            tree = PackageDAG.from_pkgs(pkgs)
            return tree.filter_nodes(list(packages), None)
