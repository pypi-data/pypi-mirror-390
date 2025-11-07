import subprocess
from .args import get_args
from .steps import build, upload, git_tag, update_version, git_commit


def main():
    args = get_args()
    version = update_version()
    if args.build:
        build()
        if args.upload:
            upload(version)

    if args.git_commit:
        git_commit(version)

    if args.git_tag:
        git_tag(version)

    if args.git_push:
        result = subprocess.run(
            ["git", "remote"], capture_output=True, text=True, check=True
        )
        remotes = result.stdout.strip().split("\n")
        for remote in remotes:
            print(f"Pushing to remote: {remote}")
            subprocess.run(["git", "push", remote], check=True)
            if args.git_tag:
                print(f"Pushing tags to remote: {remote}")
                subprocess.run(["git", "push", remote, "--tags"], check=True)


if __name__ == "__main__":
    main()
