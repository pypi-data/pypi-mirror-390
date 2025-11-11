import argparse
import os.path
import subprocess

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.utils.arg_files_glob import arg_files_glob, arg_file_glob_compile_files, arg_files_print, arg_file_info
from ul_py_tool.utils.colors import FG_RED, NC
from ul_py_tool.utils.step import Stepper, StepError
from ul_py_tool.utils.write_stdout import write_stdout


class CmdTest(Cmd):
    print_files: int
    py_file_ignore_lists: list[list[str]]
    py_file_lists: list[list[str]]

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        finder = arg_files_glob(ignore_absent=True)
        parser.add_argument('--print-files', dest='print_files', type=int, required=False, default=10)
        parser.add_argument('--files', dest='py_file_lists', help=f'{FG_RED}DEPRECATED!!!{NC}', nargs='+', type=finder, required=False, default=[])
        parser.add_argument('--ignore', dest='py_file_ignore_lists', nargs='+', type=finder, required=False, default=[
            finder('*/**/main.py'),
            finder('.*/**/*.py'),
            finder('*/**/__*__.py'),
        ])

    def _check_pytest_response(self, res: 'subprocess.CompletedProcess[bytes]') -> None:
        if res.returncode == 0:
            return
        if res.returncode == 5:
            return
        res.check_returncode()

    def _get_ini_cwd(self) -> str:
        cwd = os.getcwd()
        while cwd and len(cwd) > 5:
            if os.path.isfile(os.path.join(cwd, 'pytest.ini')):
                return cwd
            cwd = os.path.dirname(cwd)
        return os.getcwd()

    def run(self) -> None:
        stepper = Stepper()
        cwd = self._get_ini_cwd()
        tmp_dir = os.path.join(cwd, ".tmp")

        with stepper.step('PREPARE'):
            py_files, _1 = arg_file_glob_compile_files(self.py_file_lists, self.py_file_ignore_lists)
            if len(py_files) > 0:
                files_to_test = ",\n   ".join(arg_file_info(f) for f in py_files)
                raise StepError(f'--files param is deprecated!! please move your tests to __tests__dirs. files to test: \n   {files_to_test}')

            finder = arg_files_glob(ignore_absent=True)
            py_files, ignored_files = arg_file_glob_compile_files(
                include=[
                    finder('**/__tests__/*.py'),
                    finder('**/__tests__/**/*.py'),
                    finder('__tests__/*.py'),
                    finder('__tests__/**/*.py'),
                ],
                exclude=[
                    *self.py_file_ignore_lists,
                    finder('**/_*.py'),
                    finder('_*.py'),
                ],
            )

        with stepper.step('PYTEST') as stp:
            if len(py_files) == 0:
                write_stdout('no files to test')
                stp.skip()
            else:
                if self.print_files:
                    write_stdout('\n')
                    arg_files_print(self.print_files, py_files, ignored_files=ignored_files, name='testing files')
                    write_stdout('\n')
                    arg_files_print(self.print_files, ignored_files, name='ignored testing files')
                    write_stdout('\n')
                stp.run_cmd(
                    f'pytest -rxXs '
                    f'--cov={cwd} --no-cov-on-fail --cov-report html:{os.path.join(tmp_dir, "coverage")} '
                    f'-o cache_dir={tmp_dir} {" ".join(py_files)}',
                    chk=self._check_pytest_response,
                )


def test_example() -> None:
    assert 1 == 1
