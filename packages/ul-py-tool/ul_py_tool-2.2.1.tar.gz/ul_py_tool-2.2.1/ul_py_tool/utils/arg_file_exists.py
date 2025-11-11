import os.path
from argparse import ArgumentTypeError


def arg_file_exists(value: str) -> str:
    if os.path.exists(value):
        return value
    new_val = os.path.join(os.getcwd(), value)
    if os.path.exists(new_val):
        return new_val
    raise ArgumentTypeError(f'file "{value}" was not found')
