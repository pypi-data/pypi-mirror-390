import re

from ul_py_tool.utils.pipfile import Pipfile


def test_input_lines() -> None:
    Pipfile({})


def test_find_version() -> None:
    name = 'api-utils'
    page = (
        '<a'
        'href="https://gitlab.neroelectronics.by/api/v4/projects/996/packages/pypi/files/'
        '63bc8e0f46fd2c4dc27ee28e2059810d816ead14636ac0887682a81b4d91c83e/api-utils-1.6.9.tar.gz#sha256=63bc8e0f46fd2c4dc27ee28e2059810d816ead14636ac0887682a81b4d91c83e"'
        'data-requires-python="">api-utils-1.6.9.tar.gz</a>'
    )
    assert re.compile(rf'{name}-([^<]+?)\.tar\.gz').findall(page) == ['1.6.9', '1.6.9']
