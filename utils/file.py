import os
import shutil
import stat
from pathlib import Path

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
    :return:
    """
    extensions = { file.suffix for file in Path(directory).rglob('*') if file.is_file() and file.suffix }
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


if __name__ == '__main__':
    name = get_repo_name('https://github.com/zhiyu1998/nonebot-plugin-resolver')
