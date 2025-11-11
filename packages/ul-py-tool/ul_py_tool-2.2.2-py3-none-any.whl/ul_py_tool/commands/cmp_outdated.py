import argparse
import os.path

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.commands.conf import PIPFILE
from ul_py_tool.utils.colors import NC, FG_GRAY, FG_GREEN, FG_RED
from ul_py_tool.utils.pipfile import Pipfile
from ul_py_tool.utils.write_stdout import write_stdout


class CmdOutdated(Cmd):
    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        pass

    def run(self) -> None:
        pipfile = os.path.join(os.getcwd(), PIPFILE)
        ppfile = Pipfile.load(pipfile)

        max_len_pack = 0
        max_len_ver = 7
        for pack in ppfile.all_packages.values():
            max_len_pack = max(max_len_pack, len(pack.name))
            max_len_ver = max(max_len_ver, len(pack.clean_version))

        write_stdout(f'\n        {FG_GRAY}|{NC} {"Name": <{max_len_pack}} {FG_GRAY}|{NC} {"Current": >{max_len_ver}} {FG_GRAY}|{NC} Actual')
        write_stdout(f' {FG_GRAY}{"-" * 7}|{"-" * (1 + max_len_pack + 1)}|{"-" * (1 + max_len_ver + 1)}|{"-" * 16}{NC}')
        ln = len(ppfile.all_packages)
        has_outdated = False
        for i, pack in enumerate(ppfile.all_packages.values()):
            if len(pack.available_versions) > 0:
                has_outdated = True
                write_stdout(f'  {FG_GRAY}{i + 1:0>2}/{ln:0<2}{NC} {FG_GRAY}|{NC}'
                             f' {FG_RED}{pack.name: <{max_len_pack}}{NC} {FG_GRAY}|{NC}'
                             f' {FG_RED}{pack.clean_version: >{max_len_ver}}{NC} {FG_GRAY}|{NC}'
                             f' {FG_GREEN}{pack.available_versions[-1]}{NC}')
            else:
                write_stdout(f'  {FG_GRAY}{i + 1:0>2}/{ln:0<2}{NC} {FG_GRAY}|{NC}'
                             f' {pack.name: <{max_len_pack}} {FG_GRAY}|{NC}'
                             f' {pack.clean_version: >{max_len_ver}} {FG_GRAY}|{NC}'
                             f' {FG_GRAY}{pack.clean_version}{NC}')
        write_stdout('' if has_outdated else f'{FG_GREEN}NOTHING TO UPDATE{NC}')
        exit(int(has_outdated))
