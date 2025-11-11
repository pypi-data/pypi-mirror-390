import os
import re
import subprocess
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Mapping

import requests
import tomli

from ul_py_tool.utils.semver import SemVer


@dataclass
class PipfileSource:
    url: str
    name: str
    verify_ssl: bool


@dataclass
class PipfileScript:
    name: str
    command: str


class PipfilePackage:

    def __init__(
        self,
        name: str,
        version: str,
        version_operator: str,
        extras: list[str],
        semver: SemVer | None,
        index: str | None,
        path: str | None,
        source: PipfileSource | None,
        is_dev: bool,
    ):
        assert isinstance(name, str), f'package name must be str. "{type(name).__name__}" was given'
        assert isinstance(version, str), f'package "{name}" version must be str. "{type(version).__name__}" was given'
        assert isinstance(version_operator, str), f'package "{name}" version_operator must be str. "{type(version_operator).__name__}" was given'
        assert isinstance(extras, list), f'package "{name}" extras must be list. "{type(extras).__name__}" was given'
        assert semver is None or isinstance(semver, SemVer), f'package "{name}" semver must be SemVer. "{type(semver).__name__}" was given'
        assert index is None or isinstance(index, str), f'package "{name}" index must be str. "{type(index).__name__}" was given'
        assert source is None or isinstance(source, PipfileSource), f'package "{name}" source must be PipfileSource. "{type(source).__name__}" was given'
        assert path is None or isinstance(path, str), f'package "{name}" path must be str. "{type(path).__name__}" was given'
        assert isinstance(is_dev, bool), f'package "{name}" is_dev must be bool. "{type(is_dev).__name__}" was given'

        self.name = name
        self.version = version
        self.version_operator = version_operator
        self.extras = extras
        self.semver = semver
        self.index = index
        self.path = path
        self.source = source
        self.is_dev = is_dev

    @cached_property
    def pip_representation(self) -> str:
        extras = ','.join(self.extras)
        return f'{self.name}{f"[{extras}]" if extras else ""}{self.version}'

    @cached_property
    def clean_version(self) -> str:
        return self.version[len(self.version_operator):]

    @cached_property
    def all_versions(self) -> list[SemVer]:
        assert self.source is not None
        try:
            page = requests.get(f'{self.source.url.rstrip("/")}/{self.name}').text
        except Exception:  # noqa: B902
            assert self.semver is not None
            return [self.semver]

        res = []
        for v in set(re.compile(rf'{self.name}-([^<]+?)\.tar\.gz').findall(page)):
            res_v = SemVer.from_string(v)
            if res_v is not None:
                res.append(res_v)
        return sorted(res)

    @cached_property
    def is_valid(self) -> bool:
        return self.semver in self.all_versions

    @cached_property
    def available_versions(self) -> list[SemVer]:
        if self.semver is None:
            raise TypeError('semver is None')
        return [v for v in self.all_versions if v > self.semver]


class Pipfile:

    @staticmethod
    def load(file: str) -> 'Pipfile':
        with open(file, 'rt') as f:
            return Pipfile(tomli.loads(f.read()))

    @staticmethod
    def freeze() -> dict[str, PipfilePackage]:
        freeze_result = subprocess.run('pip freeze', shell=True, check=False, cwd=os.getcwd(), capture_output=True).stdout.decode()
        res = dict()
        for ps in freeze_result.split('\n'):
            psl = ps.strip().split('==')
            if len(psl) == 2:
                name, version = psl

                ver = SemVer.from_string_wop(version)

                name = name.strip().lower()

                res[name] = PipfilePackage(
                    name=name,
                    version=version,
                    version_operator='' if ver is None else ver[0] or '',
                    extras=[],
                    semver=None if ver is None else ver[1],
                    index='',
                    path=None,
                    source=None,
                    is_dev=False,
                )
        return res

    @staticmethod
    def from_string(content: str) -> 'Pipfile':
        return Pipfile(tomli.loads(content))

    def __init__(self, content: dict[str, Any]) -> None:
        assert isinstance(content, dict), f'invalid content of pipfile. content must be dict. "{type(content).__name__}" was given'
        self._cntnt = content

        # load all
        self.sources_index
        self.all_packages

    @cached_property
    def python_version(self) -> SemVer | None:
        version = self._cntnt.get('requires', dict()).get('python_version', None)
        return SemVer.from_string(version)

    @cached_property
    def scripts(self) -> dict[str, PipfileScript]:
        scr = self._cntnt.get('scripts', dict())
        assert isinstance(scr, dict), f'scripts must be dict. "{type(scr).__name__}" was given'
        res = dict()
        for name, command in scr.items():
            name = name.strip()
            res[name] = PipfileScript(
                name=name,
                command=command.strip(),
            )
        return res

    def _parse_pack(self, segment: str) -> dict[str, PipfilePackage]:
        packs = dict(self._cntnt.get(segment, dict()))
        assert isinstance(packs, dict), f'packages must be dict. "{type(packs).__name__}" was given'

        res = dict()
        for name, params in packs.items():
            name = name.strip()

            index = self.default_source.name
            path = None
            extras: list[str] = []
            if isinstance(params, dict):
                version = params['version']
                extras = params.get('extras', [])
                path = params.get('path', None)
                index = params.get('index', index).strip()
            elif isinstance(params, str):
                version = params
            else:
                raise TypeError(f'params of package "{name}" version has invalid type. must be str or dict. {type(params).__name__} was given')

            ver = SemVer.from_string_wop(version)

            if index not in self.sources_index:
                raise ValueError(f'index "{index}" not in sources')

            name = name.strip().lower()

            if name in res:
                raise KeyError(f'package "{name}" was duplicated in packages/dev-packages')

            res[name] = PipfilePackage(
                name=name,
                version=version,
                version_operator='' if ver is None else ver[0],
                extras=extras,
                semver=None if ver is None else ver[1],
                index=index,
                path=path,
                source=self.sources_index[index],
                is_dev=segment == 'dev-packages',
            )
        return res

    @cached_property
    def all_packages(self) -> Mapping[str, PipfilePackage]:
        return {
            **self._parse_pack('packages'),
            **self._parse_pack('dev-packages'),
        }

    @cached_property
    def packages(self) -> Mapping[str, PipfilePackage]:
        res = {}
        for pack in self.all_packages.values():
            if not pack.is_dev:
                res[pack.name] = pack
        return res

    @cached_property
    def dev_packages(self) -> Mapping[str, PipfilePackage]:
        res = {}
        for pack in self.all_packages.values():
            if pack.is_dev:
                res[pack.name] = pack
        return res

    @cached_property
    def default_source(self) -> PipfileSource:
        return self.sources[0]

    @cached_property
    def sources(self) -> list[PipfileSource]:
        res = []
        for source in self._cntnt.get('source', []):
            res.append(PipfileSource(
                name=source['name'].strip(),
                url=source['url'].strip(),
                verify_ssl=bool(source['verify_ssl']),
            ))
        return res

    @cached_property
    def sources_index(self) -> dict[str, PipfileSource]:
        res = dict()
        for source in self.sources:
            if source.name in res:
                raise KeyError(f'{source.name} has duplicate')
            res[source.name] = source
        return res


TEST_PIPIFILE = """
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[[source]]
name = "nero_gitlab"
verify_ssl = false
url = "https://__token__:KSnT_2NZ_cstDqvLmg-k@gitlab.neroelectronics.by/api/v4/projects/996/packages/pypi/simple"

[packages]
unipipeline = "==1.8.1"
api-utils = {version = "==4.4.1", index = "nero_gitlab"}
ul_py_tool = {version = "==1.11.3", index = "nero_gitlab"}

[dev-packages]
db-utils = {version = "==2.1.0", index = "nero_gitlab"}

[requires]
python_version = "3.10"

[scripts]
prepare = "python3 setup.py sdist bdist_wheel"
lint = "ulpytool lint --py-files src/**/*.py src/*.py bin/**/*.py bin/*.py --py-files-ignore **/migrations/**/*.py"
test = "ulpytool test --files **/test_*.py"
"""


def test_pipfile() -> None:
    ppfile = Pipfile.from_string(TEST_PIPIFILE)

    assert len(ppfile.sources) == 2
    assert len(ppfile.all_packages) == 4
    assert len(ppfile.dev_packages) == 1
    assert len(ppfile.packages) == 3
    assert len(ppfile.scripts) == 3

    assert len(ppfile.all_packages['db-utils'].all_versions) > 0
    assert ppfile.all_packages['db-utils'].is_valid
    assert len(ppfile.all_packages['db-utils'].available_versions) > 0
