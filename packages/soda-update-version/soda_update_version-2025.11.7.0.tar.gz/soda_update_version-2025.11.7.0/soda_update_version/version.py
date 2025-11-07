from pathlib import Path
import datetime
import tomli as tomllib


def get_version(project_toml: Path) -> list[int]:
    """
    从 toml 文件中获取版本号。
    如果版本号不存在或格式不正确，则返回基于当前日期的新版本号。
    """
    try:
        with project_toml.open("rb") as f:
            data = tomllib.load(f)
        version_str = data["project"]["version"]
        # 检查版本号格式是否为 x.x.x.x
        if version_str.count(".") != 3:
            raise ValueError("版本号必须有4个部分")
        # 将版本号的每个部分转换为整数
        parts = [int(p) for p in version_str.split(".")]
        return parts
    except (KeyError, ValueError, FileNotFoundError):
        # 如果找不到版本或格式错误，则使用当前日期作为新版本
        print("未找到有效版本号或格式不正确，将使用当前日期生成新版本。")
        now = datetime.datetime.now()
        return [now.year, now.month, now.day, 0]


def next_version(version: list[int]) -> list[int]:
    """
    根据当前版本和日期生成下一个版本号。
    如果日期与版本中的日期相同，则修订号加1。
    如果日期不同，则使用当前日期，修订号重置为0。
    """
    year, month, day, rev = version
    now = datetime.datetime.now()
    # 检查版本中的日期是否是今天
    if year == now.year and month == now.month and day == now.day:
        # 如果是今天，修订号加1
        return [year, month, day, rev + 1]
    else:
        # 如果不是今天，使用当前日期，修订号为0
        return [now.year, now.month, now.day, 0]


def str_version(version: list[int]) -> str:
    """将列表形式的版本号转换为字符串。"""
    return ".".join(map(str, version))


def update_version() -> str:
    """
    更新 toml 文件中的版本号。
    """
    from .toml import get_project_toml

    project_toml = get_project_toml()
    # 获取当前版本
    version = get_version(project_toml)
    # 获取下一个版本
    nextv = next_version(version)

    # 将新旧版本转换为字符串
    old_version_str = str_version(version)
    new_version_str = str_version(nextv)

    # 准备要替换的整行内容，以避免错误替换
    old_line = f'version = "{old_version_str}"'
    new_line = f'version = "{new_version_str}"'

    content = project_toml.read_text(encoding="utf8")
    # 仅替换第一个匹配的行
    new_content = content.replace(old_line, new_line, 1)

    # 如果内容没有变化（例如，当找不到旧版本行时），则不写入文件
    if content != new_content:
        project_toml.write_text(encoding="utf8", data=new_content)
    else:
        # 如果旧版本行未找到，可能是因为格式错误导致 get_version 返回了新日期
        # 在这种情况下，我们仍然需要更新文件
        content_lines = content.splitlines()
        for i, line in enumerate(content_lines):
            if line.strip().startswith("version ="):
                content_lines[i] = new_line
                new_content = "\n".join(content_lines)
                project_toml.write_text(encoding="utf8", data=new_content)
                break

    return new_version_str
