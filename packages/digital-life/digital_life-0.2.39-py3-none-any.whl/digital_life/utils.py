
# 工具箱
import re
from digital_life.models import MemoryCards

def memoryCards2str(memory_cards: MemoryCards):
    memoryCards_str = ""
    memoryCards_time_str = ""
    for memory_card in memory_cards:
        memory_card_str = memory_card["title"] + "\n" + memory_card["content"] + "\n"
        memoryCards_str += memory_card_str
        memoryCards_time_str += "\n"
        memoryCards_time_str += memory_card["time"]
    return memoryCards_str, memoryCards_time_str



def extract_last_user_input(dialogue_text):
    """
    从多轮对话文本中提取最后一个 user 的输入内容。

    Args:
        dialogue_text: 包含多轮对话的字符串。

    Returns:
        最后一个 user 的输入内容字符串，如果未找到则返回 None。
    """
    pattern = r"(?s).*user:\s*(.*?)(?=user:|$)"

    match = re.search(pattern, dialogue_text)

    if match:
        # group(1) 捕获的是最后一个 user: 到下一个 user: 或字符串末尾的内容
        return match.group(1).strip()
    else:
        return None
    

def extract_json(text: str) -> str:
    """从文本中提取python代码
    Args:
        text (str): 输入的文本。
    Returns:
        str: 提取出的python文本
    """
    pattern = r"```json([\s\S]*?)```"
    matches = re.findall(pattern, text)
    if matches:
        return matches[0].strip()  # 添加strip()去除首尾空白符
    else:
        return ""  # 返回空字符串或抛出异常，此处返回空字符串


def extract_article(text: str) -> str:
    """从文本中提取python代码
    Args:
        text (str): 输入的文本。
    Returns:
        str: 提取出的python文本
    """
    pattern = r"```article([\s\S]*?)```"
    matches = re.findall(pattern, text)
    if matches:
        return matches[0].strip()  # 添加strip()去除首尾空白符
    else:
        return ""  # 返回空字符串或抛出异常，此处返回空字符串
