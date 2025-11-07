# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:12:34.642Z
# 文件描述：autowin 模块的屏幕截图与图像识别封装。
# 文件路径：src/autowin/screenshot.py

import pyautogui
import os
import time
from typing import Tuple, Optional

from .config import settings
from .logger import logger
from .decorators import retry
from .exceptions import ImageNotFoundError, AutoWinError

class AutoWinScreenshot:
    """
    autowin 模块的屏幕截图与图像识别类。
    封装了 pyautogui 的截图和图像定位功能，并加入了日志和重试机制。
    """
    def __init__(self):
        # 确保截图目录存在
        os.makedirs(settings.SCREENSHOT_DIR, exist_ok=True)
        logger.debug(f"✨ autowin 屏幕截图模块初始化，截图将保存到: {settings.SCREENSHOT_DIR}")

    @retry(exceptions=AutoWinError)
    def take_screenshot(self, filename: Optional[str] = None, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        截取全屏或指定区域的屏幕截图。

        :param filename: 截图保存的文件名（包含扩展名，如 "screenshot.png"）。如果为 None，则自动生成文件名。
        :param region: 截图区域的左上角 x, y 坐标，以及宽度和高度 (x, y, width, height)。
        :return: 截图文件的完整路径。
        :raises AutoWinError: 如果截图失败。
        """
        try:
            if filename is None:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join(settings.SCREENSHOT_DIR, filename)

            if region:
                logger.debug(f"📸 截取屏幕指定区域: {region} 到文件: {filepath}")
                screenshot = pyautogui.screenshot(region=region)
            else:
                logger.debug(f"📸 截取全屏到文件: {filepath}")
                screenshot = pyautogui.screenshot()
            
            screenshot.save(filepath)
            logger.info(f"✅ 屏幕截图成功保存到: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"❌ 屏幕截图失败: {e}")
            raise AutoWinError(f"屏幕截图失败: {e}")

    @retry(exceptions=ImageNotFoundError)
    def locate_on_screen(self, image_path: str, confidence: float = settings.SCREENSHOT_CONFIDENCE,
                         region: Optional[Tuple[int, int, int, int]] = None, grayscale: bool = False) -> Optional[Tuple[int, int, int, int]]:
        """
        在屏幕上查找图像的位置。

        :param image_path: 要查找的图像文件的路径。
        :param confidence: 匹配的置信度（0.0到1.0）。
        :param region: 查找图像的屏幕区域 (x, y, width, height)。
        :param grayscale: 是否将图像转换为灰度进行查找，可以提高速度但可能降低准确性。
        :return: 图像在屏幕上的 (左上角x, 左上角y, 宽度, 高度) 坐标元组，如果未找到则为 None。
        :raises ImageNotFoundError: 如果在超时时间内未找到图像。
        """
        if not os.path.exists(image_path):
            logger.error(f"❌ 图像文件不存在: {image_path}")
            raise FileNotFoundError(f"图像文件不存在: {image_path}")

        logger.debug(f"🔍 在屏幕上查找图像: {image_path}, 置信度: {confidence}, 区域: {region}, 灰度: {grayscale}")
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region, grayscale=grayscale)
            if location:
                logger.info(f"✅ 成功找到图像 '{image_path}' 在屏幕上的位置: {location}")
                return location
            else:
                logger.warning(f"⚠️ 未在屏幕上找到图像: {image_path}")
                raise ImageNotFoundError(
                    message=f"未在屏幕上找到图像: {image_path}",
                    image_path=image_path,
                    confidence=confidence
                )
        except pyautogui.PyAutoGUIException as e:
            logger.error(f"❌ 图像查找失败 (pyautogui 错误): {e}")
            raise ImageNotFoundError(f"图像查找失败: {e}")
        except Exception as e:
            logger.error(f"❌ 图像查找失败: {e}")
            raise ImageNotFoundError(f"图像查找失败: {e}")

    @retry(exceptions=ImageNotFoundError)
    def click_image(self, image_path: str, button: str = 'left', clicks: int = 1, interval: float = 0.0,
                    confidence: float = settings.SCREENSHOT_CONFIDENCE, region: Optional[Tuple[int, int, int, int]] = None,
                    grayscale: bool = False, duration: float = 0.0) -> None:
        """
        在屏幕上找到图像并点击其中心。

        :param image_path: 要查找并点击的图像文件的路径。
        :param button: 鼠标按钮，可选 'left', 'middle', 'right'。
        :param clicks: 点击次数。
        :param interval: 每次点击之间的间隔秒数。
        :param confidence: 图像匹配的置信度（0.0到1.0）。
        :param region: 查找图像的屏幕区域 (x, y, width, height)。
        :param grayscale: 是否将图像转换为灰度进行查找。
        :param duration: 鼠标移动到目标位置的持续时间（秒）。
        :raises ImageNotFoundError: 如果未在屏幕上找到图像。
        :raises AutoWinError: 如果点击操作失败。
        """
        logger.debug(f"🖱️ 尝试点击图像: {image_path}")
        location = self.locate_on_screen(image_path, confidence=confidence, region=region, grayscale=grayscale)
        if location:
            # 计算图像中心的坐标
            center_x = location[0] + location[2] // 2
            center_y = location[1] + location[3] // 2
            
            try:
                pyautogui.click(x=center_x, y=center_y, button=button, clicks=clicks, interval=interval, duration=duration)
                logger.info(f"✅ 成功点击图像 '{image_path}' 的中心 ({center_x}, {center_y})")
            except Exception as e:
                logger.error(f"❌ 点击图像 '{image_path}' 失败: {e}")
                raise AutoWinError(f"点击图像 '{image_path}' 失败: {e}")
        else:
            # locate_on_screen 已经抛出 ImageNotFoundError，这里只是为了明确流程
            pass

# 提供一个屏幕截图模块的实例
screenshot = AutoWinScreenshot()