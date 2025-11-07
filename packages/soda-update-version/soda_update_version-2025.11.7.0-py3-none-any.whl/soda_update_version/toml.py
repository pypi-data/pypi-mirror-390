from pathlib import Path

"""get project toml"""


def get_project_toml() -> Path:
    import os

    cwd = Path(os.getcwd())
    if not cwd.joinpath("pyproject.toml").exists():
        print("cannot find pyproject.toml")
        exit(-1)
    return cwd.joinpath("pyproject.toml")
