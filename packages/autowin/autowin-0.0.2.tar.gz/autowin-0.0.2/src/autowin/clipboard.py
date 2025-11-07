# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:12:57.165Z
# 文件描述：autowin 模块的剪贴板操作封装。
# 文件路径：src/autowin/clipboard.py

import pyperclip
from typing import Optional
from .logger import logger
from .decorators import retry
from .exceptions import ClipboardError

class AutoWinClipboard:
    """
    autowin 模块的剪贴板操作类。
    封装了 pyperclip 的常用功能，并加入了日志和重试机制。
    """
    def __init__(self):
        logger.debug("✨ autowin 剪贴板模块初始化。")

    @retry(exceptions=ClipboardError)
    def copy(self, text: str) -> None:
        """
        将指定的文本复制到剪贴板。

        :param text: 要复制到剪贴板的文本。
        :raises ClipboardError: 如果剪贴板操作失败。
        """
        try:
            logger.debug(f"📋 尝试将文本复制到剪贴板: '{text}'")
            pyperclip.copy(text)
            logger.info(f"✅ 成功将文本复制到剪贴板。")
        except pyperclip.PyperclipException as e:
            logger.error(f"❌ 复制到剪贴板失败: {e}")
            raise ClipboardError(f"复制到剪贴板失败: {e}")
        except Exception as e:
            logger.error(f"❌ 复制到剪贴板失败 (未知错误): {e}")
            raise ClipboardError(f"复制到剪贴板失败 (未知错误): {e}")

    @retry(exceptions=ClipboardError)
    def paste(self) -> Optional[str]:
        """
        从剪贴板获取文本。

        :return: 剪贴板中的文本内容，如果剪贴板为空或操作失败则为 None。
        :raises ClipboardError: 如果剪贴板操作失败。
        """
        try:
            logger.debug("📋 尝试从剪贴板获取文本。")
            text = pyperclip.paste()
            if text:
                logger.info(f"✅ 成功从剪贴板获取文本: '{text}'")
            else:
                logger.warning("⚠️ 剪贴板中没有文本内容。")
            return text
        except pyperclip.PyperclipException as e:
            logger.error(f"❌ 从剪贴板获取文本失败: {e}")
            raise ClipboardError(f"从剪贴板获取文本失败: {e}")
        except Exception as e:
            logger.error(f"❌ 从剪贴板获取文本失败 (未知错误): {e}")
            raise ClipboardError(f"从剪贴板获取文本失败 (未知错误): {e}")

# 提供一个剪贴板模块的实例
clipboard = AutoWinClipboard()