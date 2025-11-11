import argparse
import os
import shutil

import yaml
from deepdiff import DeepDiff  # type: ignore

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.utils.arg_str2yaml import arg_str2yaml
from ul_py_tool.utils.aseembly import AssemblyFile, AssemblyTarget
from ul_py_tool.utils.colors import FG_GREEN, FG_RED, NC
from ul_py_tool.utils.docker_compose import DockerComposeFile
from ul_py_tool.utils.run_command import run_command
from ul_py_tool.utils.step import Stepper


class CmdReleaseDcf(Cmd):
    release_target: str
    assembly_file: AssemblyFile
    assembly_target: AssemblyTarget | None = None

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--release-target', dest='release_target', type=str, required=True)
        parser.add_argument('--assembly-file', dest='assembly_file', type=arg_str2yaml, required=True, default='assembly.yaml')

    def run(self) -> None:
        stepper = Stepper()
        cwd = os.getcwd()

        with stepper.step(f'{FG_GREEN}check if target exists{NC}'):
            if self.release_target not in self.assembly_file.targets.keys():
                raise argparse.ArgumentTypeError(f'{FG_RED}Target not found in assembly file{NC}')
            self.assembly_target = self.assembly_file.targets[self.release_target]

        with stepper.step(f'{FG_GREEN}check secrets{NC}') as stp:
            for component_name in self.assembly_file.components.keys():
                values_dir = os.path.join(cwd, 'secrets', component_name, f'{self.assembly_target.cluster_name}:{self.assembly_target.environment}')
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
                values_dir = os.path.join(cwd, 'secrets', component_name, f'{self.assembly_target.cluster_name}:{self.assembly_target.environment}')

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

        with stepper.step(f'{FG_GREEN}release{NC}'):
            # to store releases that completed
            for component_name, component_config in self.assembly_file.components.items():
                values_dir = os.path.join(cwd, 'secrets', component_name, f'{self.assembly_target.cluster_name}:{self.assembly_target.environment}')
                component_directory = os.path.join(cwd, component_config.directory)
                release_name = f'{component_name}-{self.assembly_target.environment}'
                # download helm chart
                run_command(
                    [
                        f'helm pull {component_config.helm_repo_name}/{component_config.helm_chart_name} --untar --version {component_config.helm_chart_version}',
                    ],
                    cwd=component_directory,
                )
                if not os.path.exists(os.path.join(cwd, component_config.directory, '.helm/templates')):
                    shutil.copytree(
                        os.path.join(cwd, component_config.directory, f"{component_config.helm_chart_name}/templates"),
                        os.path.join(cwd, component_config.directory, '.helm/templates'),
                    )
                shutil.copy(os.path.join(values_dir, "secret-values.yaml"), component_directory)
                shutil.copy(os.path.join(values_dir, "values.yaml"), component_directory)
                shutil.copy(os.path.join(cwd, component_config.directory, '.helm/charts.yaml'), component_directory)
                enc_key = os.environ[self.assembly_target.encryption_key_name]
                run_command(
                    [
                        f'git add . '
                        f'&& export RELEASE_TAG={component_config.tag} '
                        f'&& export WERF_SECRET_KEY={enc_key} '
                        f'&& export WERF_ENV={self.assembly_target.environment} '
                        f'&& werf render --config=werf-release.yaml  --namespace={release_name} --values=values.yaml  --values=charts.yaml --secret-values=secret-values.yaml --loose-giterminism=True > kubernetes-objects.yaml',
                    ],
                    cwd=component_directory,
                    silent=False,
                )
                with open(os.path.join(component_directory, "kubernetes-objects.yaml"), "r") as fr:
                    dcf = DockerComposeFile.from_kubernetes(yaml.load_all(fr, yaml.FullLoader))
                final_file = dcf.to_json()
                with open(f"docker-compose.{component_name}.release.yaml", "w") as fw:
                    yaml.dump(final_file, fw)
