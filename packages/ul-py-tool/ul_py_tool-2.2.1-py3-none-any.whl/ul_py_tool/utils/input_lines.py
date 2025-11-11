from ul_py_tool.utils.write_stdout import write_stdout


def input_lines(name: str) -> list[str]:
    logs = []
    write_stdout(f'Please add {name} (leave empty if don\'t)')
    while True:
        text = input(': ')
        if not text:
            break
        logs.append(text)
    return logs
