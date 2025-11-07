# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:13:07.981Z
# 文件描述：autowin 模块的初始化文件，用于导出核心功能和配置。
# 文件路径：src/autowin/__init__.py

"""
autowin 模块是一个基于 pywinauto 和 pyautogui 的 Windows 自动化库，
提供了统一的 API 来操作窗口、控件、鼠标、键盘、屏幕截图和剪贴板。
"""

# 导入配置、日志、异常和装饰器
from .config import settings
from .logger import logger
from .exceptions import (
    AutoWinError,
    WindowNotFoundError,
    ControlNotFoundError,
    ImageNotFoundError,
    ClipboardError,
    AutoWinConfigError,
    AutoWinInputError,
)
from .decorators import retry
from .utils import sleep, get_mouse_position, get_screen_resolution

# 导入核心模块的实例
from .application import application
from .clipboard import clipboard
from .control import control
from .core import core
from .input import input_
from .screenshot import screenshot
from .vision import vision
from .window import window
from .listener import listener
from .message import WeChatSender

# =================================================================
# 将核心功能提升到顶层命名空间，方便用户调用
# =================================================================

# 应用与核心功能
start_app = application.start_application
get_url_title = application.get_url_title
connect_app = core.connect_application
get_current_app = core.get_current_application
set_backend = core.set_pywinauto_backend
print_control_info = core.print_control_info

# 窗口功能
get_window = window.get_window
activate_window = window.activate
maximize_window = window.maximize
minimize_window = window.minimize
restore_window = window.restore
close_window = window.close
move_window = window.move_window
resize_window = window.resize_window
get_window_info = window.get_window_info
set_topmost = window.set_topmost
remove_topmost = window.remove_topmost
is_topmost = window.is_topmost

# 控件功能
get_control = control.get_control
click_control = control.click_control
set_text = control.set_text
get_text = control.get_text
select_item = control.select_item
is_checked = control.is_checked
check_control = control.check_control
uncheck_control = control.uncheck_control
get_control_properties = control.get_properties

# 输入功能 (来自 input_)
click = input_.click
double_click = input_.double_click
right_click = input_.right_click
move_to = input_.move_to
drag_to = input_.drag_to
scroll = input_.scroll
type_text = input_.type_text
press_key = input_.press_key
hotkey = input_.hotkey

# 截图与视觉功能
take_screenshot = screenshot.take_screenshot
find_image = vision.find_image_on_screen
click_image = vision.click_image
wait_for_image = vision.wait_for_image
wait_until_image_disappears = vision.wait_until_image_disappears

# 剪贴板功能
copy_to_clipboard = clipboard.copy
paste_from_clipboard = clipboard.paste

# 监听器功能
start_listening = listener.start
stop_listening = listener.stop

# 消息发送功能
wechat_sender = WeChatSender

# 定义模块的公共 API
__all__ = [
    # 配置与日志
    "settings",
    "logger",
    # 装饰器与工具
    "retry",
    "sleep",
    "get_mouse_position",
    "get_screen_resolution",
    # 异常
    "AutoWinError",
    "WindowNotFoundError",
    "ControlNotFoundError",
    "ImageNotFoundError",
    "ClipboardError",
    "AutoWinConfigError",
    "AutoWinInputError",
    # 核心与应用
    "start_app",
    "get_url_title",
    "connect_app",
    "get_current_app",
    "set_backend",
    "print_control_info",
    # 窗口操作
    "get_window",
    "activate_window",
    "maximize_window",
    "minimize_window",
    "restore_window",
    "close_window",
    "move_window",
    "resize_window",
    "get_window_info",
    "set_topmost",
    "remove_topmost",
    "is_topmost",
    # 控件操作
    "get_control",
    "click_control",
    "set_text",
    "get_text",
    "select_item",
    "is_checked",
    "check_control",
    "uncheck_control",
    "get_control_properties",
    # 输入操作
    "click",
    "double_click",
    "right_click",
    "move_to",
    "drag_to",
    "scroll",
    "type_text",
    "press_key",
    "hotkey",
    # 截图与视觉操作
    "take_screenshot",
    "find_image",
    "click_image",
    "wait_for_image",
    "wait_until_image_disappears",
    # 剪贴板操作
    "copy_to_clipboard",
    "paste_from_clipboard",
    # 监听器操作
    "start_listening",
    "stop_listening",
    # 消息发送
    "WeChatSender",
]