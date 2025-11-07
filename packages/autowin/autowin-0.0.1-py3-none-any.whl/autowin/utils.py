# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:10:48.074Z
# 文件描述：autowin 模块的辅助工具函数。
# 文件路径：src/autowin/utils.py

import time
from typing import Tuple, Union
from .logger import logger

def sleep(seconds: Union[int, float]) -> None:
    """
    暂停执行指定的秒数。

    :param seconds: 暂停的秒数。
    """
    logger.debug(f"ℹ️ 暂停执行 {seconds} 秒...")
    time.sleep(seconds)

def get_mouse_position() -> Tuple[int, int]:
    """
    获取当前鼠标的屏幕坐标。

    :return: 鼠标的 (x, y) 坐标。
    """
    import pyautogui
    x, y = pyautogui.position()
    logger.debug(f"ℹ️ 当前鼠标位置: ({x}, {y})")
    return x, y

def get_screen_resolution() -> Tuple[int, int]:
    """
    获取屏幕分辨率。

    :return: 屏幕的 (宽度, 高度) 像素。
    """
    import pyautogui
    width, height = pyautogui.size()
    logger.debug(f"ℹ️ 屏幕分辨率: {width}x{height}")
    return width, height