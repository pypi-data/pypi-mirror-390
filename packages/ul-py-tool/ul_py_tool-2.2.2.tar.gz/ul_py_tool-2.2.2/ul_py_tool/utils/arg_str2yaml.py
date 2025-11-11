import argparse
import os

import yaml

from ul_py_tool.utils.aseembly import AssemblyFile


def arg_str2yaml(value: str | int | bool) -> AssemblyFile:
    if not isinstance(value, str):
        raise argparse.ArgumentTypeError('invalid type')
    file_path = value
    if not value.startswith('/'):
        file_path = os.path.join(os.getcwd(), value)
    if not os.path.isfile(file_path):
        raise argparse.ArgumentTypeError(f'File {file_path} not found')
    with open(file_path, 'r') as f:
        assembly = yaml.safe_load(f)

    return AssemblyFile(**assembly)
