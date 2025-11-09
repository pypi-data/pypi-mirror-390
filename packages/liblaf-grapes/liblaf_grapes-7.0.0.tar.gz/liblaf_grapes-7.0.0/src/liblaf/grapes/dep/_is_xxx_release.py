import functools
import importlib.metadata
import os
from importlib.metadata import Distribution, PackagePath
from pathlib import Path

import attrs
import cachetools
import packaging.version
from packaging.version import InvalidVersion, Version

from liblaf.grapes.functools import cachedmethod


@attrs.define(slots=False)
class FilesIndex:
    _distributions: list[Distribution] = attrs.field(factory=list)

    def add(self, distributuion: Distribution) -> None:
        self._distributions.append(distributuion)

    def has(self, file: str | os.PathLike[str]) -> bool:
        file = Path(file).resolve()
        return self._has(str(file))

    @cachedmethod(factory=lambda: cachetools.LRUCache(maxsize=1024))
    def _has(self, file: str) -> bool:
        if file in self._files:
            return True
        file: Path = Path(file)
        return any(file.is_relative_to(prefix) for prefix in self._pth)

    @functools.cached_property
    def _files(self) -> set[str]:
        self._init()
        return self._files

    @functools.cached_property
    def _pth(self) -> set[str]:
        self._init()
        return self._pth

    def _init(self) -> None:
        files: set[str] = set()
        pth: set[str] = set()
        for distribution in self._distributions:
            dist_files: list[PackagePath] | None = distribution.files
            if dist_files is None:
                continue
            for dist_file in dist_files:
                if dist_file.suffix == ".pth":
                    for line in dist_file.read_text().splitlines():
                        folder = Path(line)
                        if folder.is_dir():
                            pth.add(line)
                else:
                    files.add(str(dist_file.locate()))
        self._files = files
        self._pth = pth


@attrs.define
class ReleaseTypeIndex:
    def is_dev(
        self, file: str | os.PathLike[str] | None = None, name: str | None = None
    ) -> bool:
        if name is not None and name == "__main__":
            return True
        return file is not None and self._dev_index.has(file)

    def is_prerelease(
        self, file: str | os.PathLike[str] | None = None, name: str | None = None
    ) -> bool | None:
        if name is not None and name == "__main__":
            return True
        return file is not None and self._pre_index.has(file)

    @functools.cached_property
    def _dev_index(self) -> FilesIndex:
        self._init()
        return self._dev_index

    @functools.cached_property
    def _pre_index(self) -> FilesIndex:
        self._init()
        return self._pre_index

    def _init(self) -> None:
        dev_index: FilesIndex = FilesIndex()
        pre_index: FilesIndex = FilesIndex()
        for distribution in importlib.metadata.distributions():
            try:
                version: Version = packaging.version.parse(distribution.version)
            except InvalidVersion:
                continue
            if version.is_devrelease:
                dev_index.add(distribution)
            if version.is_prerelease:
                pre_index.add(distribution)
        self._dev_index = dev_index
        self._pre_index = pre_index


def is_dev_release(
    file: str | os.PathLike[str] | None = None, name: str | None = None
) -> bool:
    return _release_type_index.is_dev(file=file, name=name)


def is_pre_release(
    file: str | os.PathLike[str] | None = None, name: str | None = None
) -> bool | None:
    return _release_type_index.is_prerelease(file=file, name=name)


_release_type_index = ReleaseTypeIndex()
