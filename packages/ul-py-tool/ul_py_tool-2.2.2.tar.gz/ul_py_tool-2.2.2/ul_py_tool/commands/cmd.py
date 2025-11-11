import argparse
import importlib
import logging
import os
import sys
from typing import Mapping, Type

from pydantic import BaseModel

from ul_py_tool.utils.colors import FG_RED, NC, FG_YELLOW
from ul_py_tool.utils.step import StepError
from ul_py_tool.utils.write_stdout import write_stdout


class Cmd(BaseModel):
    cmd: str = ''
    log: str = 'INFO'

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        pass

    def run(self) -> None:
        write_stdout('be brave!')

    @staticmethod
    def main(commands: Mapping[str, Type['Cmd'] | str], *, cwd: str | None = None) -> None:
        """

        :rtype: object
        """
        if cwd is not None:
            assert os.path.abspath(os.path.normpath(cwd)) == os.path.abspath(os.path.normpath(os.getcwd())), f'script must run from cwd "{cwd}". from "{os.getcwd()}" was ran'
            sys.path.append(cwd)

        parser = argparse.ArgumentParser()
        parser.add_argument('--log', type=str, default='INFO', required=False)
        cmd_parser = parser.add_subparsers(required=True, dest='cmd')

        cmd_name = sys.argv[1] if len(sys.argv) > 1 else None
        cmd = commands.get(cmd_name or '', None)
        if cmd is None:
            write_stdout(f'{FG_RED}command "{cmd_name}" is not supported. must be on of ({", ".join(commands.keys())}){NC}')
            exit(1)

        assert cmd_name is not None

        if not isinstance(cmd, str):
            cmd_class = cmd
        else:
            assert ':' in cmd
            cmd = cmd.strip()
            cmd_segm = cmd.split(':')
            assert len(cmd_segm) == 2
            mdl = importlib.import_module(cmd_segm[0].strip())
            cmd_class = getattr(mdl, cmd_segm[1].strip())
        assert cmd_class is not None
        assert issubclass(cmd_class, Cmd)
        cmd_class.add_parser_args(cmd_parser.add_parser(cmd_name))

        args = dict(vars(parser.parse_args()))
        log = args['log'].upper()

        logging.basicConfig(level=getattr(logging, log), format='ulpytool :: %(asctime)s :: %(levelname)s :: %(message)s')

        try:
            cmd_instance = cmd_class(**args)
            cmd_instance.run()
        except KeyboardInterrupt:
            write_stdout(f'\n{FG_YELLOW}...interrupted!{NC}')
            sys.exit(1)
        except StepError as e:
            msg = str(e)
            if msg:
                write_stdout(msg)
            write_stdout(f'{FG_RED}FAILED{NC}')
            sys.exit(1)
