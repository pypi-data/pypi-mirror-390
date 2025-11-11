import argparse
import os
from glob import glob
from urllib.parse import urlparse, ParseResult

import gitlab
import requests

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.utils.arg_str2bool import arg_str2bool
from ul_py_tool.utils.arg_str2list import arg_str2list
from ul_py_tool.utils.docker_file import DockerFile
from ul_py_tool.utils.run_command import run_command
from ul_py_tool.utils.step import Stepper


class CmdBuildImages(Cmd):
    silent: bool
    push: bool
    registry: str
    images_dir: str
    project_id: int
    api_token: str
    image_version: str
    build_dir: str
    build_args: list[str]
    gitlab: bool

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--registry', required=False, default="", type=str)
        parser.add_argument('--images-dir', required=False, default="", type=str)
        parser.add_argument('--silent', required=False, default=False, type=arg_str2bool)
        parser.add_argument('--push', required=False, default=False, type=arg_str2bool)
        parser.add_argument('--project_id', required=False, default="", type=int)
        parser.add_argument('--api-token', required=False, default="", type=str)
        parser.add_argument('--image-version', required=False, default="", type=str)
        parser.add_argument('--build-dir', required=False, default="", type=str)
        parser.add_argument('--build-args', required=False, default=[], type=arg_str2list)
        parser.add_argument('--gitlab', required=False, default=True, type=arg_str2bool)

    @staticmethod
    def _remove_prefix(text: str, prefix: str) -> str:
        if prefix and text.startswith(prefix):
            return text[len(prefix):]
        return text

    @staticmethod
    def _remove_suffix(text: str, suffix: str) -> str:
        if suffix and text.endswith(suffix):
            return text[:-len(suffix)]
        return text

    @staticmethod
    def _remove_port(text: str) -> str:
        if ':' in text:
            text_without_port = text.split(':')
            return text_without_port[0]
        return text

    @staticmethod
    def _get_gitlab_repository_urls(url: str, project_id: int, registry_url_path: str, registry_url_parsed: ParseResult, token: str) -> set[str]:
        gl = gitlab.Gitlab(url, private_token=token)
        gl.auth()
        project = gl.projects.get(project_id)
        image_repositories = project.repositories.list()
        return {f'{registry_url_parsed.netloc}/{registry_url_path}/{image_repository.name}:{tag.name}'
                for image_repository in image_repositories for tag in image_repository.tags.list()}

    def run(self) -> None:
        stepper = Stepper()

        with stepper.step('prepare variables for build and push'):
            registry_url_parsed = urlparse(self.registry)
            if len(str(registry_url_parsed.scheme)):
                registry_url_parsed = urlparse(f'https://{self.registry}')

            registry_url_path = self._remove_suffix(self._remove_prefix(str(registry_url_parsed.path), "/"), "/")

            url = f'https://{self._remove_port(registry_url_parsed.netloc)}'
            if self.gitlab:
                image_repository_urls = self._get_gitlab_repository_urls(url, self.project_id, registry_url_path, registry_url_parsed, self.api_token)
            else:
                image_repository_urls = set()
                repositories = requests.get(
                    f"https://hub.docker.com/v2/repositories/{registry_url_path}/?page_size=1000").json()
                for r in repositories['results']:
                    tags = requests.get(
                        f"https://hub.docker.com/v2/repositories/{registry_url_path}/{r['name']}/tags/?page_size=1000").json()
                    for t in tags['results']:
                        image_repository_urls.add(f"{registry_url_path}/{r['name']}:{t['name']}")

        with stepper.step('build and push target images'):
            if not self.gitlab:
                run_command([f"docker login -u {registry_url_path} -p {self.api_token}"], silent=True)
            for image_dir in glob(os.path.join(self.images_dir, "*"), recursive=False):
                if not os.path.isdir(image_dir):
                    continue

                image_version_file = os.path.join(image_dir, "version.txt")
                image_file = os.path.join(image_dir, "Dockerfile")
                image_name = os.path.basename(image_dir)
                if not self.image_version:
                    with open(image_version_file, "rt") as f:
                        self.image_version = "".join(f.readlines()).strip()

                if self.gitlab:
                    image_url = f'{registry_url_parsed.netloc}/{registry_url_path}/{image_name}:{self.image_version}'
                else:
                    image_url = f'{registry_url_path}/{image_name}:{self.image_version}'

                if image_url in image_repository_urls:
                    continue
                else:
                    df = DockerFile.load_file(image_file, image_name)
                    df.build(image_url, self.build_args, self.build_dir).display(disable=self.silent)

                    if self.push:
                        df.push(image_url)
