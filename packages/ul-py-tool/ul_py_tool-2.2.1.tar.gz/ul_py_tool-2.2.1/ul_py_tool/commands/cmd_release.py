import argparse
import os
import shutil
import time

import yaml
from deepdiff import DeepDiff  # type: ignore
from kubernetes import client, config  # type: ignore

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.commands.conf import HELM_ERROR__NOT_FOUND, KUEBERNETES_SLEEP_TIME
from ul_py_tool.utils.arg_str2yaml import arg_str2yaml
from ul_py_tool.utils.aseembly import AssemblyFile, AssemblyTarget
from ul_py_tool.utils.colors import FG_GREEN, FG_RED, NC
from ul_py_tool.utils.run_command import run_command
from ul_py_tool.utils.step import Stepper
from ul_py_tool.utils.write_stdout import write_stdout


class CmdRelease(Cmd):
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

        with stepper.step(f'{FG_GREEN}check values{NC}') as stp:
            for component_name in self.assembly_file.components.keys():
                values_dir = os.path.join(
                    cwd,
                    'secrets',
                    component_name,
                    f'{self.assembly_target.cluster_name}:{self.assembly_target.environment}'
                )
                if not os.path.exists(os.path.join(values_dir, 'values.yaml')):
                    stp.add_error(f'{FG_RED}for {component_name} deploy values not found in {values_dir}{NC}')

        with stepper.step(f'{FG_GREEN}init required repositories{NC}'):
            for component in self.assembly_file.components.values():
                os.makedirs(os.path.join(cwd, component.directory), exist_ok=False)
                run_command([f'git clone  --depth 1 --branch {component.tag} {component.repository} .'], cwd=os.path.join(cwd, component.directory))
                run_command(['git submodule sync --recursive && git submodule update --init --recursive'], cwd=os.path.join(cwd, component.directory))

        with stepper.step(f'{FG_GREEN}check chart version data{NC}') as stp:
            for component_name, component_config in self.assembly_file.components.items():
                helm_chart = run_command(
                    [
                        f'helm search repo {component_config.helm_repo_name}/{component_config.helm_chart_name} '
                        f'--version {component_config.helm_chart_version}',
                    ],
                ).stdout
                if helm_chart == HELM_ERROR__NOT_FOUND:
                    raise NotImplementedError(
                        f'{component_config.helm_chart_name} chart '
                        f'at local or remote repo {component_config.helm_repo_name} '
                        f'of version {component_config.helm_chart_version} was not found',
                    )

        with stepper.step(f'{FG_GREEN}release{NC}'):
            # to store releases that completed
            releases: dict[str, str] = {}
            kubeconfig_file_path = os.path.join(cwd, self.assembly_target.kubeconfig_file)
            config.load_kube_config(config_file=kubeconfig_file_path)
            kubernetes_client = client.AppsV1Api()
            for component_name, component_config in self.assembly_file.components.items():
                values_dir = os.path.join(cwd, 'secrets', component_name, f'{self.assembly_target.cluster_name}:{self.assembly_target.environment}')
                component_directory = os.path.join(cwd, component_config.directory)
                release_name = f'{component_name}-{self.assembly_target.environment}'

                # get list of all up-to-date releases
                list_deployments = kubernetes_client.list_namespaced_deployment(
                    namespace=release_name,
                ).items

                # collect all unique labels (after 1.1.26 ul-py-tool they are compulsory, bot now not)
                set_charts_versions = set()
                set_service_versions = set()
                set_deployment_names = set()
                for deployment in list_deployments:
                    set_charts_versions.add(deployment.metadata.labels.get('release/chart-version', None))
                    set_service_versions.add(deployment.metadata.labels.get('release/component-version', None))
                    set_deployment_names.add(deployment.metadata.name)

                if len(set_charts_versions) > 1 or len(set_service_versions) > 1:
                    raise Exception('oops, something went wrong during previous deployment. Required human review')

                if not self.assembly_target.recreate:
                    if component_config.tag in set_service_versions and component_config.helm_chart_version in set_charts_versions:
                        write_stdout(f'Service {release_name} with version {component_config.tag} already released')
                        write_stdout(f'Service {release_name} resources were crated by chart version {component_config.helm_chart_version}')
                        continue

                # get current release version, to rollback in case of
                # every success deployment creates new release from helm perspective,
                # even if nothing has changed (because of migration command)
                last_version = run_command(
                    [
                        f"helm history {release_name} "
                        f"-n {release_name} "
                        f"--kubeconfig {kubeconfig_file_path} "
                        "| tail -n1 "
                        "| awk '{print $1}' ",
                    ],
                    cwd=component_directory,
                ).stdout

                # some low-resource kbnodes have problems with correct deploy process. Its probably easier to stop all
                # pods, and then recreate them.
                if component_config.force_disable:
                    for deployment in list_deployments:
                        kubernetes_client.patch_namespaced_deployment_scale(
                            name=deployment.metadata.name,
                            namespace=deployment.metadata.namespace,
                            body={'spec': {'replicas': 0}},
                        )
                    time.sleep(KUEBERNETES_SLEEP_TIME)

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
                    shutil.copy(  # We copy this to have more detail info in helm history
                        os.path.join(cwd, component_config.directory, f"{component_config.helm_chart_name}/Chart.yaml"),
                        os.path.join(cwd, component_config.directory, '.helm/Chart.yaml'),
                    )
                shutil.copy(os.path.join(values_dir, "values.yaml"), component_directory)
                shutil.copy(os.path.join(cwd, component_config.directory, '.helm/charts.yaml'), component_directory)
                enc_key = os.environ[self.assembly_target.encryption_key_name]
                deploy_result = run_command(
                    [
                        f'git add . '
                        f'&& export RELEASE_TAG={component_config.tag} '
                        f'&& export WERF_SECRET_KEY={enc_key} '
                        f'&& export WERF_ENV={self.assembly_target.environment} '
                        f'&& werf converge --config=werf-release.yaml --kube-config {kubeconfig_file_path} --namespace={release_name} --values=values.yaml  --values=charts.yaml --set=component_version={component_config.tag} --auto-rollback=true --loose-giterminism=True --dev=True'  # noqa
                    ],
                    cwd=component_directory,
                    ignore_errors=True,
                )
                if deploy_result.code != 0:
                    for release, version in releases.items():
                        # rollback all successful releases
                        run_command([
                            f'werf helm rollback {release} -n {release} {version} --kube-config {kubeconfig_file_path}',
                        ])
                    raise Exception(f'Deploy of {release_name} version {component_config.tag} failed due to some deploy problems. All deployed services were rollbacked')
                releases[release_name] = str(last_version).strip('\n')  # because run_command adds \n and i have no idea hpw to disable it
