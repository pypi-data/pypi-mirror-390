import argparse
import os

import yaml
from deepdiff import DeepDiff  # type: ignore
from pydantic import Field

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.commands.conf import HELM_ERROR__NOT_FOUND
from ul_py_tool.utils.arg_str2yaml import arg_str2yaml
from ul_py_tool.utils.aseembly import AssemblyFile, AssemblyTarget
from ul_py_tool.utils.colors import FG_GREEN, FG_RED, NC
from ul_py_tool.utils.run_command import run_command
from ul_py_tool.utils.step import Stepper


class CmdTestSecrets(Cmd):
    release_environment: str
    assembly_file: AssemblyFile
    assembly_targets: list[AssemblyTarget] = Field(default_factory=list)

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--release-environment', dest='release_environment', type=str, required=True)
        parser.add_argument('--assembly-file', dest='assembly_file', type=arg_str2yaml, required=True, default='assembly.yaml')

    def run(self) -> None:
        stepper = Stepper()
        cwd = os.getcwd()

        with stepper.step(f'{FG_GREEN}check if target exists{NC}'):
            self.assembly_targets = [at for at in self.assembly_file.targets.values() if at.environment == self.release_environment]

        with stepper.step(f'{FG_GREEN}check secrets{NC}') as stp:
            for component_name in self.assembly_file.components.keys():
                for at in self.assembly_targets:
                    values_dir = os.path.join(cwd, 'secrets', component_name, f'{at.cluster_name}:{at.environment}')
                    if not os.path.exists(os.path.join(values_dir, 'secret-values.yaml')):
                        stp.add_error(f'{FG_RED}for {component_name} secrets not found in {values_dir}{NC}')
                    if not os.path.exists(os.path.join(values_dir, 'values.yaml')):
                        stp.add_error(f'{FG_RED}for {component_name} deploy values not found in {values_dir}{NC}')

        with stepper.step(f'{FG_GREEN}init required repositories{NC}'):
            for component in self.assembly_file.components.values():
                os.makedirs(os.path.join(cwd, component.directory), exist_ok=False)
                run_command([f'git clone  --depth 1 --branch {component.tag} {component.repository} .'], cwd=os.path.join(cwd, component.directory))
                run_command(['git submodule sync --recursive && git submodule update --init --recursive'], cwd=os.path.join(cwd, component.directory))

        with stepper.step(f'{FG_GREEN}check values and secrets data{NC}') as stp:
            ''' format of DeepDiff output looks like:
            {
              'dictionary_item_added': [root['broker'], root['db'], root['dockerconfig'], root['systemconfig'], root['pii_keys']],
              'dictionary_item_removed': [root['endpoints']]
            }
            or just {} if no diff in keys
            where dictionary_item_added - keys that are not presented  in first dict(yaml)(dev-values/dev-secret-values.yaml)
            and dictionary_item_removed - keys that are presented in first dict(yaml)(dev-values/dev-secret-values.yaml) but missing in second (target)
            '''
            for component_name, component_config in self.assembly_file.components.items():
                for at in self.assembly_targets:
                    values_dir = os.path.join(cwd, 'secrets', component_name, f'{at.cluster_name}:{at.environment}')

                    with open(os.path.join(cwd, component_config.directory, '.helm/dev-values.yaml'), 'r') as f:
                        dev_v = yaml.safe_load(f)

                    with open(os.path.join(values_dir, "values.yaml"), 'r') as f:
                        target_v = yaml.safe_load(f)
                    ddiff = DeepDiff(dev_v, target_v, ignore_order=True)
                    ddiff.pop('values_changed', None)
                    if ddiff:
                        stp.add_error(f'{FG_RED}for {component_name} deploy values have missing or extra keys in values:{NC}\n {ddiff}')

                    with open(os.path.join(cwd, component_config.directory, '.helm/dev-secret-values.yaml'), 'r') as f:
                        dev_secret_v = yaml.safe_load(f)

                    with open(os.path.join(values_dir, "secret-values.yaml"), 'r') as f:
                        target_secret_v = yaml.safe_load(f)
                    ddiff = DeepDiff(dev_secret_v, target_secret_v, ignore_order=True)
                    ddiff.pop('values_changed', None)
                    if ddiff:
                        stp.add_error(f'{FG_RED}for {component_name} deploy values have missing or extra keys in secret values:{NC}\n {ddiff}')

                    # test if helm chart exists to avoid "oops we deployed but it crashed on last step because bad package and no new features
                    helm_chart = run_command(
                        [
                            f'helm search repo {component_config.helm_repo_name}/{component_config.helm_chart_name} --version {component_config.helm_chart_version}',
                        ],
                    ).stdout
                    if helm_chart == HELM_ERROR__NOT_FOUND:
                        raise NotImplementedError(
                            f'{component_config.helm_chart_name} chart '
                            f'at local or remote repo {component_config.helm_repo_name} '
                            f'of version {component_config.helm_chart_version} was not found',
                        )
