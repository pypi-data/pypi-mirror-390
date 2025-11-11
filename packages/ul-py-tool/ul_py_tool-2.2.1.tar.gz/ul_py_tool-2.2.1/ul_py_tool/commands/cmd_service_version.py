import argparse
import os.path
from datetime import datetime
from enum import Enum

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.commands.conf import SERVICE_CHANGE_LOG
from ul_py_tool.utils.arg_file_exists import arg_file_exists
from ul_py_tool.utils.colors import FG_GREEN, NC, FG_BLUE
from ul_py_tool.utils.input_lines import input_lines
from ul_py_tool.utils.step import Stepper
from ul_py_tool.utils.write_stdout import write_stdout


class CmdServiceVersionType(Enum):
    PATCH = 'patch'
    MINOR = 'minor'
    MAJOR = 'major'


class CmdServiceVersion(Cmd):
    service_version_file: str
    type: CmdServiceVersionType

    @property
    def change_log_file(self) -> str:
        return os.path.join(os.path.dirname(self.service_version_file), SERVICE_CHANGE_LOG)

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--service-version-file', dest='service_version_file', type=arg_file_exists, default=os.path.join(os.getcwd(), '.service-version'), required=False)

    def _ask_change_logs(self, new_version: str, dt_now: datetime) -> bool:
        bugfixes_lines = input_lines(f'{FG_BLUE}bug fixes{NC}')
        new_features_lines = input_lines(f'{FG_BLUE}new features{NC}')
        release_notes_lines = input_lines(f'{FG_BLUE}release notes{NC}')

        if not len(bugfixes_lines) and not len(new_features_lines) and not len(release_notes_lines):
            return False

        logs_main_header = '# Changelog\n'

        logs_prev_content = ''
        if os.path.exists(self.change_log_file):
            with open(self.change_log_file, 'rt') as f:
                logs_prev_content = f.read()
        if not logs_prev_content:
            logs_prev_content = logs_main_header

        version_marker = '## Version `'

        log_version = f'{version_marker}{new_version}` - {dt_now.date().isoformat()}\n\n'

        for line in release_notes_lines:
            log_version += f'{line}\n\n'

        log_version += '' if not new_features_lines else '### New Features\n\n'
        for line in new_features_lines:
            log_version += f'- {line}\n'

        log_version += '\n' if new_features_lines else ''
        log_version += '' if not bugfixes_lines else '### Bug Fixes\n\n'
        for line in bugfixes_lines:
            log_version += f'- {line}\n'

        log_version += '\n'

        with open(self.change_log_file, 'wt+') as f:
            if version_marker in logs_prev_content:
                logs_prev_content = logs_prev_content.replace(version_marker, f'{log_version}\n\n{version_marker}', 1)
            else:
                logs_prev_content += f'\n\n{log_version}'
            f.write(logs_prev_content)

        return True

    def _increase_version(self) -> str:
        write_stdout(f'read "{self.service_version_file}"')
        with open(self.service_version_file, 'rt') as f:
            version = f.read()
        version_segm: tuple[int, int, int] = tuple(int(v) for v in version.split('.'))  # type: ignore

        if self.type is CmdServiceVersionType.PATCH:
            new_version_segm = (version_segm[0], version_segm[1], version_segm[2] + 1)
            write_stdout(f'{version} -> {new_version_segm[0]}.{new_version_segm[1]}.{FG_GREEN}{new_version_segm[2]}{NC}')
        elif self.type is CmdServiceVersionType.MINOR:
            new_version_segm = (version_segm[0], version_segm[1] + 1, 0)
            write_stdout(f'{version} -> {new_version_segm[0]}.{FG_GREEN}{new_version_segm[1]}.{new_version_segm[2]}{NC}')
        elif self.type is CmdServiceVersionType.MAJOR:
            new_version_segm = (version_segm[0] + 1, 0, 0)
            write_stdout(f'{version} -> {FG_GREEN}{new_version_segm[0]}.{new_version_segm[1]}.{new_version_segm[2]}{NC}')
        else:
            raise NotImplementedError(f'type {self.type} was not implemented for increasing version command')
        new_version = ".".join(str(i) for i in new_version_segm)

        with open(self.service_version_file, 'wt') as f:
            f.write(new_version)
            write_stdout(f'Changes saved to {self.service_version_file}')

        return new_version

    def run(self) -> None:
        dt_now = datetime.now()
        stepper = Stepper()

        with stepper.step('INCREASE VERSION', print_error=True):
            new_version = self._increase_version()

        with stepper.step('RELEASE NOTES') as stp:
            has_changelog_changes = self._ask_change_logs(new_version, dt_now)
            if not has_changelog_changes:
                stp.skip()

        files_to_add = [self.service_version_file]
        if has_changelog_changes:
            files_to_add.append(self.change_log_file)

        with stepper.step('GIT') as stp:
            stp.run_cmd(['git', 'reset'])
            stp.run_cmd(['git', 'add', *files_to_add])
            stp.run_cmd(['git', 'commit', '-m', new_version])
            stp.run_cmd(['git', 'tag', new_version + '-release'])


class CmdServiceVersionMinor(CmdServiceVersion):
    type: CmdServiceVersionType = CmdServiceVersionType.MINOR


class CmdServiceVersionPatch(CmdServiceVersion):
    type: CmdServiceVersionType = CmdServiceVersionType.PATCH


class CmdServiceVersionMajor(CmdServiceVersion):
    type: CmdServiceVersionType = CmdServiceVersionType.MAJOR
