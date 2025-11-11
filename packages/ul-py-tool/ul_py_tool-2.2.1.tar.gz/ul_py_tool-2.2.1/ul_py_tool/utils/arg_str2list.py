import argparse

from ul_py_tool.utils.write_stdout import write_stdout


def arg_str2list(value: str) -> list[str]:  # Because we process dict of KeyValue
    if not isinstance(value, str):
        raise argparse.ArgumentTypeError('invalid type')  # because required to be key=value,key=...
    res = []
    kv_list = value.split(",")
    for kv in kv_list:
        if not kv:
            continue  # ignore if something went wrong and we got like a=b,,,,,,
        split_kv = kv.split("=")
        if len(split_kv) != 2:
            write_stdout(f'cant process {kv} kv, skipping...')  # same as above but a====b and etc.
            continue
        if not split_kv[1]:
            write_stdout(f'No value was provided for {split_kv[0]}, skipping...')
            continue
        res.append(kv)
    return res
