from pathlib import Path

from git import Repo
from inquirer import prompt, Text, Checkbox, Confirm

from core.repo_local import process_files
from utils.logger_config import logger
from utils.file import get_file_extensions, get_repo_name, delete_directory, is_file_path


def get_extensions(file_path: str):
    """
        通过交互获取用户想要转换的文件后缀
    :param file_path:
    :return:
    """
    exts = get_file_extensions(file_path)
    ext_questions = [
        Confirm('all', message="是否将所有文件转换为markdown文件", default=True),
    ]
    ext_answers = prompt(ext_questions)
    if not ext_answers['all']:
        ext_questions = [
            Checkbox('extensions', choices=list(exts), message="选择需要转换的文件后缀"),
        ]
        exts = prompt(ext_questions)['extensions']
    return exts


def start():
    questions = [
        Text('repo', message="输入需要转换的仓库"),
        Confirm('remove', message="是否转换完成需要删除原仓库", default=True),
    ]
    answers = prompt(questions)
    repo_url = answers['repo']
    if not is_file_path(repo_url):
        repo_name = get_repo_name(repo_url)
        repo_save_path = repo_name
        logger.info(f"当前仓库{repo_name}：{repo_url}")
        if not Path(repo_name).exists():
            # 将仓库克隆到当前目录
            Repo.clone_from(repo_url, repo_name)
    else:
        repo_folder_path = Path(repo_url).resolve()
        repo_name = str(repo_folder_path)
        repo_save_path = repo_name + "/" + repo_folder_path.name
        logger.info(f"当前仓库本地位置：{repo_name}")
    extensions = get_extensions(repo_name)
    process_files(repo_name, extensions, f"{repo_save_path}.md")
    logger.success("转换完成，保存在当前目录下的 {}.md".format(repo_save_path))
    if answers['remove']:
        delete_directory(repo_name)


if __name__ == '__main__':
    start()
