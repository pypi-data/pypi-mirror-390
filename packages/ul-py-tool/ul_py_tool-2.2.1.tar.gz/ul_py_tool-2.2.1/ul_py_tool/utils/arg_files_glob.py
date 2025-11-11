import argparse
import glob
import os
from typing import Callable

from ul_py_tool.utils.write_stdout import write_stdout


def arg_file_info(file: str, *, rel_path: bool = True, ide_col_suf: bool = True, line: int = 0, col: int | None = None) -> str:
    suf = f':{line}{f":{col}" if col is not None else ""}' if ide_col_suf else ''
    return f'./{os.path.relpath(file, os.getcwd())}{suf}' if rel_path else file


def arg_files_print(
    limit: int,
    files: list[str],
    *,
    ignored_files: list[str] | None = None,
    name: str = '',
    ide_col_suf: bool = True,
    rel_path: bool = True,
    print_total: bool = True,
) -> None:
    if limit == 0:
        return
    if limit < 0:
        limit = len(files)
    if name:
        write_stdout(f'{name}:')
    for f in files[:limit]:
        write_stdout(arg_file_info(f, ide_col_suf=ide_col_suf, rel_path=rel_path))

    hidden_str = '' if len(files) <= limit else f'... {len(files) - limit} hidden. '
    ignored_str = '' if ignored_files is None else f'{len(ignored_files)} files ignored. '

    if print_total:
        write_stdout(f'... {len(files)} files found. {hidden_str}{ignored_str}')


def arg_file_glob_compile_files(include: list[str] | list[list[str]], exclude: list[str] | list[list[str]] | None = None) -> tuple[list[str], list[str]]:
    include_files = set()
    for inc in include:
        if not isinstance(inc, (list, tuple)):
            inc = [inc]
        for f in inc:
            assert isinstance(f, str), f'path must be str. "{type(f).__name__}" was given'
            include_files.add(os.path.abspath(f))

    exclude_files = set()
    for exc in (exclude or []):
        if not isinstance(exc, (list, tuple)):
            exc = [exc]
        for f in exc:
            assert isinstance(f, str), f'path must be str. "{type(f).__name__}" was given'
            exclude_files.add(os.path.abspath(f))

    res_files = include_files - exclude_files

    return list(sorted(res_files)), list(sorted(include_files - res_files))


def arg_files_glob(*, ignore_absent: bool = False, dir: bool = False) -> Callable[[str], list[str]]:
    def arg_files_glob_wr(value: str) -> list[str]:
        files: list[str] = list()
        if '*' in value:
            for gf in glob.iglob(value, recursive=True):
                gf_s = os.path.abspath(str(gf))
                if (dir and os.path.isdir(gf_s)) or (not dir and os.path.isfile(gf_s)):
                    files.append(os.path.abspath(gf_s))
        else:
            if (dir and os.path.isdir(value)) or (not dir and os.path.isfile(value)):
                files.append(os.path.abspath(value))
        if not ignore_absent and len(files) == 0:
            raise argparse.ArgumentTypeError(f'no files found with path template "{value}"')
        return files

    return arg_files_glob_wr
