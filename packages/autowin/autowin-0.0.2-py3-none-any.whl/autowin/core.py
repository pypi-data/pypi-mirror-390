# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:10:57.129Z
# 文件描述：autowin 模块的核心功能，用于应用连接、窗口和控件的查找与等待。
# 文件路径：src/autowin/core.py

import time
from typing import Optional, Union, Any, Dict
from pywinauto import Application, Desktop
from pywinauto.findwindows import ElementNotFoundError

from .config import settings
from .logger import logger
from .exceptions import AutoWinError, WindowNotFoundError, ControlNotFoundError
from .decorators import retry
from .utils import sleep

class AutoWinCore:
    """
    autowin 模块的核心类，提供应用连接、窗口和控件查找的基础功能。
    """
    def __init__(self):
        self._app: Optional[Application] = None
        logger.debug(f"✨ autowin 核心模块初始化，使用后端: {settings.PYWINAUTO_BACKEND}")

    def _get_desktop(self) -> Desktop:
        """获取 pywinauto 的 Desktop 对象。"""
        return Desktop(backend=settings.PYWINAUTO_BACKEND)

    @retry(exceptions=(ElementNotFoundError, WindowNotFoundError), attempts=settings.MAX_RETRIES, delay=settings.RETRY_DELAY, backoff=settings.RETRY_BACKOFF)
    def find_window(self, title: Optional[str] = None, class_name: Optional[str] = None,
                    regex: Optional[str] = None, timeout: int = settings.DEFAULT_TIMEOUT) -> Any:
        """
        查找并返回一个窗口对象。

        :param title: 窗口的标题。
        :param class_name: 窗口的类名。
        :param regex: 用于匹配窗口标题或类名的正则表达式。
        :param timeout: 查找窗口的超时时间（秒）。
        :return: 找到的窗口对象。
        :raises WindowNotFoundError: 如果在超时时间内未找到窗口。
        """
        search_criteria = {}
        if title:
            search_criteria['title'] = title
        if class_name:
            search_criteria['class_name'] = class_name
        if regex:
            search_criteria['title_re'] = regex # pywinauto使用title_re

        logger.debug(f"ℹ️ 尝试查找窗口，条件: {search_criteria}, 超时: {timeout}s")
        logger.debug(f"ℹ️ 尝试查找窗口，条件: {search_criteria}, 超时: {timeout}s")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                window = self._get_desktop().window(**search_criteria)
                if window.exists(): # 确保窗口确实存在且可用
                    logger.info(f"✅ 成功找到窗口: {window.window_text()}")
                    return window
            except ElementNotFoundError:
                pass # 继续重试
            sleep(1) # 增加等待时间，避免CPU占用过高，并给予窗口更多时间出现

        logger.error(f"❌ 在 {timeout}s 内未找到窗口，条件: {search_criteria}")
        raise WindowNotFoundError(
            message=f"未找到窗口，条件: {search_criteria}",
            search_criteria=search_criteria
        )

    @retry(exceptions=(ElementNotFoundError, ControlNotFoundError))
    def find_control(self, parent_window: Any, control_type: Optional[str] = None,
                     title: Optional[str] = None, auto_id: Optional[str] = None,
                     class_name: Optional[str] = None, regex: Optional[str] = None,
                     timeout: int = settings.DEFAULT_TIMEOUT) -> Any:
        """
        在指定父窗口中查找并返回一个控件对象。

        :param parent_window: 父窗口对象 (pywinauto WindowSpecification)。
        :param control_type: 控件的类型（如 "Button", "Edit", "Pane"）。
        :param title: 控件的文本或标题。
        :param auto_id: 控件的自动化 ID。
        :param class_name: 控件的类名。
        :param regex: 用于匹配控件标题或类名的正则表达式。
        :param timeout: 查找控件的超时时间（秒）。
        :return: 找到的控件对象。
        :raises ControlNotFoundError: 如果在超时时间内未找到控件。
        """
        search_criteria = {}
        if control_type:
            search_criteria['control_type'] = control_type
        if title:
            search_criteria['title'] = title
        if auto_id:
            search_criteria['auto_id'] = auto_id
        if class_name:
            search_criteria['class_name'] = class_name
        if regex:
            search_criteria['title_re'] = regex # pywinauto使用title_re

        parent_info = {"title": parent_window.window_text(), "class_name": parent_window.class_name()}
        logger.debug(f"ℹ️ 在窗口 '{parent_info['title']}' 中尝试查找控件，条件: {search_criteria}, 超时: {timeout}s")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                control = parent_window.child_window(**search_criteria)
                if control.exists(): # 确保控件确实存在且可用
                    logger.info(f"✅ 成功找到控件: {control.window_text() if hasattr(control, 'window_text') else control.class_name()}")
                    return control
            except ElementNotFoundError:
                pass # 继续重试
            sleep(0.5) # 短暂等待后重试

        logger.error(f"❌ 在 {timeout}s 内未找到控件，条件: {search_criteria}, 父窗口: {parent_info}")
        raise ControlNotFoundError(
            message=f"未找到控件，条件: {search_criteria}",
            search_criteria=search_criteria,
            parent_window_info=parent_info
        )

    def start_application(self, path: str, cmd_line_args: Optional[str] = None,
                            timeout: int = settings.DEFAULT_TIMEOUT, backend: Optional[str] = None) -> Any:
        """
        启动一个应用程序并连接。

        :param path: 应用程序的完整路径。
        :param cmd_line_args: 命令行启动参数。
        :param timeout: 启动并连接的超时时间（秒）。
        :param backend: (可选) 指定 pywinauto 的后端，可选 "uia" 或 "win32"。
                        如果为 None，则尝试使用 "uia" 后端，如果失败则回退到 "win32" 后端。
        :return: pywinauto Application 对象。
        :raises AutoWinError: 如果应用程序启动失败。
        """
        backends_to_try = []
        if backend:
            backends_to_try.append(backend)
        elif settings.PYWINAUTO_BACKEND == "uia":
            backends_to_try.extend(["uia", "win32"])
        else: # settings.PYWINAUTO_BACKEND == "win32"
            backends_to_try.extend(["win32", "uia"])
        
        last_exception = None
        for current_backend in backends_to_try:
            logger.info(f"🚀 尝试使用 '{current_backend}' 后端启动应用程序: {path} {cmd_line_args if cmd_line_args else ''}")
            try:
                self._app = Application(backend=current_backend)
                self._app.start(cmd_line=f'"{path}" {cmd_line_args if cmd_line_args else ""}', timeout=timeout, wait_for_idle=True)
                logger.info(f"✅ 应用程序 '{path}' 使用 '{current_backend}' 后端启动成功。")
                return self._app
            except Exception as e:
                logger.warning(f"⚠️ 使用 '{current_backend}' 后端启动应用程序失败: {e}")
                last_exception = e
                # 如果是显式指定了 backend，则不再尝试其他后端
                if backend:
                    break

        logger.error(f"❌ 应用程序 '{path}' 启动失败，所有尝试的后端均告失败。")
        raise AutoWinError(f"应用程序 '{path}' 启动失败: {last_exception}")

    def connect_application(self, process: Optional[int] = None, path: Optional[str] = None,
                            title: Optional[str] = None, timeout: int = settings.DEFAULT_TIMEOUT,
                            backend: Optional[str] = None) -> Any:
        """
        连接到一个已运行的应用程序。

        :param process: 应用程序的进程 ID。
        :param path: 应用程序的可执行文件路径。
        :param title: 应用程序主窗口的标题。
        :param timeout: 连接的超时时间（秒）。
        :param backend: (可选) 指定 pywinauto 的后端，可选 "uia" 或 "win32"。
                        如果为 None，则尝试使用 "uia" 后端，如果失败则回退到 "win32" 后端。
        :return: pywinauto Application 对象。
        :raises AutoWinError: 如果应用程序连接失败。
        """
        search_criteria = {}
        if process:
            search_criteria['process'] = process
        if path:
            search_criteria['path'] = path
        if title:
            search_criteria['title'] = title

        if not search_criteria:
            logger.error("❌ 连接应用程序需要提供 'process', 'path' 或 'title' 中的至少一个参数。")
            raise ValueError("连接应用程序需要提供 'process', 'path' 或 'title' 中的至少一个参数。")

        backends_to_try = []
        if backend:
            backends_to_try.append(backend)
        elif settings.PYWINAUTO_BACKEND == "uia":
            backends_to_try.extend(["uia", "win32"])
        else: # settings.PYWINAUTO_BACKEND == "win32"
            backends_to_try.extend(["win32", "uia"])

        last_exception = None
        for current_backend in backends_to_try:
            logger.info(f"🔗 尝试使用 '{current_backend}' 后端连接应用程序，条件: {search_criteria}, 超时: {timeout}s")
            try:
                self._app = Application(backend=current_backend)
                self._app.connect(**search_criteria, timeout=timeout)
                logger.info(f"✅ 应用程序使用 '{current_backend}' 后端连接成功。")
                return self._app
            except Exception as e:
                logger.warning(f"⚠️ 使用 '{current_backend}' 后端连接应用程序失败: {e}")
                last_exception = e
                if backend: # 如果是显式指定了 backend，则不再尝试其他后端
                    break

        logger.error(f"❌ 应用程序连接失败，所有尝试的后端均告失败。")
        raise AutoWinError(f"应用程序连接失败: {last_exception}")

    def get_current_application(self) -> Optional[Any]:
        """
        获取当前连接的应用程序对象。

        :return: 当前连接的 pywinauto Application 对象，如果未连接则为 None。
        """
        if self._app is None:
            logger.warning("⚠️ 尚未连接任何应用程序。请先调用 start_application 或 connect_application。")
        return self._app

    def set_pywinauto_backend(self, backend: str) -> None:
        """
        设置 pywinauto 的后端类型。

        :param backend: 后端类型，可选 "uia" 或 "win32"。
        :raises ValueError: 如果后端类型无效。
        """
        if backend not in ["uia", "win32"]:
            raise ValueError("pywinauto 后端类型必须是 'uia' 或 'win32'。")
        settings.PYWINAUTO_BACKEND = backend
        logger.info(f"🔧 pywinauto 后端已设置为: {backend}")

    def print_control_info(self, window: Any) -> None:
        """
        打印给定窗口的所有子控件的详细信息，使用 pywinauto 的 print_control_identifiers。

        :param window: pywinauto 窗口对象。
        """
        if not window:
            logger.warning("⚠️ 提供的窗口对象为空，无法打印控件信息。")
            return

        logger.info(f"📋 正在打印窗口 '{window.window_text()}' 的控件标识符:")
        try:
            window.print_control_identifiers()
        except Exception as e:
            logger.error(f"❌ 打印控件标识符时发生错误: {e}")

# 提供一个核心模块的实例
core = AutoWinCore()