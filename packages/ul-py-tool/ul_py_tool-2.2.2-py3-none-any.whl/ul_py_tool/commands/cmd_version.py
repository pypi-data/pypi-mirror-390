import argparse
import os.path
import re
from datetime import datetime
from enum import Enum

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.commands.conf import CHANGE_LOG
from ul_py_tool.utils.arg_file_exists import arg_file_exists
from ul_py_tool.utils.colors import FG_GREEN, NC, FG_BLUE
from ul_py_tool.utils.input_lines import input_lines
from ul_py_tool.utils.step import Stepper, StepError
from ul_py_tool.utils.write_stdout import write_stdout


class CmdVersionType(Enum):
    PATCH = 'patch'
    MINOR = 'minor'
    MAJOR = 'major'


class CmdVersion(Cmd):
    setup_file: str
    type: CmdVersionType

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--setup-file', dest='setup_file', type=arg_file_exists, default=os.path.join(os.getcwd(), 'setup.py'), required=False)

    @property
    def change_log_file(self) -> str:
        return os.path.join(os.path.dirname(self.setup_file), CHANGE_LOG)

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
        reg = re.compile(r'version\s*=\s*["\']\d+\.\d+\.\d+[\'"]')
        reg_version = re.compile(r'(version\s*=\s*["\'])(\d+\.\d+\.\d+)([\'"])')

        write_stdout(f'read "{self.setup_file}"')
        with open(self.setup_file, 'rt') as f:
            content = f.read()
            all_versions = reg.findall(content)
            if len(all_versions) == 0:
                write_stdout(f'semver was not found in file "{self.setup_file}"')
                raise StepError()
            if len(all_versions) > 1:
                write_stdout(f'semver was found more than once in file "{self.setup_file}"')
                raise StepError()
            match: str = all_versions[0]
            version_parts: tuple[str, str, str] = reg_version.match(match).groups()  # type: ignore
            assert len(version_parts) == 3
            version: str = version_parts[1]
            write_stdout(f'found version {version}')

        version_segm: tuple[int, int, int] = tuple(int(v) for v in version.split('.'))  # type: ignore

        if self.type is CmdVersionType.PATCH:
            new_version_segm = (version_segm[0], version_segm[1], version_segm[2] + 1)
            write_stdout(f'{version} -> {new_version_segm[0]}.{new_version_segm[1]}.{FG_GREEN}{new_version_segm[2]}{NC}')
        elif self.type is CmdVersionType.MINOR:
            new_version_segm = (version_segm[0], version_segm[1] + 1, 0)
            write_stdout(f'{version} -> {new_version_segm[0]}.{FG_GREEN}{new_version_segm[1]}.{new_version_segm[2]}{NC}')
        elif self.type is CmdVersionType.MAJOR:
            new_version_segm = (version_segm[0] + 1, 0, 0)
            write_stdout(f'{version} -> {FG_GREEN}{new_version_segm[0]}.{new_version_segm[1]}.{new_version_segm[2]}{NC}')
        else:
            raise NotImplementedError(f'type {self.type} was not implemented for increasing version command')
        new_version = ".".join(str(i) for i in new_version_segm)
        content = content.replace(match, f'{version_parts[0]}{new_version}{version_parts[2]}')

        with open(self.setup_file, 'wt') as f:
            f.write(content)
            write_stdout(f'Changes saved to {self.setup_file}')

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

        files_to_add = [self.setup_file]
        if has_changelog_changes:
            files_to_add.append(self.change_log_file)

        with stepper.step('GIT') as stp:
            stp.run_cmd(['git', 'reset'])
            stp.run_cmd(['git', 'add', *files_to_add])
            stp.run_cmd(['git', 'commit', '-m', new_version])
            stp.run_cmd(['git', 'tag', new_version])


class CmdVersionMinor(CmdVersion):
    type: CmdVersionType = CmdVersionType.MINOR


class CmdVersionPatch(CmdVersion):
    type: CmdVersionType = CmdVersionType.PATCH


class CmdVersionMajor(CmdVersion):
    type: CmdVersionType = CmdVersionType.MAJOR
