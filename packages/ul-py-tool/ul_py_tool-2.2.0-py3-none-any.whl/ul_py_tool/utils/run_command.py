import os
import subprocess
import sys
from typing import NamedTuple

from ul_py_tool.utils.colors import FG_GREEN, NC, FG_RED

PIPE = 'pipe'
STDOUT = 'stdout'
DEVNULL = 'dev_null'

PATH_CONST__CWD = os.path.dirname(os.path.dirname(__file__))


STDERR_DESCRIPTOR_MAP = {
    PIPE: subprocess.PIPE,
    STDOUT: subprocess.STDOUT,
    DEVNULL: subprocess.DEVNULL,
}


class CommandResult(NamedTuple):
    code: int
    stdout: str

    def display(self, disable: bool = False) -> None:
        if disable:
            return

        sys.stdout.write(f'{self}\n')
        sys.stdout.flush()

    def __str__(self) -> str:
        return self.stdout

    def __repr__(self) -> str:
        return self.__str__()


def add_line_pref(some_str: str, pref: str) -> str:
    if not len(pref):
        return some_str

    result_str_lines = list()
    for str_line in some_str.split('\n'):
        if str_line.startswith(pref):
            result_str_lines.append(str_line)
        else:
            result_str_lines.append(f'{pref}{str_line}')

    return '\n'.join(result_str_lines)


def execute_command(command: list[str], cwd: str, silent: bool, stderr: int = subprocess.STDOUT) -> tuple[int, str]:
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=stderr, cwd=cwd, universal_newlines=True)  # nosec
    stdout: list[str] = []
    while process.poll() is None:
        line = process.stdout.readline()  # type: ignore
        stdout.append(line)
        if not silent:
            sys.stdout.write(line.strip() + '\r\n')
    result_stdout = ''.join(stdout)
    return process.returncode, result_stdout


def run_command(
    command: list[str] | str,
    ignore_errors: bool = False,
    silent: bool = False,
    msg_pref: str = '',
    cwd: str = PATH_CONST__CWD,
    stderr: str = STDOUT,
    simple: bool = False,
) -> CommandResult:
    assert stderr in STDERR_DESCRIPTOR_MAP, f'{stderr} given'
    if isinstance(command, str):
        command = [command]
    if not silent:
        for cmd in command:
            sys.stdout.write(f'{msg_pref}{FG_GREEN}(f"RUN::   {cmd}"){NC}\n')
            sys.stdout.flush()
    if simple:
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=PATH_CONST__CWD, shell=True, check=True)  # nosec
        except subprocess.CalledProcessError as e:
            if not silent:
                print(f'{msg_pref}{add_line_pref(e.stdout.decode("utf-8"), msg_pref)}')  # noqa
                print(f'{msg_pref}FAIL:\n{add_line_pref(e.stderr.decode("utf-8"), msg_pref)}')  # noqa
            if ignore_errors:
                return CommandResult(code=e.returncode, stdout=e.stdout.decode('utf-8'))
            raise

        if not silent:
            print(result.stdout.decode('utf-8'))  # noqa
            print(f'{msg_pref}WARNINIG:\n{add_line_pref(result.stderr.decode("utf-8"), msg_pref)}')  # noqa

        cmd_result = CommandResult(code=result.returncode, stdout=result.stdout.decode('utf-8'))

        return cmd_result

    stderr_descriptor = STDERR_DESCRIPTOR_MAP[stderr]
    return_code, stdout = execute_command(command, cwd=cwd, silent=silent, stderr=stderr_descriptor)
    if return_code != 0:
        if not silent:
            sys.stdout.write(f'{msg_pref}{FG_RED}"FAIL:"){NC}\n{add_line_pref(stdout, msg_pref)}')
            sys.stdout.flush()
        if ignore_errors:
            return CommandResult(code=return_code, stdout=stdout)
        raise Exception(f"command \"{command}\" exited with code {return_code}")

    cmd_result = CommandResult(code=return_code, stdout=stdout)

    return cmd_result
