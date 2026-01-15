"""
MCP 文件操作模块
提供基本的文件操作功能，所有函数均包含详细的参数说明、返回值说明和异常处理说明。
注意：所有字符串参数中的 \n、\t 等转义符将按照 Python 字符串规则解释，即 \n 表示换行符。
"""

import os
import shutil
from typing import Union, List, Dict


def mv(source: str, destination: str) -> str:
    """
    移动文件或目录到指定路径。

    Args:
        source (str): 源文件或目录的路径。
        destination (str): 目标路径。如果目标路径不存在，请先使用 mkdir 创建。

    Returns:
        str: 操作结果信息字符串。

    Raises:
        FileNotFoundError: 当源路径不存在时。
        shutil.Error: 移动过程中发生的错误。
    """
    if not os.path.exists(source):
        raise FileNotFoundError(f"源文件/目录不存在: {source}")

    shutil.move(source, destination)
    return f"已将 {source} 移动到 {destination}"


def cp(source: str, destination: str) -> str:
    """
    复制文件或目录到指定路径。

    Args:
        source (str): 源文件或目录的路径。
        destination (str): 目标路径。

    Returns:
        str: 操作结果信息字符串。

    Raises:
        FileNotFoundError: 当源路径不存在时。
        shutil.Error: 复制过程中发生的错误。
    """
    if not os.path.exists(source):
        raise FileNotFoundError(f"源文件/目录不存在: {source}")

    if os.path.isdir(source):
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)

    return f"已将 {source} 复制到 {destination}"


def ls(directory: str = ".") -> str:
    """
    列出指定目录下的所有文件和子目录。

    Args:
        directory (str): 要列出内容的目录路径，默认为当前目录。

    Returns:
        str: 目录内容列表的字符串表示。

    Raises:
        FileNotFoundError: 当指定目录不存在时。
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"目录不存在: {directory}")

    items = os.listdir(directory)
    return f"{directory} 中的内容: {', '.join(items)}"


def mkdir(directory: str) -> str:
    """
    创建目录。如果目录已存在，不会覆盖。

    Args:
        directory (str): 要创建的目录路径。

    Returns:
        str: 操作结果信息字符串。

    Raises:
        OSError: 当目录创建失败时。
    """
    if os.path.exists(directory):
        return f"目录已存在: {directory}"

    os.makedirs(directory)
    return f"已创建目录: {directory}"


def rm(path: str) -> str:
    """
    删除文件或目录。如果是目录，会递归删除整个目录树。

    Args:
        path (str): 要删除的文件或目录路径。

    Returns:
        str: 操作结果信息字符串。

    Raises:
        FileNotFoundError: 当路径不存在时。
        OSError: 当删除失败时。
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"文件/目录不存在: {path}")

    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

    return f"已删除: {path}"


def cat(filepath: str) -> str:
    """
    读取文件内容并返回。

    Args:
        filepath (str): 要读取的文件路径。

    Returns:
        str: 文件内容字符串。

    Raises:
        FileNotFoundError: 当文件不存在时。
        UnicodeDecodeError: 当文件编码非UTF-8且无法用GBK解码时。
        IOError: 当文件读取失败时。
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")

    # 优先使用 UTF-8 编码读取
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        # 尝试使用 GBK 编码
        try:
            with open(filepath, "r", encoding="gbk") as f:
                content = f.read()
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(f"无法用UTF-8或GBK解码文件: {filepath}") from e


    return content


def write_to_file(text: str, filepath: Union[str, None], mode: str) -> str:
    """
    将文本写入文件。如果 filepath 为 None，则直接返回文本。

    Args:
        text (str): 要写入的文本。注意：字符串中的转义符（如 \n、\t）会按照 Python 规则解释，
                    即 \n 会被解释为换行符。如果希望写入原始反斜杠和 n，请使用 \\\\n。
        filepath (Union[str, None]): 文件路径。如果为 None，则直接返回 text。
        mode (int): 写入模式，0 表示覆盖写入，1 表示追加写入。

    Returns:
        str: 写入成功的信息字符串，或当 filepath 为 None 时直接返回 text。

    Raises:
        ValueError: 当 filepath 为空字符串或 mode 不为 0 或 1 时。
        TypeError: 当 text 不是字符串类型时。
        OSError: 当文件写入失败时。
    """
    if filepath is None:
        return text

    if not isinstance(text, str):
        raise TypeError("文本必须是字符串类型")

    if not filepath.strip():
        raise ValueError("文件路径不能为空")

    if mode not in ('0', '1'):
        raise ValueError("mode 必须为 0（覆盖）或 1（追加）")

    # 确保目录存在
    save_dir = os.path.dirname(filepath)
    if save_dir and not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)

    try:
        if mode == '0':
            # 覆盖写入
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
                # 如果文本不以换行符结尾，则添加一个
                if not text.endswith("\n"):
                    f.write("\n")
            return f"已将文本覆盖写入 {filepath}"
        else:  # mode == 1
            # 追加写入
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(text)
                if not text.endswith("\n"):
                    f.write("\n")
            return f"已将文本追加写入 {filepath}"
    except Exception as e:
        raise OSError(f"文件写入失败: {str(e)}")


def find_lines_in_file(
    file_path: str, search_string: str, case_sensitive: bool = True
) -> List[Dict[str, Union[int, str]]]:
    """
    从文件中查找包含指定字符串的所有行，并返回行号、内容和原始内容。

    Args:
        file_path (str): 要搜索的文件路径。
        search_string (str): 要查找的字符串，不能为空。
        case_sensitive (bool): 是否区分大小写，默认为 True（区分）。

    Returns:
        List[Dict[str, Union[int, str]]]: 匹配行的列表，每个元素为一个字典，包含：
            - line_number (int): 行号（从1开始）
            - content (str): 移除行尾换行符后的行内容
            - original_content (str): 原始行内容（保留换行符）

    Raises:
        ValueError: 当文件路径为空或搜索字符串为空时。
        FileNotFoundError: 当文件不存在时。
        ValueError: 当路径不是文件时。
        UnicodeDecodeError: 当文件无法用UTF-8或GBK解码时。
        IOError: 当文件读取失败时。
    """
    if not file_path or not file_path.strip():
        raise ValueError("文件路径不能为空")

    if not search_string or not search_string.strip():
        raise ValueError("搜索字符串不能为空")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    if not os.path.isfile(file_path):
        raise ValueError(f"路径不是文件: {file_path}")

    matched_lines = []

    def process_file(file_handle):
        for line_number, line in enumerate(file_handle, start=1):
            # 根据 case_sensitive 参数决定搜索方式
            if case_sensitive:
                if search_string in line:
                    matched_lines.append(
                        {
                            "line_number": line_number,
                            "content": line.rstrip("\n"),  # 移除行尾换行符
                            "original_content": line,  # 保留原始内容
                        }
                    )
            else:
                if search_string.lower() in line.lower():
                    matched_lines.append(
                        {
                            "line_number": line_number,
                            "content": line.rstrip("\n"),
                            "original_content": line,
                        }
                    )

    try:
        # 优先使用 UTF-8 编码读取
        with open(file_path, "r", encoding="utf-8") as file:
            process_file(file)
    except UnicodeDecodeError:
        # 尝试使用 GBK 编码
        try:
            with open(file_path, "r", encoding="gbk") as file:
                process_file(file)
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(f"无法用UTF-8或GBK解码文件: {file_path}") from e
    except Exception as e:
        raise IOError(f"文件读取失败: {str(e)}")

    return matched_lines