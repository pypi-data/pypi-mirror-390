import argparse
import os

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.commands.conf import THIS_LIB_PATH, MYPY_CONFIG, PYENV_PY_VERSION, PRE_PUSH_DEST, PRE_COMMIT_DEST
from ul_py_tool.utils.arg_str2bool import arg_str2bool
from ul_py_tool.utils.fs import copy_if_destination_is_absent
from ul_py_tool.utils.step import Stepper


class CmdInstall(Cmd):
    force_replace: bool = False

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--force', dest='force_replace', type=arg_str2bool, required=False, default=False)

    def run(self) -> None:
        stepper = Stepper()

        with stepper.step('fix rights of git-hooks') as stp:
            stp.run_cmd(['chmod', '755', '-R', os.path.join(os.getcwd(), '.git', 'hooks')], ignore_error=True)

        with stepper.step('init git pre-push hook'):
            copy_if_destination_is_absent(os.path.join(THIS_LIB_PATH, 'conf', 'git.hook.pre-push.sh'), PRE_PUSH_DEST, replace=True)

        with stepper.step('init git pre-commit hook'):
            copy_if_destination_is_absent(os.path.join(THIS_LIB_PATH, 'conf', 'git.hook.pre-commit.sh'), PRE_COMMIT_DEST, replace=True)

        with stepper.step('init .gitignore'):
            copy_if_destination_is_absent(os.path.join(THIS_LIB_PATH, 'conf', 'gitignore'), os.path.join(os.getcwd(), '.gitignore'), replace=self.force_replace)

        with stepper.step('init .editorconfig'):
            copy_if_destination_is_absent(os.path.join(THIS_LIB_PATH, 'conf', 'editorconfig'), os.path.join(os.getcwd(), '.editorconfig'), replace=self.force_replace)

        with stepper.step('init .gitattributes'):
            copy_if_destination_is_absent(os.path.join(THIS_LIB_PATH, 'conf', 'gitattributes'), os.path.join(os.getcwd(), '.gitattributes'), replace=self.force_replace)

        with stepper.step('init python-version'):
            copy_if_destination_is_absent(os.path.join(THIS_LIB_PATH, 'conf', 'python-version'), os.path.join(os.getcwd(), PYENV_PY_VERSION), replace=self.force_replace)

        with stepper.step('init mypy'):
            copy_if_destination_is_absent(os.path.join(THIS_LIB_PATH, 'conf', MYPY_CONFIG), os.path.join(os.getcwd(), MYPY_CONFIG), replace=self.force_replace)

        with stepper.step('init pytest'):
            copy_if_destination_is_absent(os.path.join(THIS_LIB_PATH, 'conf', 'pytest.ini'), os.path.join(os.getcwd(), 'pytest.ini'), replace=self.force_replace)

        with stepper.step('fix rights of git-hooks') as stp:
            stp.run_cmd(['chmod', '755', '-R', os.path.join(os.getcwd(), '.git', 'hooks')], ignore_error=True)

        # with stepper.step('MYPY') as stp:
        #     stp.run_cmd([
        #         'mypy',
        #         '--install-types',
        #         '--non-interactive',
        #     ], ignore_error=True)
