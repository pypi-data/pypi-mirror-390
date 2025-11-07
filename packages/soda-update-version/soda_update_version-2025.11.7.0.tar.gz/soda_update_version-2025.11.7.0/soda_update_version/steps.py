import subprocess
from .version import update_version  # noqa: F401
import sys

"steps to perform"


def build():
    subprocess.run(["uv", "build"], check=True)


def upload(version: str):
    subprocess.run(
        [
            sys.executable,
            "-m",
            "twine",
            "upload",
            "--repository",
            "pypi",
            f"./dist/*-{version}.*",
            f"./dist/*-{version}-*",
        ],
        check=True,
    )


def git_tag(version: str):
    subprocess.run(["git", "tag", version], check=True)


def git_commit(version: str):
    # git_stat = subprocess.getoutput("git status")
    # if not "working tree clean" in git_stat:
    #     print("please commit your changes first")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"bump version to {version}"])
