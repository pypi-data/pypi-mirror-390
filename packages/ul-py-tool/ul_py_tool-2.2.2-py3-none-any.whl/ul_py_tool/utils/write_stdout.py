from typing import Any


def write_stdout(*args: Any, **kwargs: Any) -> None:
    print(*args, **kwargs)  # noqa
