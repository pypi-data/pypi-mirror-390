import os

from ul_py_tool.utils.write_stdout import write_stdout


def copy_if_destination_is_absent(fp_from: str, fp_to: str, replace: bool = False) -> None:
    assert os.path.isfile(fp_from)
    if replace or not os.path.isfile(fp_to):
        os.makedirs(os.path.dirname(fp_to), exist_ok=True)
        with open(fp_from, 'rt') as f_from, open(fp_to, 'wt+') as f_to:
            f_to.writelines(f_from.readlines())
        write_stdout(f'file "{fp_to}" created')
