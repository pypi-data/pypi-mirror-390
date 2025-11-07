# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:11:43.605Z
# 文件描述：autowin 模块的窗口操作封装。
# 文件路径：src/autowin/window.py

from typing import Any, Optional, Tuple, Union, Dict
import win32gui
import win32con
from pywinauto.findwindows import ElementNotFoundError

from .core import core
from .logger import logger
from .decorators import retry
from .exceptions import WindowNotFoundError


class AutoWinWindow:
    """
    autowin 模块的窗口操作类。
    封装了 pywinauto 对窗口的常用操作，并加入了日志和重试机制。
    """

    def __init__(self):
        logger.debug("✨ autowin 窗口模块初始化。")

    @retry(exceptions=(WindowNotFoundError, ElementNotFoundError))
    def get_window(self, title: Optional[str] = None, class_name: Optional[str] = None,
                   regex: Optional[str] = None, timeout: int = 10) -> Any:
        """
        根据条件获取一个窗口对象。

        :param title: 窗口的标题。
        :param class_name: 窗口的类名。
        :param regex: 用于匹配窗口标题或类名的正则表达式。
        :param timeout: 查找窗口的超时时间（秒）。
        :return: 找到的窗口对象。
        :raises WindowNotFoundError: 如果在超时时间内未找到窗口。
        """
        logger.debug(
            f"ℹ️ 尝试获取窗口，条件: title='{title}', class_name='{class_name}', regex='{regex}', 超时: {timeout}s")
        window = core.find_window(
            title=title, class_name=class_name, regex=regex, timeout=timeout)
        logger.info(f"✅ 成功获取窗口: {window.window_text()}")
        return window

    @retry(exceptions=WindowNotFoundError)
    def activate(self, window_obj: Any) -> None:
        """
        激活指定的窗口，使其成为当前活动窗口。

        :param window_obj: 窗口对象。
        :raises WindowNotFoundError: 如果窗口不存在或无法激活。
        """
        try:
            logger.debug(f"ℹ️ 尝试激活窗口: {window_obj.window_text()}")
            window_obj.set_focus()
            logger.info(f"✅ 成功激活窗口: {window_obj.window_text()}")
        except Exception as e:
            logger.error(f"❌ 激活窗口失败: {window_obj.window_text()} - {e}")
            raise WindowNotFoundError(
                f"激活窗口失败: {window_obj.window_text()} - {e}")

    @retry(exceptions=WindowNotFoundError)
    def maximize(self, window_obj: Any) -> None:
        """
        最大化指定的窗口。

        :param window_obj: 窗口对象。
        """
        try:
            logger.debug(f"ℹ️ 尝试最大化窗口: {window_obj.window_text()}")
            window_obj.maximize()
            logger.info(f"✅ 成功最大化窗口: {window_obj.window_text()}")
        except Exception as e:
            logger.error(f"❌ 最大化窗口失败: {window_obj.window_text()} - {e}")
            raise WindowNotFoundError(
                f"最大化窗口失败: {window_obj.window_text()} - {e}")

    @retry(exceptions=WindowNotFoundError)
    def minimize(self, window_obj: Any) -> None:
        """
        最小化指定的窗口。

        :param window_obj: 窗口对象。
        """
        try:
            logger.debug(f"ℹ️ 尝试最小化窗口: {window_obj.window_text()}")
            window_obj.minimize()
            logger.info(f"✅ 成功最小化窗口: {window_obj.window_text()}")
        except Exception as e:
            logger.error(f"❌ 最小化窗口失败: {window_obj.window_text()} - {e}")
            raise WindowNotFoundError(
                f"最小化窗口失败: {window_obj.window_text()} - {e}")

    @retry(exceptions=WindowNotFoundError)
    def restore(self, window_obj: Any) -> None:
        """
        恢复指定的窗口（从最大化或最小化状态）。

        :param window_obj: 窗口对象。
        """
        try:
            logger.debug(f"ℹ️ 尝试恢复窗口: {window_obj.window_text()}")
            window_obj.restore()
            logger.info(f"✅ 成功恢复窗口: {window_obj.window_text()}")
        except Exception as e:
            logger.error(f"❌ 恢复窗口失败: {window_obj.window_text()} - {e}")
            raise WindowNotFoundError(
                f"恢复窗口失败: {window_obj.window_text()} - {e}")

    @retry(exceptions=WindowNotFoundError)
    def close(self, window_obj: Any) -> None:
        """
        关闭指定的窗口。

        :param window_obj: 窗口对象。
        """
        try:
            logger.debug(f"ℹ️ 尝试关闭窗口: {window_obj.window_text()}")
            window_obj.close()
            logger.info(f"✅ 成功关闭窗口: {window_obj.window_text()}")
        except Exception as e:
            logger.error(f"❌ 关闭窗口失败: {window_obj.window_text()} - {e}")
            raise WindowNotFoundError(
                f"关闭窗口失败: {window_obj.window_text()} - {e}")

    @retry(exceptions=WindowNotFoundError)
    def move_window(self, window_obj: Any, x: int, y: int) -> None:
        """
        移动指定的窗口到屏幕上的新位置。

        :param window_obj: 窗口对象。
        :param x: 新的X坐标。
        :param y: 新的Y坐标。
        """
        try:
            logger.debug(
                f"ℹ️ 尝试移动窗口 '{window_obj.window_text()}' 到 ({x}, {y})")
            window_obj.move_window(x=x, y=y)
            logger.info(f"✅ 成功移动窗口 '{window_obj.window_text()}' 到 ({x}, {y})")
        except Exception as e:
            logger.error(
                f"❌ 移动窗口失败: {window_obj.window_text()} 到 ({x}, {y}) - {e}")
            raise WindowNotFoundError(
                f"移动窗口失败: {window_obj.window_text()} 到 ({x}, {y}) - {e}")

    @retry(exceptions=WindowNotFoundError)
    def resize_window(self, window_obj: Any, width: int, height: int) -> None:
        """
        调整指定窗口的大小。

        :param window_obj: 窗口对象。
        :param width: 新的宽度。
        :param height: 新的高度。
        """
        try:
            logger.debug(
                f"ℹ️ 尝试调整窗口 '{window_obj.window_text()}' 大小为 {width}x{height}")
            window_obj.resize_window(width=width, height=height)
            logger.info(
                f"✅ 成功调整窗口 '{window_obj.window_text()}' 大小为 {width}x{height}")
        except Exception as e:
            logger.error(
                f"❌ 调整窗口失败: {window_obj.window_text()} 大小为 {width}x{height} - {e}")
            raise WindowNotFoundError(
                f"调整窗口失败: {window_obj.window_text()} 大小为 {width}x{height} - {e}")

    def get_window_info(self, window_obj: Any) -> Dict[str, Union[str, int]]:
        """
        获取窗口的详细信息。

        :param window_obj: 窗口对象。
        :return: 包含窗口信息的字典。
        """
        info = {
            "title": window_obj.window_text(),
            "class_name": window_obj.class_name(),
            "handle": window_obj.handle,
            "process_id": window_obj.process_id(),
            "rectangle": window_obj.rectangle().as_rect(),
            "is_visible": window_obj.is_visible(),
            "is_active": window_obj.has_focus(),
            "is_maximized": window_obj.is_maximized(),
            "is_minimized": window_obj.is_minimized(),
            "is_topmost": self.is_topmost(window_obj)
        }
        logger.debug(f"ℹ️ 获取窗口信息: {info['title']} - {info}")
        return info

    def set_topmost(self, window_obj: Any) -> None:
        """
        将窗口置顶。

        :param window_obj: 窗口对象。
        """
        try:
            logger.debug(f"ℹ️ 尝试将窗口 '{window_obj.window_text()}' 置顶")
            win32gui.SetWindowPos(window_obj.handle, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            logger.info(f"✅ 成功将窗口 '{window_obj.window_text()}' 置顶")
        except Exception as e:
            logger.error(f"❌ 设置窗口置顶失败: {window_obj.window_text()} - {e}")
            raise WindowNotFoundError(
                f"设置窗口置顶失败: {window_obj.window_text()} - {e}")

    def remove_topmost(self, window_obj: Any) -> None:
        """
        取消窗口的置顶状态。

        :param window_obj: 窗口对象。
        """
        try:
            logger.debug(f"ℹ️ 尝试取消窗口 '{window_obj.window_text()}' 置顶")
            win32gui.SetWindowPos(window_obj.handle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            logger.info(f"✅ 成功取消窗口 '{window_obj.window_text()}' 置顶")
        except Exception as e:
            logger.error(f"❌ 取消窗口置顶失败: {window_obj.window_text()} - {e}")
            raise WindowNotFoundError(
                f"取消窗口置顶失败: {window_obj.window_text()} - {e}")

    def is_topmost(self, window_obj: Any) -> bool:
        """
        判断窗口是否置顶。

        :param window_obj: 窗口对象。
        :return: 如果窗口置顶，返回 True，否则返回 False。
        """
        try:
            logger.debug(f"ℹ️ 检查窗口 '{window_obj.window_text()}' 是否置顶")
            ex_style = win32gui.GetWindowLong(
                window_obj.handle, win32con.GWL_EXSTYLE)
            return bool(ex_style & win32con.WS_EX_TOPMOST)
        except Exception as e:
            logger.warning(f"⚠️ 检查窗口 '{window_obj.window_text()}' 置顶状态失败: {e}")
            return False


# 提供一个窗口模块的实例
window = AutoWinWindow()
