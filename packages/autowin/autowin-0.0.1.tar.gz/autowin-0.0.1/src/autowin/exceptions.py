# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:10:07.007Z
# 文件描述：autowin 模块的自定义异常类，用于提供更详细和有意义的错误信息。
# 文件路径：src/autowin/exceptions.py

class AutoWinError(Exception):
    """autowin 模块所有自定义异常的基类。"""
    pass

class WindowNotFoundError(AutoWinError):
    """未找到指定窗口时抛出的异常。"""
    def __init__(self, message: str = "未找到指定窗口。", search_criteria: dict = None):
        super().__init__(message)
        self.search_criteria = search_criteria or {}

class ControlNotFoundError(AutoWinError):
    """未找到指定控件时抛出的异常。"""
    def __init__(self, message: str = "未找到指定控件。", search_criteria: dict = None, parent_window_info: dict = None):
        super().__init__(message)
        self.search_criteria = search_criteria or {}
        self.parent_window_info = parent_window_info or {}

class ImageNotFoundError(AutoWinError):
    """在屏幕上未找到指定图像时抛出的异常。"""
    def __init__(self, message: str = "未在屏幕上找到指定图像。", image_path: str = None, confidence: float = None):
        super().__init__(message)
        self.image_path = image_path
        self.confidence = confidence

class ClipboardError(AutoWinError):
    """剪贴板操作失败时抛出的异常。"""
    def __init__(self, message: str = "剪贴板操作失败。"):
        super().__init__(message)

class AutoWinConfigError(AutoWinError):
    """autowin 配置错误时抛出的异常。"""
    def __init__(self, message: str = "autowin 配置错误。"):
        super().__init__(message)

class AutoWinInputError(AutoWinError):
    """鼠标或键盘输入操作失败时抛出的异常。"""
    def __init__(self, message: str = "鼠标或键盘输入操作失败。"):
        super().__init__(message)