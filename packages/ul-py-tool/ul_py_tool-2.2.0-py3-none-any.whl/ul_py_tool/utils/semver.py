import re
from dataclasses import dataclass
from typing import Optional, Union

VERSION_RE = re.compile(r'^(==|>|<|<=|>=|~=|\^=)?\s*(\d+)\.(\d+)(?:\.(\d+))?(.*?)$')


@dataclass
class SemVer:
    major: int
    minor: int
    patch: int | None = None
    variant: str = ''

    def __lt__(self, other: Union[str, 'SemVer']) -> bool:
        other_ver = SemVer.from_string(other) if isinstance(other, str) else other
        if other_ver is None:
            raise ValueError(f'invalid value {other}')
        if self.major > other_ver.major:
            return False
        if self.major < other_ver.major:
            return True
        if self.minor > other_ver.minor:
            return False
        if self.minor < other_ver.minor:
            return True
        if self.patch is None:
            if other_ver.patch is not None:
                return True
        else:
            if other_ver.patch is None:
                return False
        if other_ver.patch is not None and self.patch is not None:
            if self.patch > other_ver.patch:
                return False
            if self.patch < other_ver.patch:
                return True
        if self.variant and not other_ver.variant:
            return False
        if other_ver.variant and not self.variant:
            return True
        return False

    def __gt__(self, other: Union[str, 'SemVer']) -> bool:
        other_ver = SemVer.from_string(other) if isinstance(other, str) else other
        if other_ver is None:
            raise ValueError(f'invalid value {other}')
        return other_ver < self

    def __le__(self, other: Union[str, 'SemVer']) -> bool:
        other_ver = SemVer.from_string(other) if isinstance(other, str) else other
        if other_ver is None:
            raise ValueError(f'invalid value {other}')
        return self == other or self < other

    def __ge__(self, other: Union[str, 'SemVer']) -> bool:
        other_ver = SemVer.from_string(other) if isinstance(other, str) else other
        if other_ver is None:
            raise ValueError(f'invalid value {other}')
        return other_ver == self or other_ver < self

    @staticmethod
    def from_string(version_string: str) -> Optional['SemVer']:
        version_string = version_string.strip()
        m = VERSION_RE.match(version_string)
        if m is None:
            return None
        _1, ma, mi, pa, va = m.groups()
        return SemVer(
            major=int(ma),
            minor=int(mi),
            patch=int(pa) if pa is not None else None,
            variant=va,
        )

    @staticmethod
    def from_string_wop(version_string: str) ->  tuple[str, 'SemVer'] | None:
        version_string = version_string.strip()
        m = VERSION_RE.match(version_string)
        if m is None:
            return None
        op, ma, mi, pa, va = m.groups()
        return op, SemVer(
            major=int(ma),
            minor=int(mi),
            patch=int(pa) if pa is not None else None,
            variant=va,
        )

    def __str__(self) -> str:
        return f'{self.major}.{self.minor}{f".{self.patch}" if self.patch is not None else ""}{self.variant}'


def test_semver() -> None:
    assert SemVer.from_string('1.3.2') == SemVer(1, 3, 2)
    assert SemVer.from_string('1.3') == SemVer(1, 3)
    assert SemVer.from_string('1.3-some') == SemVer(1, 3, variant='-some')
    assert str(SemVer(1, 3, 2)) == '1.3.2'
    assert str(SemVer(1, 3)) == '1.3'
    assert str(SemVer(1, 3)) != '1.4'
    assert str(SemVer(1, 3, variant='-some')) == '1.3-some'

    assert SemVer(1, 3, 2) > SemVer(1, 3, 1)
    assert SemVer(1, 3, 2) > SemVer(1, 3, 0)
    assert SemVer(1, 3, 2) > SemVer(1, 2, 0)
    assert SemVer(1, 3, 2) > SemVer(1, 2, 10)
    assert SemVer(1, 3, 2) > SemVer(0, 10, 10)
    assert SemVer(1, 3, 2) > SemVer(0, 3, 3)
    assert SemVer(1, 3, 2) > SemVer(0, 3)
    assert SemVer(1, 3, 2) > SemVer(1, 3)

    assert SemVer(1, 3, 2) >= SemVer(1, 3, 1)
    assert SemVer(1, 3, 2) >= SemVer(1, 3, 0)
    assert SemVer(1, 3, 2) >= SemVer(1, 2, 0)
    assert SemVer(1, 3, 2) >= SemVer(1, 2, 10)
    assert SemVer(1, 3, 2) >= SemVer(0, 10, 10)
    assert SemVer(1, 3, 2) >= SemVer(0, 3, 3)
    assert SemVer(1, 3, 2) >= SemVer(0, 3)
    assert SemVer(1, 3, 2) >= SemVer(1, 3)
    assert SemVer(1, 3, 2) >= SemVer(1, 3, 2)

    assert SemVer(1, 3, 1) < SemVer(1, 3, 2)
    assert SemVer(1, 3, 0) < SemVer(1, 3, 2)
    assert SemVer(1, 2, 0) < SemVer(1, 3, 2)
    assert SemVer(1, 2, 10) < SemVer(1, 3, 2)
    assert SemVer(0, 10, 10) < SemVer(1, 3, 2)
    assert SemVer(0, 3, 3) < SemVer(1, 3, 2)
    assert SemVer(0, 3) < SemVer(1, 3, 2)
    assert SemVer(1, 3) < SemVer(1, 3, 2)

    assert SemVer(1, 3, 1) < '1.3.2'
    assert SemVer(1, 3, 0) < '1.3.2'
    assert SemVer(1, 2, 0) < '1.3.2'
    assert SemVer(1, 2, 10) < '1.3.2'
    assert SemVer(0, 10, 10) < '1.3.2'
    assert SemVer(0, 3, 3) < '1.3.2'
    assert SemVer(0, 3) < '1.3.2'
    assert SemVer(1, 3) < '1.3.2'
    assert not (SemVer(1, 3) < SemVer(1, 3))

    assert SemVer(1, 3, 1) <= '1.3.2'
    assert SemVer(1, 3, 0) <= '1.3.2'
    assert SemVer(1, 2, 0) <= '1.3.2'
    assert SemVer(1, 2, 10) <= '1.3.2'
    assert SemVer(0, 10, 10) <= '1.3.2'
    assert SemVer(0, 3, 3) <= '1.3.2'
    assert SemVer(0, 3) <= '1.3.2'
    assert SemVer(1, 3) <= '1.3.2'

    assert SemVer(1, 3, 1) == SemVer(1, 3, 1)
    assert SemVer(1, 3, 0) == SemVer(1, 3, 0)
    assert SemVer(1, 2, 0) == SemVer(1, 2, 0)
    assert SemVer(1, 2, 10) == SemVer(1, 2, 10)
    assert SemVer(0, 10, 10) == SemVer(0, 10, 10)
    assert SemVer(0, 3, 3) == SemVer(0, 3, 3)
