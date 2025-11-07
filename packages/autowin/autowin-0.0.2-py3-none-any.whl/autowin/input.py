# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:11:18.982Z
# 文件描述：autowin 模块的鼠标和键盘操作封装。
# 文件路径：src/autowin/input.py

import pyautogui
from typing import Union, Tuple
from .logger import logger
from .decorators import retry
from .exceptions import AutoWinInputError
from .utils import sleep

class AutoWinInput:
    """
    autowin 模块的鼠标和键盘输入操作类。
    封装了 pyautogui 的常用功能，并加入了日志和重试机制。
    """
    def __init__(self):
        # pyautogui 的一些通用设置
        pyautogui.FAILSAFE = True  # 鼠标移动到左上角会终止程序
        pyautogui.PAUSE = 0.01     # 每个pyautogui函数执行后暂停的秒数
        logger.debug("✨ autowin 输入模块初始化。")

    @retry(exceptions=AutoWinInputError)
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1, interval: float = 0.0, duration: float = 0.0) -> None:
        """
        模拟鼠标点击。

        :param x: 点击的X坐标。
        :param y: 点击的Y坐标。
        :param button: 鼠标按钮，可选 'left', 'middle', 'right'。
        :param clicks: 点击次数。
        :param interval: 每次点击之间的间隔秒数。
        :param duration: 鼠标移动到目标位置的持续时间（秒）。
        :raises AutoWinInputError: 如果点击操作失败。
        """
        try:
            logger.debug(f"🖱️ 模拟鼠标点击: ({x}, {y}), 按钮: {button}, 次数: {clicks}, 间隔: {interval}s, 移动时长: {duration}s")
            pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval, duration=duration)
            logger.info(f"✅ 成功模拟鼠标点击: ({x}, {y})")
        except Exception as e:
            logger.error(f"❌ 鼠标点击失败: {e}")
            raise AutoWinInputError(f"鼠标点击失败: {e}")

    @retry(exceptions=AutoWinInputError)
    def double_click(self, x: int, y: int, button: str = 'left', duration: float = 0.0) -> None:
        """
        模拟鼠标双击。

        :param x: 双击的X坐标。
        :param y: 双击的Y坐标。
        :param button: 鼠标按钮，可选 'left', 'middle', 'right'。
        :param duration: 鼠标移动到目标位置的持续时间（秒）。
        :raises AutoWinInputError: 如果双击操作失败。
        """
        try:
            logger.debug(f"🖱️ 模拟鼠标双击: ({x}, {y}), 按钮: {button}, 移动时长: {duration}s")
            pyautogui.doubleClick(x=x, y=y, button=button, duration=duration)
            logger.info(f"✅ 成功模拟鼠标双击: ({x}, {y})")
        except Exception as e:
            logger.error(f"❌ 鼠标双击失败: {e}")
            raise AutoWinInputError(f"鼠标双击失败: {e}")

    @retry(exceptions=AutoWinInputError)
    def right_click(self, x: int, y: int, duration: float = 0.0) -> None:
        """
        模拟鼠标右键点击。

        :param x: 右键点击的X坐标。
        :param y: 右键点击的Y坐标。
        :param duration: 鼠标移动到目标位置的持续时间（秒）。
        :raises AutoWinInputError: 如果右键点击操作失败。
        """
        try:
            logger.debug(f"🖱️ 模拟鼠标右键点击: ({x}, {y}), 移动时长: {duration}s")
            pyautogui.rightClick(x=x, y=y, duration=duration)
            logger.info(f"✅ 成功模拟鼠标右键点击: ({x}, {y})")
        except Exception as e:
            logger.error(f"❌ 鼠标右键点击失败: {e}")
            raise AutoWinInputError(f"鼠标右键点击失败: {e}")

    @retry(exceptions=AutoWinInputError)
    def move_to(self, x: int, y: int, duration: float = 0.0) -> None:
        """
        模拟鼠标移动到指定坐标。

        :param x: 移动到的X坐标。
        :param y: 移动到的Y坐标。
        :param duration: 鼠标移动的持续时间（秒）。
        :raises AutoWinInputError: 如果鼠标移动操作失败。
        """
        try:
            logger.debug(f"🖱️ 模拟鼠标移动到: ({x}, {y}), 持续时间: {duration}s")
            pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"✅ 成功模拟鼠标移动到: ({x}, {y})")
        except Exception as e:
            logger.error(f"❌ 鼠标移动失败: {e}")
            raise AutoWinInputError(f"鼠标移动失败: {e}")

    @retry(exceptions=AutoWinInputError)
    def drag_to(self, x: int, y: int, duration: float = 0.0, button: str = 'left') -> None:
        """
        模拟鼠标从当前位置拖拽到指定坐标。

        :param x: 拖拽到的X坐标。
        :param y: 拖拽到的Y坐标。
        :param duration: 拖拽的持续时间（秒）。
        :param button: 拖拽时按下的鼠标按钮，可选 'left', 'middle', 'right'。
        :raises AutoWinInputError: 如果鼠标拖拽操作失败。
        """
        try:
            logger.debug(f"🖱️ 模拟鼠标拖拽到: ({x}, {y}), 持续时间: {duration}s, 按钮: {button}")
            pyautogui.dragTo(x, y, duration=duration, button=button)
            logger.info(f"✅ 成功模拟鼠标拖拽到: ({x}, {y})")
        except Exception as e:
            logger.error(f"❌ 鼠标拖拽失败: {e}")
            raise AutoWinInputError(f"鼠标拖拽失败: {e}")

    @retry(exceptions=AutoWinInputError)
    def scroll(self, clicks: int) -> None:
        """
        模拟鼠标滚轮滚动。

        :param clicks: 滚动量（正数向上滚动，负数向下滚动）。
        :raises AutoWinInputError: 如果鼠标滚轮滚动失败。
        """
        try:
            logger.debug(f"🖱️ 模拟鼠标滚轮滚动: {clicks} 次")
            pyautogui.scroll(clicks)
            logger.info(f"✅ 成功模拟鼠标滚轮滚动: {clicks} 次")
        except Exception as e:
            logger.error(f"❌ 鼠标滚轮滚动失败: {e}")
            raise AutoWinInputError(f"鼠标滚轮滚动失败: {e}")

    @retry(exceptions=AutoWinInputError)
    def type_text(self, text: str, interval: float = 0.0) -> None:
        """
        模拟键盘输入文本。

        :param text: 要输入的文本。
        :param interval: 每个字符输入之间的间隔秒数。
        :raises AutoWinInputError: 如果文本输入失败。
        """
        try:
            logger.debug(f"⌨️ 模拟键盘输入文本: '{text}', 间隔: {interval}s")
            pyautogui.write(text, interval=interval)
            logger.info(f"✅ 成功模拟键盘输入文本: '{text}'")
        except Exception as e:
            logger.error(f"❌ 文本输入失败: {e}")
            raise AutoWinInputError(f"文本输入失败: {e}")

    @retry(exceptions=AutoWinInputError)
    def press_key(self, key: str, presses: int = 1, interval: float = 0.0) -> None:
        """
        模拟键盘按键。

        :param key: 要按下的键（如 'enter', 'esc', 'shift', 'ctrl' 等）。
        :param presses: 按下次数。
        :param interval: 每次按键之间的间隔秒数。
        :raises AutoWinInputError: 如果按键操作失败。
        """
        try:
            logger.debug(f"⌨️ 模拟键盘按键: '{key}', 次数: {presses}, 间隔: {interval}s")
            pyautogui.press(key, presses=presses, interval=interval)
            logger.info(f"✅ 成功模拟键盘按键: '{key}'")
        except Exception as e:
            logger.error(f"❌ 键盘按键失败: {e}")
            raise AutoWinInputError(f"键盘按键失败: {e}")

    @retry(exceptions=AutoWinInputError)
    def hotkey(self, *args: str, interval: float = 0.0) -> None:
        """
        模拟组合键（热键）。

        :param args: 组合键的序列，例如 'ctrl', 'alt', 'del'。
        :param interval: 每个按键之间的间隔秒数。
        :raises AutoWinInputError: 如果组合键操作失败。
        """
        try:
            logger.debug(f"⌨️ 模拟组合键: {args}, 间隔: {interval}s")
            pyautogui.hotkey(*args, interval=interval)
            logger.info(f"✅ 成功模拟组合键: {args}")
        except Exception as e:
            logger.error(f"❌ 组合键操作失败: {e}")
            raise AutoWinInputError(f"组合键操作失败: {e}")

# 提供一个输入模块的实例
input_ = AutoWinInput()