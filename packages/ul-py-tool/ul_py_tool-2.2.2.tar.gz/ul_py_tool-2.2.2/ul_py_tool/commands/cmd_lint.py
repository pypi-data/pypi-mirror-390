import argparse
import configparser
import json
import os
import platform
import re
import subprocess
import sys
from typing import Any, Pattern

import tomli
import yaml

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.commands.conf import MAX_LINE_LEN, THIS_LIB_PATH, PYENV_PY_VERSION, SUPPORTED_PYTHON_VERSIONS, \
    MYPY_CONFIG, PIPFILE, PRE_PUSH_DEST, \
    PRE_COMMIT_DEST, UNDER_CI_JOB, PY_TYPED, SOURCE_PYPI, SOURCE_NERO_GITLAB, SOURCE_NERO_GITLAB_HOST, \
    SOURCE_NERO_GITLAB_URL, PIPFILE_LOCK
from ul_py_tool.utils.arg_files_glob import arg_files_glob, arg_file_glob_compile_files, arg_files_print, arg_file_info
from ul_py_tool.utils.arg_str2bool import arg_str2bool
from ul_py_tool.utils.colors import FG_RED, NC, FG_YELLOW, FG_GRAY
from ul_py_tool.utils.pipfile import Pipfile
from ul_py_tool.utils.step import StepError, Stepper, Step
from ul_py_tool.utils.write_stdout import write_stdout


class CmdLint(Cmd):
    setup_file_lists: list[list[str]]
    fix: bool
    py_file_lists: list[list[str]]
    py_file_ignore_lists: list[list[str]]
    # docker_registry_tpl: str
    dockerfiles_lists: list[list[str]]
    dockerfiles_ignore_lists: list[list[str]]
    dockercomposefiles_lists: list[list[str]]
    dockercomposefiles_ignore_lists: list[list[str]]
    helmtemplates_lists: list[list[str]]
    helmtemplates_ignore_lists: list[list[str]]
    yml_file_lists: list[list[str]]
    yml_file_ignored_lists: list[list[str]]
    print_files: int
    check_environment: bool
    check_imports: bool
    exclude_libs: list[str]
    packages_ignored: list[str]
    py_init_dir_ignore_lists: list[list[str]]
    packages_ignored_in_setup: list[str]
    check_hooks: bool
    check_setup_packages: bool
    check_nero_packages_is_fresh: bool
    check_packages: bool

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--fix', dest='fix', type=arg_str2bool, default=False)
        parser.add_argument('--check-env', dest='check_environment', type=arg_str2bool, default=False)
        parser.add_argument('--check-hooks', dest='check_hooks', type=arg_str2bool, required=False, default=not UNDER_CI_JOB)
        parser.add_argument('--check-imports', dest='check_imports', type=arg_str2bool, default=True, required=False)
        parser.add_argument('--check-packages', dest='check_packages', type=arg_str2bool, default=not UNDER_CI_JOB, required=False)
        parser.add_argument('--check-setup-packages', dest='check_setup_packages', type=arg_str2bool, default=not UNDER_CI_JOB, required=False)
        parser.add_argument('--check-nero-packages-is-fresh', dest='check_nero_packages_is_fresh', type=arg_str2bool, default=not UNDER_CI_JOB, required=False)
        parser.add_argument('--ignore-setup-packages', dest='packages_ignored_in_setup', type=str, default=[], nargs='+', required=False)
        parser.add_argument('--ignore-packages', dest='packages_ignored', type=str, default=[], nargs='+', required=False)

        parser.add_argument('--exclude-import', dest='exclude_libs', type=str, default=[], nargs='+', required=False)

        parser.add_argument('--print-files', dest='print_files', type=int, required=False, default=10)

        #  parser.add_argument('--docker-registry-tpl', dest='docker_registry_tpl', type=str, required=False, default='gitlab.neroelectronics.by:5050/unic-lab')

        parser.add_argument('--dockerfiles-ignore', dest='dockerfiles_ignore_lists', nargs='+', type=arg_files_glob(ignore_absent=True), required=False, default=[])
        parser.add_argument('--dockerfiles', dest='dockerfiles_lists', nargs='+', type=arg_files_glob(), required=False, default=[
            arg_files_glob(ignore_absent=True)('Dockerfile'),
            arg_files_glob(ignore_absent=True)('**/Dockerfile'),
        ])

        parser.add_argument('--dockercomposefiles-ignore', dest='dockercomposefiles_ignore_lists', nargs='+', type=arg_files_glob(ignore_absent=True), required=False, default=[])
        parser.add_argument('--dockercomposefiles', dest='dockercomposefiles_lists', nargs='+', type=arg_files_glob(), required=False, default=[
            arg_files_glob(ignore_absent=True)('**/*.docker-compose.yml'),
            arg_files_glob(ignore_absent=True)('**/docker-compose.*.yml'),
            arg_files_glob(ignore_absent=True)('**/docker-compose.yml'),
            arg_files_glob(ignore_absent=True)('*.docker-compose.yml'),
            arg_files_glob(ignore_absent=True)('docker-compose.*.yml'),
            arg_files_glob(ignore_absent=True)('docker-compose.yml'),
        ])

        parser.add_argument('--helmtemplatefiles-ignore', dest='helmtemplates_ignore_lists', nargs='+', type=arg_files_glob(ignore_absent=True), required=False, default=[])
        parser.add_argument('--helmtemplatefiles', dest='helmtemplates_lists', nargs='+', type=arg_files_glob(), required=False, default=[
            arg_files_glob(ignore_absent=True)('.helm/templates/**/*.yml'),
            arg_files_glob(ignore_absent=True)('.helm/templates/*.yml'),
        ])

        parser.add_argument('--setup-files', dest='setup_file_lists', nargs='+', type=arg_files_glob(ignore_absent=True), required=False, default=[
            arg_files_glob(ignore_absent=True)('setup.py'),
        ])

        parser.add_argument('--py-init-dir-ignore', dest='py_init_dir_ignore_lists', nargs='+', type=arg_files_glob(ignore_absent=True, dir=True), required=False, default=[
            arg_files_glob(ignore_absent=True, dir=True)('__init__.py'),
        ])

        parser.add_argument('--py-files-ignore', dest='py_file_ignore_lists', nargs='+', type=arg_files_glob(ignore_absent=True), required=False, default=[
            arg_files_glob(ignore_absent=True)('**/.*/**/*.py'),
        ])
        parser.add_argument('--py-files', dest='py_file_lists', nargs='+', type=arg_files_glob(), required=False, default=[
            arg_files_glob(ignore_absent=True)('**/*.py'),
        ])

        parser.add_argument('--yml-files-ignore', dest='yml_file_ignored_lists', nargs='+', type=arg_files_glob(ignore_absent=True), required=False, default=[
        ])
        parser.add_argument('--yml-files', dest='yml_file_lists', nargs='+', type=arg_files_glob(), required=False, default=[
            arg_files_glob(ignore_absent=True)('*.yml'),
            arg_files_glob(ignore_absent=True)('**/*.yml'),
        ])

    def _check_type_ignore_file(self, files: list[str]) -> None:
        ingore_re = re.compile(r'^\s*#\s*type\s*:\s*ignore\s*')
        noqa_re = re.compile(r'^\s*#\s*noqa\s*$')
        flake8_noqa_re = re.compile(r'^\s*#\s*flake8\s*:\s*noqa\s*$')
        type_ignored_files = []
        noqa_files = []
        for file in files:
            with open(file, 'rt') as f:
                for line in f.readlines():
                    if ingore_re.match(line) is not None:
                        type_ignored_files.append(file)
                        break
                    if noqa_re.match(line) is not None:
                        noqa_files.append(file)
                        break
                    if flake8_noqa_re.match(line) is not None:
                        noqa_files.append(file)
                        break
        if len(type_ignored_files) > 0 or len(noqa_files) > 0:
            for ign_file in type_ignored_files:
                write_stdout(f'{arg_file_info(ign_file)} :: has "# type: ignore" for HOLE FILE. please explicitly ignore this file from linting recipe')
            for ign_file in noqa_files:
                write_stdout(f'{arg_file_info(ign_file)} :: has "# noqa" or "# flake8: noqa" for HOLE FILE. please explicitly ignore this file from linting recipe')
            raise StepError()

    def _check_isort(self, result: 'subprocess.CompletedProcess[bytes]') -> None:
        lines_count = 0
        for line in result.stderr.decode('utf-8').split('\n'):
            line = line.strip()
            if not line:
                continue
            lines_count += 1
            write_stdout(line.replace('ERROR: ', '').replace(' Imports ', f':0 {FG_RED}Imports ') + NC)
        write_stdout(f'{lines_count} errors')
        if lines_count > 0:
            raise StepError()

    def _step_check_setup_files(self) -> bool:
        setup_files, ignored_files = arg_file_glob_compile_files(self.setup_file_lists)

        if len(setup_files) == 0:
            return False

        arg_files_print(self.print_files, setup_files, print_total=False, name='setup files')
        for setup_file in setup_files:
            with open(setup_file, 'rt') as f:
                setup_file_content = f.read()
                if PY_TYPED not in setup_file_content:
                    raise StepError(f'"py.typed" must be specified in {setup_file}. please add "py.typed" EMPTY file to repo and specify it in setup.py')
        return True

    def _check_imports(self, py_files: list[str]) -> bool:
        excl_libs = set(self.exclude_libs or [])
        libs = {i for i in {'flask', 'requests', 'flask_limiter', 'werkzeug'} if i not in excl_libs}

        if len(libs) == 0:
            return False

        write_stdout(f'Checking libs: {", ".join(libs)}')
        regs: dict[str, list[Pattern[str]]] = {}
        for lib in libs:
            regs[lib] = [
                re.compile(rf'^\s*import\s+{lib}\s+'),
                re.compile(rf'^\s*import\s+{lib}\.'),
                re.compile(rf'^\s*from\s+{lib}\s+'),
                re.compile(rf'^\s*from\s+{lib}\.'),
            ]

        errors: dict[str, list[str]] = {}
        for py_file in py_files:
            with open(py_file, 'rt') as f:
                for i, line in enumerate(f.readlines()):
                    for lib, reg_list in regs.items():
                        for reg in reg_list:
                            for m in reg.findall(line):
                                if py_file not in errors:
                                    errors[py_file] = []
                                errors[py_file].append((
                                    f'{py_file}:{i + 1}: '
                                    f'{FG_RED}RESTRICTED{NC} import of "{FG_RED}{lib}{NC}" in line #{i} '
                                    f'::    {line.replace(m, f"{FG_YELLOW}{m.strip()}{NC}").strip()}'
                                ))
        if len(errors.keys()) > 0:
            for _1, err_list in errors.items():
                for err in err_list:
                    write_stdout(err)
            raise StepError()
        return True

    def _step_check_gitignore(self) -> bool:
        gitignore = os.path.join(os.getcwd(), '.gitignore')
        if not os.path.isfile(gitignore):
            write_stdout(f'file "{gitignore}" was not found ')
            raise StepError()
        with open(gitignore, 'rt') as f:
            for line in f.readlines():
                if PYENV_PY_VERSION in line:
                    raise StepError(f'found {PYENV_PY_VERSION} in version. REMOVE IT FROM .gitignore')
        return True

    def _step_check_python_version(self) -> None:
        python_version_fp = os.path.join(os.getcwd(), PYENV_PY_VERSION)
        if not os.path.exists(python_version_fp):
            raise StepError(f'file ./{PYENV_PY_VERSION}:0 not found. please use pyenv!')
        with open(python_version_fp, 'rt') as f:
            version_string = f.read().strip()
        m = re.compile(r'^\d+\.\d+\.\d+$').findall(version_string)
        if len(m) != 1:
            raise StepError(f'invalid format of python version. {version_string} was given')

        version: str = m[0]
        minor_version = ".".join(version.split('.')[:2])
        if not any(version.startswith(v) for v in SUPPORTED_PYTHON_VERSIONS):
            raise StepError(f'unsupported python version. MUST BE {" or ".join(SUPPORTED_PYTHON_VERSIONS)}. {version} was given')
        if not version.startswith('.'.join(platform.python_version_tuple()[:2])):
            write_stdout(f'unsupported version of python to run this script. must be {minor_version}. {sys.version} was ran')

        mypy_config_fp = os.path.join(os.getcwd(), MYPY_CONFIG)
        if os.path.exists(mypy_config_fp):
            config = configparser.ConfigParser()
            config.read(mypy_config_fp)
            mypy_section = config['mypy']
            if not mypy_section:
                raise StepError(f'[mypy] section must be specified in {mypy_config_fp}')
            mypy_py_version = mypy_section.get('python_version', None)
            if not mypy_py_version:
                raise StepError(f'python_version must be specified in {mypy_config_fp}')
            if not mypy_py_version.startswith(minor_version):
                raise StepError(f'python_version in {MYPY_CONFIG} is not compatible with version in {PYENV_PY_VERSION}. must be {minor_version}')

        pipfile = os.path.join(os.getcwd(), PIPFILE)
        if not os.path.exists(pipfile):
            raise StepError(f'file {pipfile} must be specified')

        with open(pipfile, 'rt') as f:
            pipfile_content = tomli.loads(f.read())

        pipfile_requires = pipfile_content.get('requires', None)
        if pipfile_requires is None:
            raise StepError(f'[requires] section must be specified in {PIPFILE}')

        pipfile_py_version: str | None = pipfile_requires.get('python_version', None)
        if pipfile_py_version is None:
            raise StepError(f'python_version must be specified in {PIPFILE}')

        if not pipfile_py_version.startswith(minor_version):
            raise StepError(f'python_version in {PIPFILE} not compatible with version in {PYENV_PY_VERSION}. must be {minor_version}')

    def _step_check_hooks(self) -> bool:
        if not self.check_hooks:
            return False

        with open(PRE_COMMIT_DEST, 'rt') as f:
            content = f.read()
            if 'pipenv run lint' not in content:
                raise StepError('"pipenv run lint" must be in pre-commit hook. please do "ulpytool install"')

        with open(PRE_PUSH_DEST, 'rt') as f:
            content = f.read()
            if 'pipenv run test' not in content:
                raise StepError('"pipenv run test" must be in pre-push hook. please do "ulpytool install"')
            if 'pipenv run lint' not in content:
                raise StepError('"pipenv run lint" must be in pre-push hook. please do "ulpytool install"')
        return True

    def _check_docker_image(self, file: str, stp: Step, image: str | None = None, *, line: int = 0, err_prefix: str = '') -> None:
        if image is None:
            return
        if len(image) == 0:
            return
        if 'WERF_' in image:
            return
        # if self.docker_registry_tpl not in image:
            # stp.add_error_in_file(file, f'{err_prefix} invalid image. must starts from "{self.docker_registry_tpl}". "{image}" was given', line=line)

    def _step_check_docker_compose_files(self, stp: Step) -> bool:
        dockercomposefiles, ignored_files = arg_file_glob_compile_files(self.dockercomposefiles_lists, self.dockercomposefiles_ignore_lists)
        if len(dockercomposefiles) == 0:
            return False
        arg_files_print(self.print_files, dockercomposefiles, ignored_files=ignored_files, name='docker-compose files')
        for dcf in dockercomposefiles:
            with open(dcf, 'rt') as f:
                content = yaml.load(f.read(), yaml.SafeLoader)
            if content.get('version') != '3.8':
                stp.add_error_in_file(dcf, 'invalid specification version. must be 3.8')
            if 'services' not in content:
                stp.add_error_in_file(dcf, 'no services found')
                continue
            for service_name, sv in content['services'].items():
                self._check_docker_image(dcf, stp, sv.get('image', None), err_prefix=f'service "{FG_RED}{service_name}{NC}" has ')
        return True

    def _step_check_dockerfiles(self, stp: Step) -> bool:
        dockerfiles, ignored_files = arg_file_glob_compile_files(self.dockerfiles_lists, self.dockerfiles_ignore_lists)
        if len(dockerfiles) == 0:
            return False
        arg_files_print(self.print_files, dockerfiles, ignored_files=ignored_files, name='Dockerfiles')
        for df in dockerfiles:
            with open(df, 'rt') as f:
                df_lines = f.readlines()
            for li, lc in enumerate(df_lines):
                lc = lc.strip()
                if lc.startswith('FROM'):
                    res = re.split(r'\s+', lc)
                    self._check_docker_image(df, stp, res[1], line=li + 1)
                if lc.startswith('RUN'):
                    if 'pipenv' in lc and 'install' in lc:
                        valid_pipenv_install_str = 'RUN pipenv install --dev --system --deploy --ignore-pipfile'
                        if lc != valid_pipenv_install_str:
                            stp.add_error_in_file(df, f'invalid command of packages installation from Pipfile. must be "{valid_pipenv_install_str}". "{lc}" was given', line=li + 1)
        return True

    def _find_helm_spec(self, spec: Any, prop: str, *, _context: str = '') -> list[tuple[Any, str]]:
        res: list[tuple[Any, str]] = []
        if isinstance(spec, dict):
            if prop in spec:
                res.append((spec[prop], _context[1:] if _context.startswith('.') else _context))
            for k, v in spec.items():
                res = [*res, *self._find_helm_spec(v, prop, _context=f'{_context}.{k}')]
        if isinstance(spec, list):
            for i, v in enumerate(spec):
                res = [*res, *self._find_helm_spec(v, prop, _context=f'{_context}.{i}')]
        return res

    def check_helm(self, stp: Step) -> bool:
        helm_files, ignored_files = arg_file_glob_compile_files(self.helmtemplates_lists, self.helmtemplates_ignore_lists)
        if len(helm_files) == 0:
            return False
        for f_name in helm_files:
            with open(f_name, 'rt') as f:
                contents = ['']
                for line in f.read().split('\n'):
                    if line.startswith('#'):
                        continue
                    line = re.sub(r'\{\{[^}]+\}\}', '', line)
                    if len(line.strip()) == 0:
                        continue
                    if line == '---':
                        if len(contents[-1]) > 0:
                            contents.append('')
                        continue
                    contents[-1] += f'\n{line}'
                yml_contents = [yaml.load(content, yaml.SafeLoader) for content in contents]
                for yml_content in yml_contents:
                    for image in self._find_helm_spec(yml_content, 'image'):
                        self._check_docker_image(f_name, stp, image[0], err_prefix=f'{image[1]} :: ')
        return True

    def _step_check_mypy_config(self) -> bool:
        mypy_config = os.path.join(os.getcwd(), MYPY_CONFIG)
        if not os.path.exists(mypy_config):
            return False

        config = configparser.ConfigParser()
        config.read(mypy_config)
        mypy_section = config['mypy']
        if not mypy_section:
            raise StepError(f'[mypy] section must be specified in {mypy_config}')

        # important_plugins = ['pydantic.mypy']
        # for plug in important_plugins:
        #     if plug not in mypy_section.get('plugins', '').lower():
        #         raise StepError(f'{arg_file_info(MYPY_CONFIG)} :: plugins must contains "{plug}"')
        if mypy_section.get('ignore_missing_imports', '').lower() != "false":
            raise StepError(f'{arg_file_info(MYPY_CONFIG)} :: ignore_missing_imports must be False. "{mypy_section["ignore_missing_imports"]}" was given')
        if mypy_section.get('follow_imports', '').lower() != "error":
            raise StepError(f'{arg_file_info(MYPY_CONFIG)} :: follow_imports must be error. "{mypy_section["follow_imports"]}" was given')
        # if mypy_section.get('follow_imports_for_stubs', '').lower() != "true":
        #     raise StepError(f'{arg_file_info(MYPY_CONFIG)} :: follow_imports_for_stubs must be True. "{mypy_section["follow_imports_for_stubs"]}" was given')

        return True

    @property
    def _ignored_packages(self) -> set[str]:
        res = {'wheel', 'setuptools'}
        for p in self.packages_ignored:
            res.add(p.strip().lower())
        return res

    @property
    def _packages_ignored_in_setup(self) -> set[str]:
        res = set()
        for p in self.packages_ignored_in_setup:
            res.add(p.strip().lower())
        return res

    def _step_check_pipfile(self, stp: Step) -> bool:
        err_pref = f'{arg_file_info(PIPFILE, line=1)} ::'
        pipfile = os.path.join(os.getcwd(), PIPFILE)
        pipfile_lock = os.path.join(os.getcwd(), PIPFILE_LOCK)

        if not os.path.exists(pipfile):
            raise StepError(f'{err_pref} must be specified')

        if not os.path.exists(pipfile_lock):
            raise StepError(f'{err_pref} was not locked. please make "pipenv install"')

        try:
            with open(pipfile_lock, 'rt') as f:
                pipfile_lock_cntnt: dict[str, Any] = json.load(f)
            ppfile = Pipfile.load(pipfile)
        except Exception as e:  # noqa: B902
            raise StepError(f'{err_pref} {e}')

        if len(ppfile.sources) == 0:
            raise StepError(f'{err_pref} has no sources')

        # valid_pypi_source = 'https://pypi.org/simple'
        # if ppfile.default_source.url != valid_pypi_source:
        #     stp.add_error_in_file(pipfile, f'has invalid default source url. must be "{valid_pypi_source}". {ppfile.default_source.url} was given')

        if not ppfile.default_source.verify_ssl:
            stp.add_error_in_file(pipfile, f'default source must be verified with ssl. please set "verify_ssl = true" for source "{ppfile.default_source.name}"')

        if ppfile.default_source.name != SOURCE_PYPI:
            stp.add_error_in_file(pipfile, f'default source must have name "{SOURCE_PYPI}". "{ppfile.default_source.name}" was given')

        for source in ppfile.sources:
            if SOURCE_NERO_GITLAB_HOST not in source.url:
                continue
            if source.name != SOURCE_NERO_GITLAB:
                stp.add_error_in_file(pipfile, f'please rename source "{FG_RED}{source.name}{NC}" to {SOURCE_NERO_GITLAB}')
            if source.url != SOURCE_NERO_GITLAB_URL:
                stp.add_error_in_file(pipfile, f'ALL GITLAB packages must be stored in one project. url must be "{SOURCE_NERO_GITLAB_URL}"')
            if source.verify_ssl:
                stp.add_error_in_file(pipfile, f'source "{source.name}" must have "verify_ssl = false"')

        if self.check_hooks:
            for command in {'test', 'lint'}:
                if ppfile.scripts.get(command, None) is None:
                    stp.add_error_in_file(pipfile, f'script "{FG_RED}{command}{NC}" is not specified')
                else:
                    if not ppfile.scripts[command].command:
                        stp.add_error_in_file(pipfile, f'script "{FG_RED}{command}{NC}" has empty command')

        setup_files, _1 = arg_file_glob_compile_files(self.setup_file_lists)

        main_setup_file_content = ''
        for sf in setup_files:
            if os.path.dirname(sf) == os.getcwd():
                with open(sf, 'rt') as f:
                    main_setup_file_content = f.read()
                break

        installed_packages = Pipfile.freeze()
        for pack in ppfile.all_packages.values():
            if pack.name in self._ignored_packages or not self.check_packages:
                continue

            assert pack.source is not None

            if pack.semver is None and pack.source.name == SOURCE_NERO_GITLAB:
                stp.add_error_in_file(
                    pipfile,
                    f'package "{FG_RED}{pack.name}{NC}" form "{SOURCE_NERO_GITLAB}" must have version with valid semver formant. '
                    f'IT IS THE RULE OF COMPANY. {pack.version} was given',
                )

            if pack.source.name == SOURCE_NERO_GITLAB:
                if pack.is_dev:
                    stp.add_error_in_file(pipfile, f'package "{FG_RED}{pack.name}{NC}" could not be in the dev-package!')

                if len(pack.available_versions) > 0:
                    msg = f'package "{FG_RED}{pack.name}{NC}" is not fresh. version={FG_RED}{pack.semver}{NC}. ' \
                        f'versions for upgrading: {", ".join(str(v) for v in pack.available_versions)}'

                    if pack.name == 'ulpytool':
                        stp.add_error(msg)
                    else:
                        stp.add_warn(msg)

            if pack.name not in installed_packages:
                stp.add_error_in_file(pipfile, f'package "{FG_RED}{pack.name}{NC}" not installed')

            if pack.is_dev:
                ps = pipfile_lock_cntnt['develop']
            else:
                ps = pipfile_lock_cntnt['default']
            if pack.name not in ps:
                stp.add_error_in_file(pipfile, f'package "{FG_RED}{pack.name}{NC}" not in lock. please make "pipenv install{" --dev" if pack.is_dev else ""}"')

            if main_setup_file_content and pack.name not in self._packages_ignored_in_setup and not pack.is_dev and pack.source.name != SOURCE_NERO_GITLAB:
                if pack.pip_representation not in main_setup_file_content and pack.pip_representation.replace('==', '>=') not in main_setup_file_content:
                    stp.add_error_in_file(pipfile, f'package "{FG_RED}{pack.pip_representation}{NC}" not in {arg_file_info(setup_files[0])}')
        return True

    def _chk_ymllinter(self, result: 'subprocess.CompletedProcess[bytes]') -> None:
        form_re = re.compile(r'^(.+?):(\d+):(\d+):\s+\[([^]]+)]\s+([^(]+)\(([^)]+)\)\s*$')
        errors: list[tuple[str, str, str, str, str, str]] = []
        max_len_of_file = 0
        for lc in result.stdout.decode().split('\n'):
            m = form_re.findall(lc.strip())
            for mr in m:
                if len(mr) == 6:
                    file, line, col, lvl, msg, code = mr
                    max_len_of_file = max(max_len_of_file, len(file))
                    errors.append(mr)
        for file, line, col, lvl, msg, code in errors:
            write_stdout(f'{arg_file_info(os.path.abspath(file), line=int(line), col=int(col)): <{max_len_of_file + 10}} :: {FG_RED}{lvl}{NC} :: {msg} :: {FG_GRAY}({code}){NC}')
        if len(errors) == 0 and result.returncode != 0:
            write_stdout(result.stdout.decode())
        result.check_returncode()

    def _check_init_files(self, py_files: list[str], stp: Step) -> None:
        uniq_init_files = set()
        cwd = os.path.abspath(os.getcwd())
        for f in py_files:
            d = os.path.dirname(f)
            if d != cwd:
                uniq_init_files.add(os.path.join(d, '__init__.py'))

        init_files, ignored_inits = arg_file_glob_compile_files([list(uniq_init_files)], self.py_init_dir_ignore_lists)
        for init in init_files:
            if not os.path.exists(init):
                stp.add_error_in_file(init, 'is not exists')
            elif not os.path.isfile(init):
                stp.add_error_in_file(init, 'is not a file')

        for init in init_files:
            if not os.path.exists(init):
                continue
            with open(init, 'rt') as init_f:
                if len(init_f.read().strip()) > 0:
                    stp.add_warn(f'init file "{init}" is not empty')

    def run(self) -> None:
        stepper = Stepper()

        with stepper.step('CHECK PYTHON VERSION'):
            self._step_check_python_version()

        has_py_files = self._check_py_files(stepper)

        with stepper.step('CHECK HOOKS', print_error=True) as stp:
            if not self._step_check_hooks():
                stp.skip()

        yml_files, ignored_yml_files = arg_file_glob_compile_files(self.yml_file_lists, self.yml_file_ignored_lists)
        with stepper.step('CHECK YAML FILES') as stp:
            if len(yml_files) == 0:
                stp.skip()
            else:
                arg_files_print(self.print_files, yml_files, ignored_files=ignored_yml_files)
                stp.run_cmd([
                    'yamllint',
                    '--config-file', os.path.join(THIS_LIB_PATH, 'conf', 'yamlint.yml'),
                    '--format', 'parsable',
                    '--strict',
                    *yml_files,
                ], chk=self._chk_ymllinter, print_std=False)

        with stepper.step('CHECK HELM-TEMPLATES') as stp:
            if not self.check_helm(stp):
                stp.skip()

        with stepper.step('CHECK PIPFILE') as stp:
            if not self._step_check_pipfile(stp):
                stp.skip()

        with stepper.step('CHECK DOCKER COMPOSE FILES') as stp:
            if not self._step_check_docker_compose_files(stp):
                stp.skip()

        with stepper.step('CHECK SETUP FILES') as stp:
            if not self._step_check_setup_files():
                stp.skip()

        with stepper.step('CHECK gitignore') as stp:
            if not self._step_check_gitignore():
                stp.skip()

        with stepper.step('CHECK DOCKERFILES') as stp:
            if not self._step_check_dockerfiles(stp):
                stp.skip()

        if not has_py_files:
            raise StepError('no python files found for linting')

    def _check_py_files(self, stepper: Stepper) -> bool:
        py_files, ignored_files = arg_file_glob_compile_files(self.py_file_lists, self.py_file_ignore_lists)
        write_stdout('')
        arg_files_print(self.print_files, py_files, ignored_files=ignored_files, name='python files')

        local_mypy_conf = os.path.join(os.getcwd(), 'mypy.ini')
        mypy_conf = local_mypy_conf if os.path.isfile(local_mypy_conf) else os.path.join(THIS_LIB_PATH, "conf", "mypy.ini")

        with stepper.step('CHECK __init__.py FILES') as stp:
            if not len(py_files):
                stp.skip()
            else:
                self._check_init_files(py_files, stp)

        with stepper.step('TYPE IGNORE FILES') as stp:
            if not len(py_files):
                stp.skip()
            else:
                self._check_type_ignore_file(py_files)

        with stepper.step('CHECK MYPY CONFIG') as stp:
            if not len(py_files):
                stp.skip()
            else:
                if not self._step_check_mypy_config():
                    stp.skip()

        with stepper.step('MYPY') as stp:
            if not len(py_files):
                stp.skip()
            else:
                stp.run_cmd([
                    'mypy',
                    '--follow-imports=normal',
                    f'--config-file={mypy_conf}',
                    '--namespace-packages',
                    '--explicit-package-bases',
                    *py_files,
                ])

        with stepper.step('LINTING RUFF') as stp:
            if not len(py_files):
                stp.skip()
            else:
                stp.run_cmd([
                    'ruff',
                    'check',
                    *(('--fix', ) if self.fix else tuple()),
                    '--cache-dir',
                    os.path.join(os.getcwd(), ".tmp", "ruff_cache"),
                    f'--line-length={MAX_LINE_LEN}',
                    *py_files,
                ])

        with stepper.step('LINT IMPORTS') as stp:
            if not len(py_files):
                stp.skip()
            else:
                if not self.check_imports:
                    stp.skip()
                elif not self._check_imports(py_files):
                    stp.skip()

        return bool(py_files)
