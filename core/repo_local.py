import re

from pathlib import Path
from typing import Dict, Union, List, Tuple, Set

from icecream import ic

from utils.file import get_exclude_files_from_gitignore


def save_to_markdown(file_dict: Dict[str, str], markdown_file: str, append: bool = False) -> None:
    """
    将文件字典保存为 Markdown 格式：
    - 对于 .md 文件，将所有标题转换为四级标题保存。
    - 对于其他文件，内容用代码块表示。

    :param file_dict: 保存文件名和内容的字典，key为文件路径，value为文件内容
    :param markdown_file: 要保存的 markdown 文件路径
    :param append: 是否追加保存（True 为追加保存，False 为覆盖写入）
    """
    mode = 'a' if append else 'w'  # 追加模式 or 覆盖模式
    with open(markdown_file, mode, encoding='utf-8') as md_file:
        for key, content in file_dict.items():
            # 三级标题显示文件路径
            md_file.write(f"### {key}\n\n")

            # 判断是否为 .md 文件
            if key.endswith('.md'):
                # 将所有标题（一级到三级）转换为四级标题
                modified_content = re.sub(r'(^|\n)(#+)', r'\1####', content)
                md_file.write(f"{modified_content}\n\n")
            else:
                # 对于其他文件，用代码块保存内容
                md_file.write(f"```\n{content}\n```\n\n")


def process_files(directory: str,
                  suffix_filter: Union[List[str], Tuple[str], Set[str]],
                  markdown_file: str) -> None:
    """
    递归读取符合后缀的文件，按要求保存为 Markdown 文件。

    :param directory: 要递归遍历的文件夹路径
    :param suffix_filter: 需要过滤的文件后缀，支持 List、tuple 和 set
    :param markdown_file: 输出的 Markdown 文件路径
    """
    file_dict = {}  # 保存文件名和内容的字典
    count = 0  # 用于统计每处理5个文件保存一次
    exclude_dirs = get_exclude_files_from_gitignore(directory)
    ic(exclude_dirs)

    for file in Path(directory).rglob('*'):
        # 跳过要排除的目录及其子文件
        if any(part in exclude_dirs for part in file.parts):
            continue
        if file.is_file() and file.suffix in suffix_filter:
            # 组合键为文件夹名+文件名
            key = str(file.relative_to(Path(directory).parent))
            # 读取文件内容
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                file_dict[key] = content
                count += 1

            # 每处理 5 个文件增量保存一次
            if count % 5 == 0:
                save_to_markdown(file_dict, markdown_file, append=True)
                file_dict.clear()  # 清空字典，继续保存后续文件

    # 处理剩余不足 5 个文件的情况
    if file_dict:
        save_to_markdown(file_dict, markdown_file, append=True)


if __name__ == '__main__':
    # 使用示例
    directory = "."  # 当前目录
    suffix_filter = {'.py', '.md'}  # 需要过滤的后缀，可以是 List, tuple, set
    markdown_file = "output.md"  # 输出的 Markdown 文件
    process_files(directory, suffix_filter, markdown_file)
