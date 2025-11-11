import re
from typing import NamedTuple

from ul_py_tool.utils.run_command import CommandResult, run_command

FROM_RE = re.compile(r'^FROM\s+(?P<image>[^\s]+)(?:\s+as\s+(?P<label>[^\s]+))?$')


class DockerFile(NamedTuple):
    lines: list[str]
    images: dict[str, str]  # label => image with version
    file_path: str | None = None

    def ensure_image(self, label: str = '') -> str:
        return self.images[label]

    @staticmethod
    def load_image(image: str) -> 'DockerFile':
        assert isinstance(image, str)
        return DockerFile(
            file_path=None,
            lines=[],
            images={
                '': image,
            },
        )

    def push(self, full_url: str, silent: bool = False) -> CommandResult:
        return run_command([f'docker push {full_url}'], silent=silent)

    def build(self, full_url: str, build_args: list[str], build_dir: str = '.', silent: bool = False) -> CommandResult:
        build_args_str = f"--build-arg {' --build-arg '.join(build_args)}" if len(build_args) else ""
        return run_command([f"docker build -f {self.file_path} -t {full_url} {build_dir} {build_args_str}"], silent=silent)

    @staticmethod
    def load_file(docker_file_path: str, image_name: str = '') -> 'DockerFile':
        images = dict()
        images[''] = image_name
        lines: list[str] = []

        with open(docker_file_path, 'rt') as dockery:
            for line in dockery:
                if FROM_RE.match(line):
                    groups_r = FROM_RE.search(line)
                    assert groups_r is not None
                    groups = groups_r.groupdict()
                    images[groups.get('label', '')] = groups['image']

        return DockerFile(
            file_path=docker_file_path,
            lines=lines,
            images=images,
        )
