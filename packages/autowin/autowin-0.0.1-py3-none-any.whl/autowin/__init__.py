# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:13:07.981Z
# 文件描述：autowin 模块的初始化文件，用于导出核心功能和配置。
# 文件路径：src/autowin/__init__.py

"""
autowin 模块是一个基于 pywinauto 和 pyautogui 的 Windows 自动化库，
提供了统一的 API 来操作窗口、控件、鼠标、键盘、屏幕截图和剪贴板。
"""

# 导入配置，日志，异常和装饰器
from .config import settings
from .logger import logger
from .exceptions import AutoWinError, WindowNotFoundError, ControlNotFoundError, ImageNotFoundError, ClipboardError, AutoWinConfigError, AutoWinInputError
from .decorators import retry
from .utils import sleep, get_mouse_position, get_screen_resolution

# 导入核心功能模块
from . import core
from . import input
from . import window
from . import control
from . import screenshot
from . import clipboard
from . import vision
from . import listener
from . import application

# 定义模块的公共 API
__all__ = [
    "settings",
    "logger",
    "retry",
    "sleep",
    "get_mouse_position",
    "get_screen_resolution",
    "AutoWinError",
    "WindowNotFoundError",
    "ControlNotFoundError",
    "ImageNotFoundError",
    "ClipboardError",
    "AutoWinConfigError",
    "AutoWinInputError",
    "core",
    "input",
    "window",
    "control",
    "screenshot",
    "clipboard",
    "vision",
    "listener",
    "application",
]

logger.info("🎉 autowin 模块初始化完成。")