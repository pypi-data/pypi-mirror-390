# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T07:03:15.366Z
# 文件描述：autowin 模块的应用程序启动和管理功能。
# 文件路径：src/autowin/application.py

import os
import subprocess
import time
import webbrowser
import httpx
from parsel import Selector
from typing import Optional, Any

from .logger import logger
from .exceptions import AutoWinError
from .config import settings

class ApplicationManager:
    """
    提供应用程序启动、URL 打开和相关管理功能。
    """
    def __init__(self):
        logger.debug("✨ autowin 应用程序管理模块初始化。")

    def start_application(
        self,
        target: str,
        wait_time: int = 3,
        browser_path: Optional[str] = None,
        backend: Optional[str] = None
    ) -> Any: # 返回值类型可以是 pywinauto.Application 或 None
        """
        打开文件、程序或网址。

        :param target: 要打开的文件、程序路径或网址。
        :param wait_time: 等待程序启动的时间（秒）。
        :param browser_path: (可选) 指定浏览器路径，用于打开网址。
        :param backend: (可选) 指定 pywinauto 的后端，可选 "uia" 或 "win32"。如果未指定，则使用全局配置。
        :raises AutoWinError: 如果目标无效或启动失败。
        :return: 如果成功启动程序，返回 pywinauto.Application 对象，否则返回 None。
        """
        logger.info(f"ℹ️ 尝试启动目标: {target}")
        if target.startswith(('http://', 'https://')):
            self._open_url(target, browser_path)
            # 对于URL，我们无法直接返回pywinauto.Application对象，因为浏览器是独立的进程
            # 可以在后续通过get_window找到浏览器窗口
            app_object = None
        elif os.path.exists(target):
            try:
                # 使用 pywinauto 启动应用程序
                app_object = core.start_application(target, backend=backend)
                logger.info(f"✅ 成功启动应用程序: {target}")
            except Exception as e:
                logger.error(f"❌ 启动应用程序失败: {target} - {e}")
                raise AutoWinError(f"启动应用程序失败: {target} - {e}")
        else:
            logger.error(f"❌ 无效的目标: {target}")
            raise AutoWinError(f"无效的目标: {target}")

        if wait_time > 0:
            logger.info(f"ℹ️ 等待 {wait_time} 秒，等待目标加载完成...")
            time.sleep(wait_time)
        
        return app_object

    def _open_url(self, url: str, browser_path: Optional[str] = None) -> None:
        """
        在浏览器中打开指定的 URL。

        :param url: 要打开的 URL。
        :param browser_path: (可选) 指定浏览器路径。
        """
        try:
            if browser_path:
                try:
                    subprocess.Popen([browser_path, url])
                    logger.info(f"✅ 使用指定浏览器打开网址: {url} (浏览器路径: {browser_path})")
                except Exception as e:
                    logger.warning(f"⚠️ 使用指定浏览器打开网址失败，尝试使用默认浏览器: {url} - {e}")
                    webbrowser.open(url)
            else:
                webbrowser.open(url)
                logger.info(f"✅ 使用默认浏览器打开网址: {url}")
        except Exception as e:
            logger.error(f"❌ 打开网址失败: {url} - {e}")
            raise AutoWinError(f"打开网址失败: {url} - {e}")

    def get_url_title(self, url: str) -> Optional[str]:
        """
        获取指定 URL 的网页标题。

        :param url: 要获取标题的网页 URL。
        :return: 网页标题，如果无法获取则返回 None。
        """
        try:
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
            }
            response = httpx.get(url, headers=headers, timeout=settings.DEFAULT_TIMEOUT)
            response.raise_for_status()

            selector = Selector(text=response.text)
            title = selector.xpath('//title/text()').get()
            if title:
                logger.debug(f"ℹ️ 获取到 URL '{url}' 的标题: {title.strip()}")
                return title.strip()
            else:
                logger.warning(f"⚠️ 未能获取到 URL '{url}' 的标题。")
                return None
        except httpx.RequestError as e:
            logger.error(f"❌ 请求 URL '{url}' 失败: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 解析 URL '{url}' 标题失败: {e}")
            return None

# 提供一个应用程序管理模块的实例
application = ApplicationManager()

# 由于 start_application 可能会返回 pywinauto.Application 对象，这里需要从 core 模块导入
# 避免循环引用，将此导入放在类定义之后
from .core import core
