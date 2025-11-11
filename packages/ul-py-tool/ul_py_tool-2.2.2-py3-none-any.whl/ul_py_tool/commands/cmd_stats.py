import argparse

from ul_py_tool.commands.cmd import Cmd
from ul_py_tool.utils.arg_files_glob import arg_files_glob, arg_file_glob_compile_files, arg_files_print
from ul_py_tool.utils.colors import FG_YELLOW, NC
from ul_py_tool.utils.write_stdout import write_stdout


class CmdStats(Cmd):
    print_files: int
    file_lists: list[list[str]]
    file_ignore_lists: list[list[str]]

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        finder = arg_files_glob(ignore_absent=True)
        parser.add_argument('--print-files', dest='print_files', type=int, required=False, default=10)
        parser.add_argument('--files', dest='file_lists', nargs='+', type=finder, required=False, default=[
            finder('*'),
            finder('**/*'),
        ])
        parser.add_argument('--ignore', dest='file_ignore_lists', nargs='+', type=finder, required=False, default=[])

    def run(self) -> None:
        py_files, ignored_files = arg_file_glob_compile_files(self.file_lists, self.file_ignore_lists)
        arg_files_print(self.print_files, py_files, ignored_files=ignored_files, name='files to count', ide_col_suf=False)

        write_stdout('\n')

        stats_by_type: dict[str, list[tuple[str, int, int]]] = dict()
        max_pf = 0
        max_pf_t = 0
        for pf in py_files:
            max_pf = max(len(pf), max_pf)
            try:
                with open(pf, 'rt') as f:
                    this_file_count_not_empty_lines = 0
                    this_file_count_lines = 0
                    for line in f.readlines():
                        this_file_count_lines += 1
                        if len(line.strip()) > 0:
                            this_file_count_not_empty_lines += 1
                    pft = pf.split('/')[-1].split('.')[-1]
                    max_pf_t = max(len(pft), max_pf_t)
                    if pft not in stats_by_type:
                        stats_by_type[pft] = []
                    stats_by_type[pft].append((pf, this_file_count_lines, this_file_count_not_empty_lines))
            except UnicodeDecodeError:
                continue

        count_lines = 0
        count_not_empty_lines = 0
        for type, stats in stats_by_type.items():
            t_count_lines = 0
            t_count_not_empty_lines = 0
            for _file_path, count, non_empty_count in stats:
                count_not_empty_lines += non_empty_count
                count_lines += count
                t_count_not_empty_lines += non_empty_count
                t_count_lines += count
                # write_stdout(f'{arg_file_info(file_path, ide_col_suf=True, rel_path=True): <{max_pf + 10:}} = {FG_YELLOW}{non_empty_count: >4}{NC} / {count: <4} lines')
            write_stdout(f'{len(stats): >4} *.{type: <{max_pf_t}} files has {FG_YELLOW}{t_count_not_empty_lines}{NC} / {t_count_lines} lines')
        write_stdout(f'{"=" * 80}\nsummary: {len(py_files)} files has {FG_YELLOW}{count_not_empty_lines}{NC} / {count_lines} lines\n')


def test_example() -> None:
    assert 1 == 1
