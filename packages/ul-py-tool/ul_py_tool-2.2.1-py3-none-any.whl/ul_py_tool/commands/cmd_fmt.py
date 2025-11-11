import argparse

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.utils.arg_files_glob import (
    arg_files_glob,
    arg_file_glob_compile_files,
    arg_files_print,
)
from ul_py_tool.utils.step import Stepper


class CmdFmt(Cmd):
    py_file_lists: list[list[str]]
    py_file_ignore_lists: list[list[str]]
    print_files: int

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--print-files",
            dest="print_files",
            type=int,
            required=False,
            default=10,
        )
        parser.add_argument(
            "--py-files",
            dest="py_file_lists",
            nargs="+",
            type=arg_files_glob(),
            required=False,
            default=[
                arg_files_glob(ignore_absent=True)("*.py"),
                arg_files_glob(ignore_absent=True)("**/*.py"),
            ],
        )
        parser.add_argument(
            "--py-files-ignore",
            dest="py_file_ignore_lists",
            nargs="+",
            type=arg_files_glob(ignore_absent=True),
            required=False,
            default=[],
        )

    def run(self) -> None:
        py_files, ignored_files = arg_file_glob_compile_files(
            self.py_file_lists,
            self.py_file_ignore_lists,
        )
        arg_files_print(
            self.print_files,
            py_files,
            ignored_files=ignored_files,
            name="python files",
        )

        stepper = Stepper()

        # stp.step_cmd('ISORT', [
        #     'python', '-m', 'isort',
        #     '--profile=pycharm',
        #     '--order-by-type',
        #     '--diff',
        #     '--trailing-comma',
        #     '--honor-noqa',
        #     '--color',
        #     # '--force-single-line-imports',
        #     '--force-alphabetical-sort',
        #     '--lines-after-imports=2',
        #     '--lines-between-types=1',
        #     '--settings-path', os.path.join(THIS_LIB_PATH, 'conf', 'isort.cfg'),
        #     # '--show-config',
        #     # '--no-sections',
        #     '--line-length', '180',
        #     # '--sections=FUTURE,STDLIB,FIRSTPARTY,THIRDPARTY,LOCALFOLDER',
        #     # '--check-only',
        #     *py_files,
        # ], chk=self._check_isort, print_std=False)

        with stepper.step("BLACK") as stp:
            stp.run_cmd(["black", *py_files])
