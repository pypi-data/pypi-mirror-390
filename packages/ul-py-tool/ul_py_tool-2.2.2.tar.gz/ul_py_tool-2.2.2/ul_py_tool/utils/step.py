import contextlib
import io
import os
import shutil
import subprocess
import sys
import traceback
from typing import Generator, Optional, Callable, NamedTuple

from ul_py_tool.commands.conf import MAX_LINE_LEN
from ul_py_tool.utils.arg_files_glob import arg_file_info
from ul_py_tool.utils.colors import FG_RED, NC, FG_GREEN, FG_GRAY, FG_BLUE, FG_YELLOW
from ul_py_tool.utils.write_stdout import write_stdout

TChk = Optional[Callable[['subprocess.CompletedProcess[bytes]'], None]]


class StepError(Exception):
    pass


class StepFileErr(NamedTuple):
    err: str
    col: int | None
    code: str | None


class Step:
    def __init__(self, name: str, n: int) -> None:
        self._n = n
        self._name = name
        self._raised = False
        self._errors_in_file: dict[str, dict[int, set[StepFileErr]]] = dict()
        self._skipped = False

        write_stdout('')
        self._print(f'{FG_BLUE}{self._name}{NC}')

        self._errors: set[str] = set()
        self._warns: set[str] = set()

    def _print(self, txt: str) -> None:
        write_stdout(f'{FG_BLUE}[{self._n:0>2}]{NC} :: {txt}')

    def skip(self) -> None:
        if self._skipped:
            return
        self._skipped = True
        self._print(f'{FG_GRAY}SKIPPED{NC}')

    def add_error(self, message: str) -> None:
        self._errors.add(message)

    def add_warn(self, message: str) -> None:
        self._warns.add(message)

    def _internal_use_raise_if_has_errors(self) -> None:
        assert not self._raised
        self._raised = True

        has_errors = False
        max_len_of_file = 0
        errors_list = []
        for file, error_lines in self._errors_in_file.items():
            for line, errors in error_lines.items():
                for err in errors:
                    file_info = arg_file_info(file, line=line, col=err.col)
                    file_err = f'{err.err} {f"{FG_GRAY}({err.code}){NC}" if err.code is not None else ""}'
                    max_len_of_file = max(max_len_of_file, len(file_info))
                    errors_list.append((file_info, file_err))

        for file_info, file_err in errors_list:
            write_stdout(f'{file_info: <{max_len_of_file}} :: {file_err}')

        has_errors = len(errors_list) > 0 or has_errors
        has_warns = len(self._warns) > 0

        for err_str in self._errors:
            has_errors = True
            write_stdout(err_str)

        for warn_str in self._warns:
            write_stdout(f'{FG_YELLOW}{warn_str}{NC}')

        if has_errors:
            raise StepError()

        if not self._skipped:
            self._print(f'{FG_GREEN if not has_warns else FG_YELLOW}DONE{NC}')

    def add_error_in_file(self, file: str, err: str, *, line: int = 0, col: int | None = None, code: str | None = None) -> None:
        if file not in self._errors_in_file:
            self._errors_in_file[file] = dict()
        if line not in self._errors_in_file[file]:
            self._errors_in_file[file][line] = set()
        self._errors_in_file[file][line].add(StepFileErr(col=col, code=code, err=err))

    def run_cmd(self, cmd: list[str] | str, chk: TChk = None, ignore_error: bool = False, print_std: bool = True) -> 'subprocess.CompletedProcess[bytes]':
        ret_code = -1

        kwargs = dict()
        if chk is None and print_std:
            kwargs['stderr'] = sys.stderr
            kwargs['stdout'] = sys.stdout
        cmd_log = cmd if isinstance(cmd, str) else (" ".join(cmd))
        write_stdout(f'run cmd :: {FG_GRAY}{cmd_log if len(cmd_log) < MAX_LINE_LEN else f"{cmd_log[:MAX_LINE_LEN]}..."}{NC}')

        try:
            subprocess_result = subprocess.run(  # type: ignore
                cmd,
                shell=isinstance(cmd, str),
                check=False,
                capture_output=chk is not None or not print_std,
                cwd=os.getcwd(),
                env={
                    **os.environ,
                    "COLOR": '1',
                    "COLORS": '1',
                    "FORCE_COLOR": '1',
                    "FORCE_COLORS": '1',
                },
                **kwargs,
            )

            ret_code = subprocess_result.returncode
            if chk is not None:
                if print_std:
                    shutil.copyfileobj(io.StringIO(subprocess_result.stdout.decode()), sys.stdout)
                    shutil.copyfileobj(io.StringIO(subprocess_result.stderr.decode()), sys.stderr)
                chk(subprocess_result)
            else:
                subprocess_result.check_returncode()
        except Exception as e:  # noqa: B902
            if not isinstance(e, subprocess.CalledProcessError):
                write_stdout(f'{FG_RED}ERROR:{NC} {type(e).__name__} :: {e}')
                write_stdout(traceback.format_exc())
            if not ignore_error:
                write_stdout(f'run cmd :: {FG_RED}ERROR{NC} exit code {ret_code}')
                raise StepError()
            write_stdout(f'run cmd :: {FG_YELLOW}DONE with ignored error{NC}')
            return subprocess_result
        write_stdout(f'run cmd :: {FG_GREEN}DONE{NC}')

        return subprocess_result


class Stepper:
    def __init__(self) -> None:
        self._index = 0

    @contextlib.contextmanager
    def step(self, name: str, print_error: bool = True, ignore_error: bool = False) -> Generator[Step, None, None]:
        self._index += 1
        stp = Step(name, self._index)
        try:
            yield stp
            stp._internal_use_raise_if_has_errors()  # noqa
        except StepError:
            raise
        except Exception as e:  # noqa: B902
            if print_error:
                write_stdout(f'{FG_RED}ERROR:{NC} {type(e).__name__} :: {e}')
            if not ignore_error:
                raise
            write_stdout(f'{FG_GREEN}>> {name} :: DONE {NC}{FG_YELLOW}with ignored error{NC}')
