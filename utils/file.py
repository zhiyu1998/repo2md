import os
import shutil
import stat
from pathlib import Path
from urllib.parse import urlparse

from .logger_config import logger


def get_all_files(directory):
    """
    递归匹配指定目录下的所有文件
    :param directory:
    :return:
    """
    return [str(file) for file in Path(directory).rglob('*') if file.is_file()]


def get_file_extensions(directory):
    """
        提取后缀
    :param directory:
    :param exclude_dirs:
    :return:
    """
    exclude_dirs = get_exclude_files_from_gitignore(directory)
    extensions = {file.suffix for file in Path(directory).rglob('*')
                  if file.is_file() and file.suffix and not any(part in exclude_dirs for part in file.parts)}
    return extensions


def get_repo_name(repo_url):
    """
        提取仓库名
    :param repo_url:
    :return:
    """
    repo_name = os.path.basename(repo_url)
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    # 目标路径为当前文件夹下的仓库名称
    return os.path.join("./", repo_name)


def force_remove_readonly(func, path, _):
    """
    强制修改只读文件的权限并删除
    """
    os.chmod(path, stat.S_IWRITE)  # 修改文件权限为可写
    func(path)


def delete_directory(directory: str) -> None:
    """
    递归删除指定的目录及其所有内容，强制解除只读文件权限。

    :param directory: 要删除的目录路径
    """
    dir_path = Path(directory)
    if dir_path.exists() and dir_path.is_dir():
        try:
            shutil.rmtree(dir_path, onerror=force_remove_readonly)
            logger.info(f"Directory {directory} has been deleted.")
        except Exception as e:
            logger.error(f"Failed to delete {directory}: {e}")
    else:
        logger.error(f"Directory {directory} does not exist or is not a directory.")


def is_file_path(s):
    """
    判断字符串是否是文件路径
    :param s: 输入字符串
    :return: True 如果是文件路径, False 如果不是
    """
    # 使用pathlib检查是否是路径
    path = Path(s)
    if path.exists():
        return True

    # 使用urllib检查是否是URL
    if bool(urlparse(s).scheme) and bool(urlparse(s).netloc):
        return False

    # 检查路径是否以斜杠开头或包含盘符
    if s.startswith('/') or (len(s) > 1 and s[1] == ':'):
        return True

    # 默认返回False
    return False


def parse_gitignore(gitignore_path):
    exclude_patterns = set()
    with open(gitignore_path, 'r') as f:
        for line in f:
            # 忽略注释和空行
            line = line.strip()
            if line and not line.startswith('#'):
                exclude_patterns.add(line)
    return exclude_patterns


def should_exclude(file, exclude_patterns):
    for pattern in exclude_patterns:
        # 检查文件路径是否匹配 .gitignore 的模式
        if file.match(pattern) or any(part.match(pattern) for part in file.parts):
            return True
    return False


def get_exclude_files_from_gitignore(gitignore_path):
    # 如果 .gitignore 文件存在，解析排除模式
    gitignore_path = Path(gitignore_path) / '.gitignore'
    if Path(gitignore_path).exists():
        return parse_gitignore(gitignore_path)
    else:
        return set()


if __name__ == '__main__':
    name = get_repo_name('https://github.com/zhiyu1998/nonebot-plugin-resolver')
    logger.info(is_file_path("https://github.com/zhiyu1998/nonebot-plugin-resolver"))  # 输出: False
    logger.info(is_file_path("/home/user/file.txt"))  # 输出: True
    logger.info(is_file_path("C:\\Users\\file.txt"))  # 输出: True
    logger.info(is_file_path("not_a_path_or_url"))  # 输出: False
