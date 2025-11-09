import platform

import PySide6  # type: ignore  # noqa: PGH003


def main() -> None:
    print("Hello from ex05-pyside6-py310!")  # noqa: T201
    print(f"Current python ver: {platform.python_version()}")  # noqa: T201
    print(f"Pyside2 version: {PySide6.__version__}")  # noqa: T201
