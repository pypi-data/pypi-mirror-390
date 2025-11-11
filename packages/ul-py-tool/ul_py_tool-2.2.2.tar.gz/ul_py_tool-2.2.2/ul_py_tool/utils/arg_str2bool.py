import argparse


def arg_str2bool(value: str | int | bool) -> bool:
    if isinstance(value, str):
        return value.lower() not in {'0', 'false', '', 'no'}

    if isinstance(value, int):
        return bool(value)

    if isinstance(value, bool):  # type: ignore
        return value

    raise argparse.ArgumentTypeError('invalid type')
